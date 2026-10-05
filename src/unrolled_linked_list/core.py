"""Unrolled linked list implementation.

An unrolled linked list stores a small array of elements in each node, rather
than one element per node as in a classic singly linked list. The motivation is
cache locality: sequential traversal touches far fewer nodes, and each node's
internal list is contiguous in memory, so hardware prefetching works in our
favour.

Design decisions (stated plainly so the tests and the reader agree):

* Fixed node capacity. We do not implement splitting/merging based on fill
  ratio. Each node holds at most ``node_capacity`` elements; insertions into a
  full node split it in half and splice in a new node. This keeps the logic
  small and the invariants easy to reason about.
* Zero-based integer indexing into the logical sequence, matching Python list
  semantics. Out-of-range indices raise ``IndexError``.
* Mutation while iterating is not specially detected. We document this rather
  than attempt to track concurrent modification; the behaviour mirrors what you
  get from a hand-rolled linked list.
* Elements are compared by value for ``__contains__`` and ``remove``. Equality
  with ``==`` is used, so custom objects participate naturally.
* ``index`` and ``remove`` raise ``ValueError`` when the element is absent,
  matching the built-in list's contract.
"""

from __future__ import annotations

from typing import Any, Iterator, List, Optional


class Node:
    """A single node holding up to ``capacity`` elements.

    We keep ``elements`` as a plain Python list. The list is dense (no gaps):
    every slot from index 0 up to ``len(elements) - 1`` is occupied. Relying on
    a dense representation makes the split and append logic straightforward and
    avoids sentinel values.
    """

    __slots__ = ("capacity", "elements", "next")

    def __init__(self, capacity: int) -> None:
        if capacity < 2:
            # A capacity of 1 would defeat the point of unrolling and would
            # also break the split logic, which needs at least two slots to
            # divide evenly.
            raise ValueError("node capacity must be at least 2")
        self.capacity = capacity
        self.elements: List[Any] = []
        self.next: Optional["Node"] = None

    def is_full(self) -> bool:
        return len(self.elements) >= self.capacity

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Node(elements={self.elements!r}, capacity={self.capacity})"


