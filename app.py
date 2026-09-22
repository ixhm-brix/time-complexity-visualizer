import base64
import io
import math
import os
import random
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, jsonify, request

app = Flask(__name__)

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

MAX_OPS = 20_000_000
MAX_N = 1_000_000


class Stack:
    """LIFO collection backed by a Python list."""

    def __init__(self, values=()):
        self._items = list(values)

    def push(self, value):
        self._items.append(value)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def to_list(self):
        return list(self._items)


class Queue:
    """FIFO collection backed by a list and a moving front index."""

    def __init__(self, values=()):
        self._items = list(values)
        self._front = 0

    def enqueue(self, value):
        self._items.append(value)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        value = self._items[self._front]
        self._front += 1
        if self._front == len(self._items):
            self._items = []
            self._front = 0
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._items[self._front]

    def is_empty(self):
        return self._front == len(self._items)

    def __len__(self):
        return len(self._items) - self._front

    def to_list(self):
        return list(self._items[self._front:])


def stack_push_pop(n):
    stack = Stack()
    ops = 0
    for value in range(n):
        stack.push(value)
        ops += 1
    while not stack.is_empty():
        stack.pop()
        ops += 1
    return ops


def stack_search(data, target):
    ops = 0
    while not data.is_empty():
        ops += 1
        if data.pop() == target:
            break
    return ops


def stack_reverse(data):
    values = []
    ops = 0
    while not data.is_empty():
        values.append(data.pop())
        ops += 1
    for value in values:
        data.push(value)
        ops += 1
    return ops


def queue_enqueue_dequeue(n):
    queue = Queue()
    ops = 0
    for value in range(n):
        queue.enqueue(value)
        ops += 1
    while not queue.is_empty():
        queue.dequeue()
        ops += 1
    return ops


def queue_search(data, target):
    ops = 0
    remaining = len(data)
    while remaining:
        value = data.dequeue()
        ops += 1
        remaining -= 1
        if value == target:
            break
    return ops


def queue_reverse(data):
    values = []
    ops = 0
    while not data.is_empty():
        values.append(data.dequeue())
        ops += 1
    for value in reversed(values):
        data.enqueue(value)
        ops += 1
    return ops


def linear_search(data, target):
    ops = 0
    for value in data:
        ops += 1
        if value == target:
            break
    return ops


def binary_search(data, target):
    ops = 0
    low, high = 0, len(data) - 1
    while low <= high:
        ops += 1
        mid = (low + high) // 2
        if data[mid] == target:
            break
        if data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return ops


def jump_search(data, target):
    n = len(data)
    if n == 0:
        return 0
    ops = 0
    stride = max(1, int(math.sqrt(n)))
    prev = cur = 0
    while cur < n:
        ops += 1
        if data[cur] >= target:
            break
        prev, cur = cur, cur + stride
    for i in range(prev, min(cur + 1, n)):
        ops += 1
        if data[i] == target:
            break
    return ops


def bubble_sort(data):
    ops = 0
    n = len(data)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            ops += 1
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                ops += 1
                swapped = True
        if not swapped:
            break
    return ops


def selection_sort(data):
    ops = 0
    n = len(data)
    for i in range(n - 1):
        lowest = i
        for j in range(i + 1, n):
            ops += 1
            if data[j] < data[lowest]:
                lowest = j
        if lowest != i:
            data[i], data[lowest] = data[lowest], data[i]
            ops += 1
    return ops


def insertion_sort(data):
    ops = 0
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0:
            ops += 1
            if data[j] <= key:
                break
            data[j + 1] = data[j]
            ops += 1
            j -= 1
        data[j + 1] = key
    return ops


def merge_sort(data):
    ops = 0

    def sort(chunk):
        nonlocal ops
        if len(chunk) <= 1:
            return chunk
        mid = len(chunk) // 2
        left, right = sort(chunk[:mid]), sort(chunk[mid:])
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            ops += 1
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        ops += len(left) - i + len(right) - j
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    sort(data)
    return ops


def quick_sort(data):
    ops = 0
    stack = [(0, len(data) - 1)]
    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        pivot = data[high]
        i = low - 1
        for j in range(low, high):
            ops += 1
            if data[j] <= pivot:
                i += 1
                data[i], data[j] = data[j], data[i]
                ops += 1
        data[i + 1], data[high] = data[high], data[i + 1]
        ops += 1
        stack.append((low, i))
        stack.append((i + 2, high))
    return ops


