import base64

import pytest

import app


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    return app.app.test_client()


def test_stack_is_lifo_and_reports_state():
    stack = app.Stack()
    assert stack.is_empty()
    assert len(stack) == 0

    stack.push("first")
    stack.push("second")
    assert not stack.is_empty()
    assert len(stack) == 2
    assert stack.peek() == "second"
    assert stack.to_list() == ["first", "second"]
    assert stack.pop() == "second"
    assert stack.pop() == "first"
    assert stack.is_empty()


def test_stack_can_start_with_values_and_rejects_empty_reads():
    stack = app.Stack([1, 2, 3])
    assert stack.to_list() == [1, 2, 3]

    with pytest.raises(IndexError, match="empty stack"):
        app.Stack().pop()
    with pytest.raises(IndexError, match="empty stack"):
        app.Stack().peek()


def test_queue_is_fifo_and_reports_state():
    queue = app.Queue()
    assert queue.is_empty()
    assert len(queue) == 0

    queue.enqueue("first")
    queue.enqueue("second")
    assert not queue.is_empty()
    assert len(queue) == 2
    assert queue.peek() == "first"
    assert queue.to_list() == ["first", "second"]
    assert queue.dequeue() == "first"
    assert queue.dequeue() == "second"
    assert queue.is_empty()


def test_queue_reuses_storage_after_becoming_empty():
    queue = app.Queue([1, 2])
    assert queue.dequeue() == 1
    queue.enqueue(3)
    assert queue.to_list() == [2, 3]
    assert queue.dequeue() == 2
    assert queue.dequeue() == 3

    with pytest.raises(IndexError, match="empty queue"):
        queue.dequeue()
    with pytest.raises(IndexError, match="empty queue"):
        queue.peek()


def test_stack_algorithms():
    stack = app.Stack([1, 2, 3])
    assert app.stack_search(stack, 2) == 2
    assert stack.to_list() == [1]

    stack = app.Stack([1, 2, 3])
    assert app.stack_reverse(stack) == 6
    assert stack.to_list() == [3, 2, 1]
    assert app.stack_push_pop(3) == 6


def test_queue_algorithms():
    queue = app.Queue([1, 2, 3])
    assert app.queue_search(queue, 2) == 2
    assert queue.to_list() == [3]

    queue = app.Queue([1, 2, 3])
    assert app.queue_reverse(queue) == 6
    assert queue.to_list() == [3, 2, 1]
    assert app.queue_enqueue_dequeue(3) == 6


@pytest.mark.parametrize("algorithm", [
    "stack_push_pop",
    "stack_search",
    "stack_reverse",
    "queue_enqueue_dequeue",
    "queue_search",
    "queue_reverse",
])
def test_visualizer_runs_stack_and_queue_algorithms(client, algorithm, tmp_path, monkeypatch):
    monkeypatch.setattr(app, "PLOT_DIR", str(tmp_path))
    response = client.get(
        "/analyze", query_string={"algo": algorithm, "step": 2, "n_max": 4}
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["algo"] == algorithm
    assert payload["complexity"] == "O(n)"
    assert payload["points_measured"] == 3
    assert payload["operations_at_largest_n"] > 0
    assert base64.b64decode(payload["image_base64"]).startswith(b"\x89PNG")
    assert (tmp_path / f"{algorithm}_step2_n4.png").exists()


def test_index_lists_stack_and_queue_algorithms(client):
    payload = client.get("/").get_json()
    assert {
        "stack_push_pop",
        "stack_search",
        "stack_reverse",
        "queue_enqueue_dequeue",
        "queue_search",
        "queue_reverse",
    }.issubset(payload["algorithms"])