class UnrolledLinkedList:
    """An unrolled linked list with fixed-capacity nodes.

    Example::

        ull = UnrolledLinkedList(node_capacity=4)
        for i in range(10):
            ull.append(i)
        ull[3]      # -> 3
        ull[3] = 99
        ull.remove(0)
        list(ull)   # -> [1, 2, 99, 4, 5, 6, 7, 8, 9]
    """

    def __init__(self, node_capacity: int = 4) -> None:
        if node_capacity < 2:
            raise ValueError("node capacity must be at least 2")
        self._node_capacity: int = node_capacity
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None
        self._size: int = 0

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------

    def _new_node(self) -> Node:
        return Node(self._node_capacity)

    def _find_node_for_index(self, index: int) -> "tuple[Node, int]":
        """Return ``(node, local_index)`` for the global ``index``.

        Assumes the caller has already validated ``0 <= index < len(self)``.
        Walking the list linearly is the expected access pattern for this data
        structure; random access is O(n) just as with a plain linked list.
        """
        remaining = index
        node = self._head
        assert node is not None  # invariant: non-empty list has a head
        while True:
            count = len(node.elements)
            if remaining < count:
                return node, remaining
            remaining -= count
            node = node.next
            assert node is not None  # invariant: index was in range

    def _split_full_node(self, node: Node, prev: Optional[Node]) -> "tuple[Node, Node]":
        """Split ``node`` (which must be full) in place and return ``(node, new_node)``.

        The first half of the elements stays in ``node``; the second half move
        into a freshly allocated node inserted immediately after. We split in
        half rather than moving a single element because it keeps nodes around
        half-full on average, which is the stated trade-off of this structure:
        waste some memory to gain locality.
        """
        assert node.is_full(), "_split_full_node called on a non-full node"
        mid = len(node.elements) // 2
        new_node = self._new_node()
        new_node.elements = node.elements[mid:]
        node.elements = node.elements[:mid]
        new_node.next = node.next
        node.next = new_node
        if self._tail is node:
            self._tail = new_node
        return node, new_node

    # ------------------------------------------------------------------
    # Sequence protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        node = self._head
        while node is not None:
            for item in node.elements:
                yield item
            node = node.next

    def __contains__(self, item: Any) -> bool:
        for existing in self:
            if existing == item:
                return True
        return False

    def __getitem__(self, index: int) -> Any:
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(self._size))]
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")
        node, local = self._find_node_for_index(index)
        return node.elements[local]

    def __setitem__(self, index: int, value: Any) -> None:
        if isinstance(index, slice):
            raise TypeError("slice assignment is not supported")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")
        node, local = self._find_node_for_index(index)
        node.elements[local] = value

    def __delitem__(self, index: int) -> None:
        if isinstance(index, slice):
            raise TypeError("slice deletion is not supported")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")
        node, local = self._find_node_for_index(index)
        del node.elements[local]
        self._size -= 1
        # If the node is now empty and it is not the only node, drop it to
        # avoid accumulating dead nodes during heavy deletion. Keeping a
        # single empty node is harmless and simplifies append logic.
        if not node.elements and (node is not self._head or node.next is not None):
            self._unlink_node(node)

    def _unlink_node(self, node: Node) -> None:
        """Remove ``node`` from the chain. Assumes it is present."""
        if node is self._head:
            self._head = node.next
            if self._head is None:
                self._tail = None
            return
        prev = self._head
        assert prev is not None
        while prev is not None and prev.next is not node:
            prev = prev.next
        assert prev is not None, "_unlink_node: node not in chain"
        prev.next = node.next
        if node is self._tail:
            self._tail = prev

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------

    def append(self, item: Any) -> None:
        """Append ``item`` to the end of the sequence. O(1) amortised."""
        if self._tail is None:
            node = self._new_node()
            self._head = node
            self._tail = node
            node.elements.append(item)
        elif self._tail.is_full():
            # Tail is full: split it, then append to whichever half has room.
            # After a half-split of a full node, both halves have at least one
            # free slot (capacity >= 2 guarantees this), so the new tail always
            # has room for one more item.
            _, new_tail = self._split_full_node(self._tail, self._find_prev_of_tail())
            new_tail.elements.append(item)
            self._tail = new_tail
        else:
            self._tail.elements.append(item)
        self._size += 1

    def _find_prev_of_tail(self) -> Optional[Node]:
        if self._head is self._tail:
            return None
        prev = self._head
        assert prev is not None
        while prev.next is not self._tail:
            prev = prev.next
            assert prev is not None
        return prev

    def insert(self, index: int, item: Any) -> None:
        """Insert ``item`` before ``index``.

        Negative indices and indices beyond the end are clamped to the start or
        end respectively, matching the leniency of ``list.insert``.
        """
        if index < 0:
            index = max(0, index + self._size)
        if index >= self._size:
            self.append(item)
            return
        if index == 0 and self._head is not None and not self._head.is_full():
            self._head.elements.insert(0, item)
            self._size += 1
            return
        node, local = self._find_node_for_index(index)
        if node.is_full():
            node, new_node = self._split_full_node(node, self._prev_of(node))
            # After the split, decide which node receives the insertion so the
            # logical order is preserved. If the target local index falls in
            # the first half, insert there; otherwise adjust and insert into
            # the new node.
            first_half_len = len(node.elements)
            if local <= first_half_len:
                node.elements.insert(local, item)
            else:
                new_node.elements.insert(local - first_half_len, item)
        else:
            node.elements.insert(local, item)
        self._size += 1

    def _prev_of(self, target: Node) -> Optional[Node]:
        if target is self._head:
            return None
        prev = self._head
        assert prev is not None
        while prev is not None and prev.next is not target:
            prev = prev.next
        return prev

    def remove(self, item: Any) -> None:
        """Remove the first occurrence of ``item``. Raises ``ValueError`` if absent."""
        index = self.index(item)
        del self[index]

    def index(self, item: Any) -> int:
        """Return the index of the first element equal to ``item``.

        Raises ``ValueError`` if not present, matching ``list.index``.
        """
        for i, existing in enumerate(self):
            if existing == item:
                return i
        raise ValueError(f"{item!r} is not in list")

    def pop(self, index: int = -1) -> Any:
        """Remove and return the element at ``index``. Raises ``IndexError`` if empty."""
        if self._size == 0:
            raise IndexError("pop from empty list")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")
        value = self[index]
        del self[index]
        return value

    def clear(self) -> None:
        self._head = None
        self._tail = None
        self._size = 0

    def extend(self, items: "Any") -> None:
        """Append each element of ``items`` in order."""
        for item in items:
            self.append(item)

    def to_list(self) -> list:
        """Return a flat Python list of all elements. Mainly for debugging/tests."""
        return list(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UnrolledLinkedList):
            return list(self) == list(other)
        if isinstance(other, list):
            return list(self) == other
        return NotImplemented

    def __repr__(self) -> str:
        return f"UnrolledLinkedList({list(self)!r}, node_capacity={self._node_capacity})"