def heap_sort(data):
    ops = 0
    n = len(data)

    def sift_down(root, end):
        nonlocal ops
        while True:
            child = 2 * root + 1
            if child >= end:
                return
            if child + 1 < end:
                ops += 1
                if data[child] < data[child + 1]:
                    child += 1
            ops += 1
            if data[root] >= data[child]:
                return
            data[root], data[child] = data[child], data[root]
            ops += 1
            root = child

    for start in range(n // 2 - 1, -1, -1):
        sift_down(start, n)
    for end in range(n - 1, 0, -1):
        data[0], data[end] = data[end], data[0]
        ops += 1
        sift_down(0, end)
    return ops


def counting_sort(data):
    if not data:
        return 0
    ops = len(data)
    counts = [0] * (max(data) + 1)
    for value in data:
        counts[value] += 1
        ops += 1
    index = 0
    for value, repeat in enumerate(counts):
        ops += 1
        for _ in range(repeat):
            data[index] = value
            index += 1
            ops += 1
    return ops


def nested_loops(n):
    ops = 0
    for _i in range(n):
        for _j in range(n):
            ops += 1
    return ops


def triangular_loops(n):
    ops = 0
    for i in range(n):
        for _j in range(i, n):
            ops += 1
    return ops


def triple_nested_loops(n):
    ops = 0
    for _i in range(n):
        for _j in range(n):
            for _k in range(n):
                ops += 1
    return ops


def matrix_multiply(n):
    ops = 0
    a = [list(range(n)) for _ in range(n)]
    b = [list(range(n)) for _ in range(n)]
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += a[i][k] * b[k][j]
                ops += 1
            result[i][j] = total
    return ops


def constant_time(n):
    ops = 0
    ops += 1
    _ = n * 2 + 1
    ops += 1
    _ = n // 2
    ops += 1
    return ops


def binary_exponentiation(n):
    ops = 0
    base, exponent, result = 2, n, 1
    while exponent > 0:
        ops += 1
        if exponent & 1:
            result = result * base % 1000003
            ops += 1
        base = base * base % 1000003
        exponent >>= 1
    return max(ops, 1)


def fibonacci_recursive(n):
    calls = [0]

    def fib(k):
        calls[0] += 1
        if k < 2:
            return k
        return fib(k - 1) + fib(k - 2)

    fib(n)
    return calls[0]


def _sorted(n):
    return list(range(n))


def _reversed(n):
    return list(range(n, 0, -1))


def _shuffled(n):
    data = list(range(n))
    random.Random(42).shuffle(data)
    return data


def _stack(n):
    return Stack(range(n))


def _queue(n):
    return Queue(range(n))


ALGORITHMS = {
    "stack_push_pop": {
        "run": stack_push_pop,
        "complexity": "O(n)", "unit": "pushes + pops", "max_n": None},
    "stack_search": {
        "run": lambda n: stack_search(_stack(n), -1),
        "complexity": "O(n)", "unit": "pops + comparisons", "max_n": None},
    "stack_reverse": {
        "run": lambda n: stack_reverse(_stack(n)),
        "complexity": "O(n)", "unit": "pops + pushes", "max_n": None},
    "queue_enqueue_dequeue": {
        "run": queue_enqueue_dequeue,
        "complexity": "O(n)", "unit": "enqueues + dequeues", "max_n": None},
    "queue_search": {
        "run": lambda n: queue_search(_queue(n), -1),
        "complexity": "O(n)", "unit": "dequeues + comparisons", "max_n": None},
    "queue_reverse": {
        "run": lambda n: queue_reverse(_queue(n)),
        "complexity": "O(n)", "unit": "dequeues + enqueues", "max_n": None},
    "linear_search": {
        "run": lambda n: linear_search(_sorted(n), -1),
        "complexity": "O(n)", "unit": "comparisons", "max_n": None},
    "binary_search": {
        "run": lambda n: binary_search(_sorted(n), -1),
        "complexity": "O(log n)", "unit": "comparisons", "max_n": None},
    "jump_search": {
        "run": lambda n: jump_search(_sorted(n), n),
        "complexity": "O(sqrt n)", "unit": "comparisons", "max_n": None},
    "bubble_sort": {
        "run": lambda n: bubble_sort(_reversed(n)),
        "complexity": "O(n^2)", "unit": "comparisons + swaps", "max_n": None},
    "selection_sort": {
        "run": lambda n: selection_sort(_reversed(n)),
        "complexity": "O(n^2)", "unit": "comparisons + swaps", "max_n": None},
    "insertion_sort": {
        "run": lambda n: insertion_sort(_reversed(n)),
        "complexity": "O(n^2)", "unit": "comparisons + shifts", "max_n": None},
    "merge_sort": {
        "run": lambda n: merge_sort(_shuffled(n)),
        "complexity": "O(n log n)", "unit": "comparisons + merges", "max_n": None},
    "quick_sort": {
        "run": lambda n: quick_sort(_sorted(n)),
        "complexity": "O(n^2)", "unit": "comparisons + swaps", "max_n": None},
    "heap_sort": {
        "run": lambda n: heap_sort(_shuffled(n)),
        "complexity": "O(n log n)", "unit": "comparisons + swaps", "max_n": None},
    "counting_sort": {
        "run": lambda n: counting_sort(_shuffled(n)),
        "complexity": "O(n + k)", "unit": "tallies + writes", "max_n": None},
    "nested_loops": {
        "run": nested_loops,
        "complexity": "O(n^2)", "unit": "inner-loop steps", "max_n": None},
    "triangular_loops": {
        "run": triangular_loops,
        "complexity": "O(n^2)", "unit": "inner-loop steps", "max_n": None},
    "triple_nested_loops": {
        "run": triple_nested_loops,
        "complexity": "O(n^3)", "unit": "inner-loop steps", "max_n": 600},
    "matrix_multiply": {
        "run": matrix_multiply,
        "complexity": "O(n^3)", "unit": "multiply-adds", "max_n": 260},
    "constant_time": {
        "run": constant_time,
        "complexity": "O(1)", "unit": "operations", "max_n": None},
    "binary_exponentiation": {
        "run": binary_exponentiation,
        "complexity": "O(log n)", "unit": "multiplications", "max_n": None},
    "fibonacci_recursive": {
        "run": fibonacci_recursive,
        "complexity": "O(2^n)", "unit": "function calls", "max_n": 28},
}


def read_int(name, default, minimum, maximum):
    raw = request.args.get(name)
    if raw is None or not raw.strip():
        return default, None
    text = raw.strip().strip("\"'").replace(",", "").replace("_", "").strip()
    if not re.fullmatch(r"\d+", text):
        return None, "%s must be a whole number, got %r" % (name, raw)
    value = int(text)
    if value < minimum or value > maximum:
        return None, "%s must be between %d and %d, got %d" % (
            name, minimum, maximum, value)
    return value, None


def measure(algo, step, n_max):
    spec = ALGORITHMS[algo]
    run = spec["run"]

    sizes = list(range(0, n_max + 1, step))
    if sizes[-1] != n_max:
        sizes.append(n_max)

    points = []
    total = 0
    last_n = last_ops = 0

    for n in sizes:
        if spec["max_n"] is not None and n > spec["max_n"]:
            break
        if last_n:
            estimate = last_ops * (n / last_n) ** 2
            if total + estimate > MAX_OPS:
                break
        ops = run(n)
        points.append({"n": n, "operations": ops})
        total += ops
        last_n, last_ops = n, ops
        if total >= MAX_OPS:
            break

    return points, total


def plot(algo, points, n_max, path):
    spec = ALGORITHMS[algo]
    xs = [p["n"] for p in points]
    ys = [p["operations"] for p in points]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=110)
    ax.plot(xs, ys, color="#2a78d6", linewidth=2,
            marker="o" if len(xs) <= 30 else None, markersize=4)

    ax.set_title("%s  -  %s" % (algo.replace("_", " ").title(), spec["complexity"]),
                 fontsize=15, fontweight="bold", loc="left", pad=14)
    ax.set_xlabel("input size (n)", fontsize=11)
    ax.set_ylabel(spec["unit"], fontsize=11)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(bottom=0)

    if xs and xs[-1] < n_max:
        ax.set_xlabel("input size (n)   -   measured up to n = %s of %s"
                      % (format(xs[-1], ","), format(n_max, ",")), fontsize=11)

    fig.tight_layout()
    fig.savefig(path)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    return buffer.getvalue()


