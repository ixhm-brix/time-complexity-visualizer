import base64
import io
import os
from datetime import datetime

import matplotlib.pyplot as plt
from flask import Flask, jsonify, request

from Algorithm import time_complexity_visualizer
from algorithms import ALGORITHMS
from database import Analysis, SessionLocal, init_db

app = Flask(__name__)

SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)
init_db()


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
def save_analysis():
    """Run an analysis and store the result in the database.

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
