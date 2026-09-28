"""Run with:
    python -m unittest data_structures_test.py -v
"""
import unittest

from data_structures import Queue, Stack


class TestStack(unittest.TestCase):
    def setUp(self):
        self.stack = Stack()

    def test_new_stack_is_empty(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(len(self.stack), 0)

    def test_push_increases_length(self):
        self.stack.push(1)
        self.stack.push(2)
        self.assertEqual(len(self.stack), 2)
        self.assertFalse(self.stack.is_empty())

    def test_pop_returns_items_in_lifo_order(self):
        for value in (1, 2, 3):
            self.stack.push(value)
        self.assertEqual([self.stack.pop() for _ in range(3)], [3, 2, 1])

    def test_pop_decreases_length(self):
        self.stack.push("a")
        self.stack.push("b")
        self.stack.pop()
        self.assertEqual(len(self.stack), 1)

    def test_pop_empty_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_peek_returns_top_without_removing(self):
        self.stack.push(10)
        self.stack.push(20)
        self.assertEqual(self.stack.peek(), 20)
        self.assertEqual(len(self.stack), 2)

    def test_peek_empty_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.stack.peek()

    def test_lifo_order_with_mixed_operations(self):
        self.stack.push(1)
        self.stack.push(2)
        self.assertEqual(self.stack.pop(), 2)
        self.stack.push(3)
        self.stack.push(4)
        self.assertEqual(self.stack.pop(), 4)
        self.assertEqual(self.stack.pop(), 3)
        self.assertEqual(self.stack.pop(), 1)
        self.assertTrue(self.stack.is_empty())

    def test_repr_contains_class_name(self):
        self.stack.push(1)
        self.assertIn("Stack", repr(self.stack))

    def test_handles_none_and_falsy_values(self):
        for value in (None, 0, False):
            self.stack.push(value)
        self.assertIs(self.stack.pop(), False)
        self.assertEqual(self.stack.pop(), 0)
        self.assertIsNone(self.stack.pop())
        self.assertTrue(self.stack.is_empty())


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()

    def test_new_queue_is_empty(self):
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(len(self.queue), 0)

    def test_enqueue_increases_length(self):
        self.queue.enqueue(1)
        self.queue.enqueue(2)
        self.assertEqual(len(self.queue), 2)
        self.assertFalse(self.queue.is_empty())

    def test_dequeue_returns_items_in_fifo_order(self):
        for value in (1, 2, 3):
            self.queue.enqueue(value)
        self.assertEqual([self.queue.dequeue() for _ in range(3)], [1, 2, 3])

    def test_dequeue_decreases_length(self):
        self.queue.enqueue("a")
        self.queue.enqueue("b")
        self.queue.dequeue()
        self.assertEqual(len(self.queue), 1)

    def test_dequeue_empty_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.queue.dequeue()

    def test_front_returns_first_without_removing(self):
        self.queue.enqueue(10)
        self.queue.enqueue(20)
        self.assertEqual(self.queue.front(), 10)
        self.assertEqual(len(self.queue), 2)

    def test_front_empty_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.queue.front()

    def test_fifo_order_with_mixed_operations(self):
        self.queue.enqueue(1)
        self.queue.enqueue(2)
        self.assertEqual(self.queue.dequeue(), 1)
        self.queue.enqueue(3)
        self.queue.enqueue(4)
        self.assertEqual(self.queue.dequeue(), 2)
        self.assertEqual(self.queue.dequeue(), 3)
        self.assertEqual(self.queue.dequeue(), 4)
        self.assertTrue(self.queue.is_empty())

    def test_repr_contains_class_name(self):
        self.queue.enqueue(1)
        self.assertIn("Queue", repr(self.queue))

    def test_handles_none_and_falsy_values(self):
        for value in (None, 0, False):
            self.queue.enqueue(value)
        self.assertIsNone(self.queue.dequeue())
        self.assertEqual(self.queue.dequeue(), 0)
        self.assertIs(self.queue.dequeue(), False)
        self.assertTrue(self.queue.is_empty())


if __name__ == "__main__":
    unittest.main()