@app.route("/analyze")
def analyze():
    algo = (request.args.get("algo") or "").strip().strip("\"'")
    if algo not in ALGORITHMS:
        return jsonify({
            "error": "unknown algo %r" % algo,
            "supported": sorted(ALGORITHMS),
        }), 400

    n_max, error = read_int("n_max", 1000, 0, MAX_N)
    if error:
        return jsonify({"error": error}), 400
    step, error = read_int("step", 10, 1, max(n_max, 1))
    if error:
        return jsonify({"error": error}), 400

    points, total = measure(algo, step, n_max)

    filename = "%s_step%d_n%d.png" % (algo, step, n_max)
    os.makedirs(PLOT_DIR, exist_ok=True)
    path = os.path.join(PLOT_DIR, filename)
    png = plot(algo, points, n_max, path)

    return jsonify({
        "algo": algo,
        "complexity": ALGORITHMS[algo]["complexity"],
        "unit": ALGORITHMS[algo]["unit"],
        "n_min": 0,
        "n_max": n_max,
        "step": step,
        "points_measured": len(points),
        "measured_up_to_n": points[-1]["n"] if points else 0,
        "operations_at_largest_n": points[-1]["operations"] if points else 0,
        "total_operations_executed": total,
        "data": points,
        "image_file": path,
        "image_base64": base64.b64encode(png).decode("ascii"),
    })


@app.route("/")
def index():
    return jsonify({
        "service": "Time Complexity Visualizer",
        "usage": "/analyze?algo=linear_search&step=10&n_max=10000",
        "algorithms": sorted(ALGORITHMS),
    })


if __name__ == "__main__":
    print("\n  http://localhost:8000/analyze?algo=linear_search&step=10&n_max=10000\n")
    app.run(host="127.0.0.1", port=8000, debug=False)
