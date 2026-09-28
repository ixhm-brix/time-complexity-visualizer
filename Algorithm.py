"""Times an algorithm across a range of input sizes and plots the result."""
import time

import matplotlib

matplotlib.use("Agg")  # headless backend: the server has no display
import matplotlib.pyplot as plt


def time_complexity_visualizer(algorithm, n_min, n_max, n_step, algo_name=""):
    """Run ``algorithm(n)`` once for each n in n_min, n_min+n_step, ..., n_max.

    Returns ``(fig, input_sizes, times)``: the matplotlib figure, the input
    sizes used, and the wall-clock seconds each run took. The caller owns the
    figure and should close it with ``plt.close(fig)`` when done.
    """
    input_sizes = list(range(n_min, n_max + 1, n_step))
    times = []

    for n in input_sizes:
        start = time.time()
        algorithm(n)
        times.append(time.time() - start)

    fig, ax = plt.subplots()
    title = "Algorithm time complexity visualisation"
    if algo_name:
        title += f" - {algo_name}"
    ax.set_title(title)
    ax.set_xlabel("Input size")
    ax.set_ylabel("Running time (seconds)")
    ax.plot(input_sizes, times, "o-")

    return fig, input_sizes, times
