# unrolled-linked-list

A small, dependency-free Python implementation of an unrolled linked list: a linked list whose nodes each hold a small fixed-size array of elements, trading a little wasted memory for better cache locality on sequential traversal.

## Usage

```python
from unrolled_linked_list import UnrolledLinkedList

ull = UnrolledLinkedList(node_capacity=4)
ull.extend([1, 2, 3, 4, 5, 6])
print(ull[3])      # 4
ull.insert(0, 99)
ull.remove(2)
print(list(ull))   # [99, 1, 3, 4, 5, 6]
```

Exported names: `UnrolledLinkedList`, `Node`.

## Why this exists

A plain singly linked list allocates one node per element, so each hop is a pointer chase through memory with poor locality. An unrolled linked list packs several elements into each node, so a full sequential scan touches far fewer nodes and each node's internal array is contiguous, which is friendlier to CPU caches and prefetchers.

The trade-off this library makes: node capacity is fixed at construction time, and a full node is split in half before any further insertion. This keeps the logic small and the invariants obvious, at the cost of roughly half a node of wasted space in the worst case. There is no fill-ratio-based merging after deletes; empty interior nodes are simply unlinked.

## Awkward edges

Random access by index is O(n) — it walks the node chain — so this structure is not a drop-in replacement for a Python list in index-heavy code. Use it when you mostly iterate sequentially and occasionally mutate at the ends or by value lookup.

Negative indices behave like Python lists (e.g. `ull[-1]` is the last element). Slice *reading* works and returns a plain list; slice *assignment* and slice *deletion* raise `TypeError`, because the node-splicing semantics were not worth the complexity for this small library.

`remove` and `index` compare by `==`, matching `list`. They raise `ValueError`, not `IndexError`, when the element is absent.
