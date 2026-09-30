import base64
import io
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from sqlalchemy import select

from Algorithm import time_complexity_visualizer
from algorithms import ALGORITHMS
from database import Analysis, SessionLocal, User, init_db

app = Flask(__name__)
# Set JWT_SECRET_KEY in the environment for anything beyond local development.
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-only-secret-change-me-in-production-0123456789"
)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Authorization: Bearer <token>
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)
init_db()


# Every JWT failure is a 401. Flask-JWT-Extended would otherwise answer a
# malformed token with 422.
@jwt.unauthorized_loader
def missing_token(reason):
    return jsonify(error="I don't know you", detail=reason), 401


@jwt.invalid_token_loader
def invalid_token(reason):
    return jsonify(error="I don't know you", detail=reason), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify(error="Bye", detail="Token has expired"), 401


@jwt.user_lookup_loader
def load_user(jwt_header, jwt_payload):
    with SessionLocal() as session:
        return session.get(User, int(jwt_payload["sub"]))


@jwt.user_lookup_error_loader
def unknown_user(jwt_header, jwt_payload):
    return jsonify(error="I don't know you", detail="User no longer exists"), 401


def read_credentials():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    password = body.get("password")
    if not isinstance(username, str) or not username.strip():
        raise ValidationError("'username' is required")
    if not isinstance(password, str) or not password:
        raise ValidationError("'password' is required")
    return username.strip(), password


@app.route("/register", methods=["POST"])
def register():
    username, password = read_credentials()
    with SessionLocal.begin() as session:
        taken = session.scalar(select(User).where(User.username == username))
        if taken:
            return jsonify(error=f"Username '{username}' is already taken"), 409
        user = User(username=username)
        user.set_password(password)
        session.add(user)
    return jsonify(id=user.id, username=user.username), 201


@app.route("/login", methods=["POST"])
def login():
    username, password = read_credentials()
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.username == username))
    if user is None or not user.check_password(password):
        return jsonify(error="Invalid username or password"), 401
    return jsonify(access_token=create_access_token(identity=str(user.id)))


class ValidationError(Exception):
    def __init__(self, message, **extra):
        super().__init__(message)
        self.body = {"error": message, **extra}


@app.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(err.body), 400


def parse_params(source):
    """Validate algo/step/n_max from a query string or JSON body."""
    algo_name = source.get("algo")
    step_raw = source.get("step")
    n_max_raw = source.get("n_max")

    if not algo_name:
        raise ValidationError("Missing required query parameter: algo")
    # Accept algo=linear_search, algo='linear_search' and algo="Linear_Search".
    algo_name = str(algo_name).strip().strip("'\"").lower()
    if algo_name not in ALGORITHMS:
        raise ValidationError(
            f"Unknown algorithm '{algo_name}'",
            supported_algorithms=sorted(ALGORITHMS),
        )

    try:
        step = int(step_raw)
    except (TypeError, ValueError):
        step = None
    if step is None or step <= 0:
        raise ValidationError("Query parameter 'step' must be a positive integer")

    if n_max_raw is None:
        raise ValidationError("Missing required query parameter: n_max")
    try:
        n_max = int(str(n_max_raw).replace(",", ""))  # allow 10,000
    except ValueError:
        raise ValidationError("Query parameter 'n_max' must be an integer")
    if n_max <= 0:
        raise ValidationError("Query parameter 'n_max' must be greater than 0")

    return algo_name, step, n_max


def run_analysis(algo_name, step, n_max):
    """Time the algorithm, save a snapshot PNG and return the result dict."""
    fig, input_sizes, times = time_complexity_visualizer(
        ALGORITHMS[algo_name], n_min=0, n_max=n_max, n_step=step, algo_name=algo_name
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"{algo_name}_{timestamp}.png")
    try:
        fig.savefig(snapshot_path, format="png")
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
    finally:
        plt.close(fig)

    return {
        "algo": algo_name,
        "step": step,
        "n_min": 0,
        "n_max": n_max,
        "input_sizes": input_sizes,
        "times": times,
        "snapshot_path": snapshot_path,
        "image_base64": base64.b64encode(buffer.getvalue()).decode("ascii"),
    }


@app.route("/analyze", methods=["GET"])
def analyze():
    return jsonify(run_analysis(*parse_params(request.args)))


@app.route("/save_analysis", methods=["POST"])
@jwt_required()
def save_analysis():
    """Run an analysis and store the result in the database.

    Requires an "Authorization: Bearer <token>" header from /login.
    Parameters come from a JSON body, falling back to the query string.
    """
    params = request.get_json(silent=True) or request.args
    result = run_analysis(*parse_params(params))

    with SessionLocal.begin() as session:
        analysis = Analysis(**result)
        session.add(analysis)

    return jsonify(analysis.to_dict()), 201


@app.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    with SessionLocal() as session:
        analysis = session.get(Analysis, analysis_id)
    if analysis is None:
        return jsonify(error=f"No analysis with id {analysis_id}"), 404
    return jsonify(analysis.to_dict())


@app.route("/algorithms", methods=["GET"])
def list_algorithms():
    return jsonify(supported_algorithms=sorted(ALGORITHMS))


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
