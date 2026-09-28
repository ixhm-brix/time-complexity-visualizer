"""Algorithms available to the visualizer.

Each function takes an input size ``n`` and performs one full run of the
algorithm on an input of that size. Searches look for a value that is never
present so every run hits the worst case.
"""
import random

from data_structures import Queue, Stack


def _random_list(n):
    return [random.randint(0, n) for _ in range(n)]


def linear_search(n):
    """O(n): scan every element looking for a missing value."""
    data = _random_list(n)
    target = -1
    for value in data:
        if value == target:
            return True
    return False


def binary_search(n):
    """O(log n): halve a sorted range until it is empty."""
    data = list(range(n))
    target = -1
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return True
        if data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return False


def bubble_sort(n):
    """O(n^2): repeatedly swap adjacent out-of-order pairs."""
    data = _random_list(n)
    for i in range(len(data)):
        for j in range(len(data) - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data


def nested_loops(n):
    """O(n^2): a baseline with no data-dependent branching."""
    total = 0
    for _ in range(n):
        for _ in range(n):
            total += 1
    return total


def insertion_sort(n):
    """O(n^2): grow a sorted prefix by inserting one element at a time."""
    data = _random_list(n)
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    return data


def selection_sort(n):
    """O(n^2): repeatedly move the smallest remaining element into place."""
    data = _random_list(n)
    for i in range(len(data)):
        smallest = i
        for j in range(i + 1, len(data)):
            if data[j] < data[smallest]:
                smallest = j
        data[i], data[smallest] = data[smallest], data[i]
    return data


def stack_push_pop(n):
    """O(n): n pushes then n pops, each O(1)."""
    stack = Stack()
    for i in range(n):
        stack.push(i)
    while not stack.is_empty():
        stack.pop()
    return True


def queue_enqueue_dequeue(n):
    """O(n^2): n enqueues (O(1)) then n dequeues (O(n) each)."""
    queue = Queue()
    for i in range(n):
        queue.enqueue(i)
    while not queue.is_empty():
        queue.dequeue()
    return True


def stack_based_reversal(n):
    """O(n): push every element, then pop them back out in reverse."""
    stack = Stack()
    for value in _random_list(n):
        stack.push(value)
    reversed_data = []
    while not stack.is_empty():
        reversed_data.append(stack.pop())
    return reversed_data


def queue_based_rotation(n):
    """O(n^2): move the front element to the back n times."""
    data = _random_list(n)
    queue = Queue()
    for value in data:
        queue.enqueue(value)
    for _ in range(len(data)):
        queue.enqueue(queue.dequeue())
    return True


ALGORITHMS = {
    "linear_search": linear_search,
    "binary_search": binary_search,
    "bubble_sort": bubble_sort,
    "nested_loops": nested_loops,
    "insertion_sort": insertion_sort,
    "selection_sort": selection_sort,
    "stack_push_pop": stack_push_pop,
    "queue_enqueue_dequeue": queue_enqueue_dequeue,
    "stack_based_reversal": stack_based_reversal,
    "queue_based_rotation": queue_based_rotation,
}
