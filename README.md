# Time Complexity Visualizer

A local Flask API that measures how an algorithm's running time grows with
input size. It plots the measurements with matplotlib and returns the raw
timings together with the chart as a base64-encoded PNG.

## How it works

For a request such as `algo=linear_search&step=10&n_max=100`, the server:

1. Builds the input sizes `0, 10, 20, ..., 100`. `n_min` is always `0`, and
   `n_max` is included only when it falls on a step boundary.
2. Runs the algorithm once for each input size and times each run with
   `time.time()`.
3. Plots input size (x-axis) against running time in seconds (y-axis). It
   uses matplotlib's headless `Agg` backend, so no display is needed.
4. Saves the chart to `snapshots/` and also encodes it as base64.
5. Returns the input sizes, the timings and the image in one JSON response.

## Project layout

| File | Purpose |
|---|---|
| `server.py` | The Flask app. Defines `/analyze`, `/register`, `/login`, `/save_analysis`, `/analyses/<id>` and `/algorithms`, checks parameters and JWTs, saves snapshots and builds the JSON response. |
| `database.py` | SQLAlchemy engine, session factory and the `Analysis` and `User` models. Stores data in `analyses.db` (SQLite). |
| `algorithms.py` | The algorithms you can time, registered in the `ALGORITHMS` dict. |
| `Algorithm.py` | `time_complexity_visualizer(...)`. Times an algorithm over a range of input sizes and returns a matplotlib figure with the timings. |
| `data_structures.py` | The `Stack` and `Queue` classes. |
| `data_structures_test.py` | `unittest` suite for `Stack` and `Queue`. |
| `snapshots/` | Created on the first run. Holds one timestamped PNG per `/analyze` request. |

## Setup

You need Python 3.10 or later.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

## Running the server

```bash
python server.py
```

The server listens on `http://localhost:8000` in debug mode and reloads when
you edit a file. Press `Ctrl+C` to stop it.

## API

### `GET /analyze`

