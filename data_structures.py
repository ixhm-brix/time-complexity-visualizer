"""Stack and Queue implementations used by the visualizer.

Both are backed by a plain Python list. Removing from or inspecting an empty
structure raises ``IndexError``, the same way ``list.pop()`` does, instead of
returning a sentinel value that could be confused with a stored item.
"""


class Stack:
    """Last-in, first-out collection."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items!r})"


class Queue:
    """First-in, first-out collection.

    ``enqueue`` appends to the end of the list (O(1) amortized). ``dequeue``
    removes from the front with ``list.pop(0)``, which shifts every remaining
    element and is therefore O(n). That is deliberate: it gives queue
    operations a curve that visibly differs from the stack's O(1) operations
    when plotted. A production queue would use ``collections.deque``.
    """

    def __init__(self):
        self._items = []

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)

    def front(self):
        if self.is_empty():
            raise IndexError("front from empty queue")
        return self._items[0]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Queue({self._items!r})"
