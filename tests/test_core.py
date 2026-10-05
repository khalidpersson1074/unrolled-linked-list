import unittest

from unrolled_linked_list import UnrolledLinkedList, Node


class TestConstruction(unittest.TestCase):

    def test_empty_default_capacity(self):
        ull = UnrolledLinkedList()
        self.assertEqual(len(ull), 0)
        self.assertEqual(list(ull), [])
        self.assertEqual(ull.to_list(), [])

    def test_custom_capacity(self):
        ull = UnrolledLinkedList(node_capacity=8)
        for i in range(20):
            ull.append(i)
        self.assertEqual(ull.to_list(), list(range(20)))

    def test_capacity_must_be_at_least_two(self):
        with self.assertRaises(ValueError):
            UnrolledLinkedList(node_capacity=1)
        with self.assertRaises(ValueError):
            UnrolledLinkedList(node_capacity=0)

    def test_node_capacity_must_be_at_least_two(self):
        with self.assertRaises(ValueError):
            Node(capacity=1)


class TestAppendAndIteration(unittest.TestCase):

    def test_append_within_single_node(self):
        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(4):
            ull.append(i)
        self.assertEqual(ull.to_list(), [0, 1, 2, 3])
        self.assertEqual(len(ull), 4)

    def test_append_across_node_boundary_triggers_split(self):
        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(9):
            ull.append(i)
        self.assertEqual(ull.to_list(), list(range(9)))
        self.assertEqual(len(ull), 9)

    def test_iterate_many_elements(self):
        ull = UnrolledLinkedList(node_capacity=3)
        expected = list(range(100))
        for i in expected:
            ull.append(i)
        self.assertEqual(list(ull), expected)

    def test_contains(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(10):
            ull.append(i)
        self.assertIn(5, ull)
        self.assertNotIn(99, ull)
        self.assertIn(0, ull)
        self.assertIn(9, ull)

    def test_contains_empty(self):
        ull = UnrolledLinkedList()
        self.assertNotIn(0, ull)


class TestIndexing(unittest.TestCase):

    def test_getitem_positive(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(10):
            ull.append(i)
        for i in range(10):
            self.assertEqual(ull[i], i)

    def test_getitem_negative(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(10):
            ull.append(i)
        self.assertEqual(ull[-1], 9)
        self.assertEqual(ull[-10], 0)

    def test_getitem_out_of_range(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append(1)
        with self.assertRaises(IndexError):
            ull[1]
        with self.assertRaises(IndexError):
            ull[-2]

    def test_getitem_empty(self):
        ull = UnrolledLinkedList()
        with self.assertRaises(IndexError):
            ull[0]

    def test_setitem(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(6):
            ull.append(i)
        ull[2] = 99
        self.assertEqual(ull[2], 99)
        self.assertEqual(ull.to_list(), [0, 1, 99, 3, 4, 5])

    def test_setitem_negative(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(6):
            ull.append(i)
        ull[-1] = 99
        self.assertEqual(ull[-1], 99)

    def test_setitem_out_of_range(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append(1)
        with self.assertRaises(IndexError):
            ull[5] = 99
        with self.assertRaises(IndexError):
            ull[-2] = 99

    def test_setitem_slice_unsupported(self):
        ull = UnrolledLinkedList()
        with self.assertRaises(TypeError):
            ull[0:1] = [1]

    def test_getitem_slice(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(10):
            ull.append(i)
        self.assertEqual(ull[2:5], [2, 3, 4])
        self.assertEqual(ull[::2], [0, 2, 4, 6, 8])
        self.assertEqual(ull[::-1], list(range(9, -1, -1)))


class TestInsert(unittest.TestCase):

    def test_insert_at_start_with_room(self):
        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(3):
            ull.append(i)
        ull.insert(0, 99)
        self.assertEqual(ull.to_list(), [99, 0, 1, 2])

    def test_insert_at_start_when_head_full(self):
        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(4):
            ull.append(i)
        ull.insert(0, 99)
        self.assertEqual(ull.to_list(), [99, 0, 1, 2, 3])

    def test_insert_in_middle(self):
        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(6):
            ull.append(i)
        ull.insert(3, 99)
        self.assertEqual(ull.to_list(), [0, 1, 2, 99, 3, 4, 5])

    def test_insert_into_full_node_splits(self):
        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(4):
            ull.append(i)
        ull.insert(2, 99)
        self.assertEqual(ull.to_list(), [0, 1, 99, 2, 3])

    def test_insert_at_end_via_large_index(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        ull.insert(100, 99)
        self.assertEqual(ull.to_list(), [0, 1, 2, 3, 4, 99])

    def test_insert_negative_index_clamps_to_zero(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append(1)
        ull.insert(-100, 99)
        self.assertEqual(ull.to_list(), [99, 1])

    def test_insert_negative_index_in_range(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        ull.insert(-1, 99)
        self.assertEqual(ull.to_list(), [0, 1, 2, 3, 99, 4])

    def test_insert_into_empty(self):
        ull = UnrolledLinkedList()
        ull.insert(0, 42)
        self.assertEqual(ull.to_list(), [42])


class TestDeleteAndPop(unittest.TestCase):

    def test_delitem_middle(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(6):
            ull.append(i)
        del ull[2]
        self.assertEqual(ull.to_list(), [0, 1, 3, 4, 5])

    def test_delitem_first(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(6):
            ull.append(i)
        del ull[0]
        self.assertEqual(ull.to_list(), [1, 2, 3, 4, 5])

    def test_delitem_last(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(6):
            ull.append(i)
        del ull[5]
        self.assertEqual(ull.to_list(), [0, 1, 2, 3, 4])

    def test_delitem_negative(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(6):
            ull.append(i)
        del ull[-1]
        self.assertEqual(ull.to_list(), [0, 1, 2, 3, 4])

    def test_delitem_out_of_range(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append(1)
        with self.assertRaises(IndexError):
            del ull[5]
        with self.assertRaises(IndexError):
            del ull[-2]

    def test_delitem_empty_node_unlinks_when_not_only_node(self):
        ull = UnrolledLinkedList(node_capacity=2)
        for i in range(6):
            ull.append(i)
        # Delete elements until a node becomes empty; the structure should
        # remain consistent and iterable.
        for _ in range(3):
            del ull[0]
        self.assertEqual(ull.to_list(), [3, 4, 5])
        self.assertEqual(len(ull), 3)

    def test_delitem_slice_unsupported(self):
        ull = UnrolledLinkedList()
        with self.assertRaises(TypeError):
            del ull[0:1]

    def test_pop_default_last(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        self.assertEqual(ull.pop(), 4)
        self.assertEqual(ull.to_list(), [0, 1, 2, 3])

    def test_pop_index(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        self.assertEqual(ull.pop(2), 2)
        self.assertEqual(ull.to_list(), [0, 1, 3, 4])

    def test_pop_negative(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        self.assertEqual(ull.pop(-2), 3)

    def test_pop_empty_raises(self):
        ull = UnrolledLinkedList()
        with self.assertRaises(IndexError):
            ull.pop()

    def test_pop_out_of_range(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append(1)
        with self.assertRaises(IndexError):
            ull.pop(5)


class TestRemoveAndIndex(unittest.TestCase):

    def test_index_existing(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in [10, 20, 30, 40, 50]:
            ull.append(i)
        self.assertEqual(ull.index(30), 2)

    def test_index_missing_raises_value_error(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        with self.assertRaises(ValueError):
            ull.index(99)

    def test_index_empty_raises_value_error(self):
        ull = UnrolledLinkedList()
        with self.assertRaises(ValueError):
            ull.index(0)

    def test_remove_existing(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in [1, 2, 3, 2, 4]:
            ull.append(i)
        ull.remove(2)
        self.assertEqual(ull.to_list(), [1, 3, 2, 4])

    def test_remove_missing_raises_value_error(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append(1)
        with self.assertRaises(ValueError):
            ull.remove(99)

    def test_remove_uses_equality_not_identity(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.append("a")
        ull.append("b")
        ull.remove("a")
        self.assertEqual(ull.to_list(), ["b"])


class TestExtendClearEquiv(unittest.TestCase):

    def test_extend(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.extend([1, 2, 3, 4, 5])
        self.assertEqual(ull.to_list(), [1, 2, 3, 4, 5])

    def test_extend_empty(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.extend([])
        self.assertEqual(len(ull), 0)

    def test_clear(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(10):
            ull.append(i)
        ull.clear()
        self.assertEqual(len(ull), 0)
        self.assertEqual(list(ull), [])
        self.assertNotIn(5, ull)

    def test_clear_then_reuse(self):
        ull = UnrolledLinkedList(node_capacity=3)
        for i in range(5):
            ull.append(i)
        ull.clear()
        ull.append(99)
        self.assertEqual(ull.to_list(), [99])

    def test_equality_with_list(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.extend([1, 2, 3, 4])
        self.assertEqual(ull, [1, 2, 3, 4])
        self.assertNotEqual(ull, [1, 2, 3])

    def test_equality_with_other_ull(self):
        a = UnrolledLinkedList(node_capacity=3)
        b = UnrolledLinkedList(node_capacity=5)
        a.extend([1, 2, 3, 4])
        b.extend([1, 2, 3, 4])
        self.assertEqual(a, b)

    def test_repr_roundtrips_contents(self):
        ull = UnrolledLinkedList(node_capacity=3)
        ull.extend([1, 2, 3])
        r = repr(ull)
        self.assertIn("[1, 2, 3]", r)
        self.assertIn("node_capacity=3", r)


class TestLargeWorkload(unittest.TestCase):

    def test_mixed_operations_consistency(self):
        ull = UnrolledLinkedList(node_capacity=4)
        reference = []
        for i in range(50):
            ull.append(i)
            reference.append(i)
        for _ in range(20):
            del ull[0]
            del reference[0]
        ull.insert(0, 999)
        reference.insert(0, 999)
        for _ in range(5):
            ull.pop()
            reference.pop()
        self.assertEqual(ull.to_list(), reference)
        self.assertEqual(len(ull), len(reference))

    def test_all_equal_after_many_appends(self):
        ull = UnrolledLinkedList(node_capacity=4)
        expected = list(range(1000))
        ull.extend(expected)
        self.assertEqual(ull.to_list(), expected)
        self.assertEqual(len(ull), 1000)


if __name__ == "__main__":
    unittest.main()