| Parameter | Required | Notes |
|---|---|---|
| `algo` | Yes | One of the [supported algorithms](#supported-algorithms). Case-insensitive. Surrounding quotes are removed, so `'linear_search'` also works. |
| `step` | Yes | A positive integer: the gap between input sizes. |
| `n_max` | Yes | A positive integer: the largest input size. Commas are allowed, for example `10,000`. |

Example:

```bash
curl "http://localhost:8000/analyze?algo=linear_search&step=10&n_max=100"
```

```json
{
  "algo": "linear_search",
  "step": 10,
  "n_min": 0,
  "n_max": 100,
  "input_sizes": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
  "times": [2.1e-06, 5.0e-06, "..."],
  "snapshot_path": "/.../snapshots/linear_search_20260928_104834.png",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgA..."
}
```

`image_base64` is a plain base64 PNG. You can decode it and write the bytes
to a `.png` file, or prefix it with `data:image/png;base64,` to display it in
an `<img>` tag.

Invalid requests get `400 Bad Request`:

| Condition | Body |
|---|---|
| `algo` missing | `{"error": "Missing required query parameter: algo"}` |
| `algo` unknown | `{"error": "Unknown algorithm '<value>'", "supported_algorithms": [...]}` |
| `step` missing, not a number, or ≤ 0 | `{"error": "Query parameter 'step' must be a positive integer"}` |
| `n_max` missing | `{"error": "Missing required query parameter: n_max"}` |
| `n_max` not a number | `{"error": "Query parameter 'n_max' must be an integer"}` |
| `n_max` ≤ 0 | `{"error": "Query parameter 'n_max' must be greater than 0"}` |

### `POST /register` and `POST /login`

`/save_analysis` requires a JWT, so you first create an account and log in.
Both endpoints take a JSON body with `username` and `password`.

```bash
curl -X POST http://localhost:8000/register \
     -H "Content-Type: application/json" \
     -d '{"username": "faber", "password": "secret"}'

curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username": "faber", "password": "secret"}'
# {"access_token": "eyJhbGciOi..."}
```

| Endpoint | Result |
|---|---|
| `/register` | `201` with the new user's `id`. `409` if the username is taken. `400` if either field is missing. |
| `/login` | `200` with `access_token`. `401` if the username or password is wrong. |

Passwords are stored as salted hashes, never as plain text. Tokens expire
after one hour.

### `POST /save_analysis`

Runs the same analysis as `/analyze` and stores the result in the database.
It accepts the same `algo`, `step` and `n_max` parameters, either as a JSON
body or in the query string, and applies the same validation. On success it
returns `201 Created` with the saved record, including its new `id` and
`created_at`.

The request must send the token from `/login` in the `Authorization` header
as a Bearer token. A token in the query string or the body is ignored.

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username": "faber", "password": "secret"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8000/save_analysis \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"algo": "bubble_sort", "step": 100, "n_max": 1000}'
```

Without a valid token the endpoint returns `401 Unauthorized` and saves
nothing:

| Condition | Body |
|---|---|
| No `Authorization` header, or no `Bearer` prefix | `{"error": "I don't know you", "detail": "..."}` |
| Malformed token or bad signature | `{"error": "I don't know you", "detail": "..."}` |
| Token for a user that no longer exists | `{"error": "I don't know you", "detail": "User no longer exists"}` |
| Expired token | `{"error": "Bye", "detail": "Token has expired"}` |

Tokens are signed with the `JWT_SECRET_KEY` environment variable. Without
it, the server falls back to a built-in development key, which anyone
reading this code could use to forge tokens. Set your own key before the
server is reachable by anyone else:

```bash
export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Records live in the `analyses` table of `analyses.db` in the project folder,
and accounts live in the `users` table. Both tables are created
automatically when the server starts. To use a
different database, set the `DATABASE_URL` environment variable to any
SQLAlchemy URL, for example `postgresql://user:pass@localhost/dsa`.

### `GET /analyses/<id>`

Returns a saved analysis by `id`, or `404` if no record has that `id`.

### `GET /algorithms`

Returns the accepted `algo` values in alphabetical order:

```json
{"supported_algorithms": ["binary_search", "bubble_sort", "insertion_sort", "..."]}
```

## Supported algorithms

Each algorithm is a function `f(n)` in `algorithms.py` that does one full run
on an input of size `n`. Both searches look for a value that is not in the
list, so every run is the worst case.

| `algo` | What it does | Expected complexity |
|---|---|---|
| `linear_search` | Scans `n` random integers for a missing value. | O(n) |
| `binary_search` | Binary search over `0..n-1` for a missing value. | O(log n) |
| `bubble_sort` | Bubble sort on `n` random integers. | O(n²) |
| `nested_loops` | Two nested loops of `n` that only increment a counter. A plain O(n²) baseline. | O(n²) |
| `insertion_sort` | Insertion sort on `n` random integers. | O(n²) |
| `selection_sort` | Selection sort on `n` random integers. | O(n²) |
| `stack_push_pop` | Pushes `n` items onto a `Stack`, then pops them all. | O(n) |
| `queue_enqueue_dequeue` | Enqueues `n` items onto a `Queue`, then dequeues them all. | O(n²) |
| `stack_based_reversal` | Reverses `n` random integers by pushing them onto a `Stack` and popping them off. | O(n) |
| `queue_based_rotation` | Moves the front of a `Queue` of `n` items to the back, `n` times. | O(n²) |

The stack and queue entries come in pairs so you can compare them. Stack
operations are O(1), so the stack runs grow linearly. `Queue.dequeue()` uses
`list.pop(0)`, which is O(n), so the queue runs grow quadratically and the
two curves pull apart as `n` gets bigger.

## Stack and Queue

`data_structures.py` defines two list-backed classes:

- `Stack` (last in, first out): `push`, `pop`, `peek`, `is_empty`, `len()`.
- `Queue` (first in, first out): `enqueue`, `dequeue`, `front`, `is_empty`,
  `len()`.

Calling `pop`, `peek`, `dequeue` or `front` on an empty structure raises
`IndexError`.

Run the 20 tests:

```bash
python -m unittest data_structures_test.py -v
```

## Adding an algorithm

1. Add a function `def my_algorithm(n): ...` to `algorithms.py` that does one
   full run for input size `n`.
2. Add it to the `ALGORITHMS` dict: `"my_algorithm": my_algorithm`.

`server.py` and `Algorithm.py` read `ALGORITHMS` directly, so neither needs
to change.

## Known limitations

- Each input size is timed once with no averaging, so small inputs or a busy
  machine can produce noisy curves. A larger `step` and `n_max` give steadier
  results.
- O(n²) algorithms with a large `n_max` can take a long time, because the
  request does not return until every run has finished.
- The server runs with `debug=True`. That is fine on `localhost` but should
  not be exposed to a network.
