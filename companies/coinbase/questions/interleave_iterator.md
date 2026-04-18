# Interleave Iterator

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 30-45 min
**Key Topics:** Iterator Pattern, Deque, Round-Robin Scheduling, Lazy Evaluation

---

## Problem Statement

Build a system that interleaves elements from multiple sources in round-robin order. Implement this progressively: first as a simple function, then using the Iterator pattern, then as a composable `InterleaveIterator` that manages any number of iterators.

## Requirements

### Level 1: Array Interleaving
```python
def interleave(arrays: list[list[int]]) -> list[int]:
    # Round-robin across arrays; skip exhausted arrays
    # interleave([[1, 2, 3], [6], [7, 8]]) -> [1, 6, 7, 2, 8, 3]
```

### Level 2: Iterator Abstraction
```python
class Iterator(ABC):
    def has_next(self) -> bool: ...
    def get_next(self) -> int: ...  # raises StopIteration if empty

class ListIterator(Iterator):
    def __init__(self, items: list[int]): ...

class RangeIterator(Iterator):
    def __init__(self, start: int, end: int): ...  # [start, end), exclusive end
```

### Level 3: Composable Interleave Iterator
```python
class InterleaveIterator(Iterator):
    def __init__(self, iterators: list[Iterator]): ...
    # Cycles through iterators round-robin, dropping exhausted ones
    # it1=[1,2,3], it2=range(10,12), it3=[20] -> 1,10,20,2,11,3
```

---

## Solution Approach

### Level 1
**Core Idea:** Outer loop over position index (0 to max_len-1), inner loop over each array — bounds-check to skip exhausted arrays.

```python
def interleave(arrays: list[list[int]]) -> list[int]:
    result = []
    max_len = max((len(a) for a in arrays), default=0)
    for i in range(max_len):
        for a in arrays:
            if i < len(a):
                result.append(a[i])
    return result
```

**Complexity:** O(N) time, O(N) space — N = total elements

### Level 2
**Core Idea:** Encapsulate traversal state. Both implementations maintain a pointer/counter; `has_next` is a bounds check; `get_next` advances state.

```python
from abc import ABC, abstractmethod

class Iterator(ABC):
    @abstractmethod
    def has_next(self) -> bool: ...
    @abstractmethod
    def get_next(self) -> int: ...

class ListIterator(Iterator):
    def __init__(self, items: list[int]):
        self.items = items
        self.index = 0

    def has_next(self) -> bool:
        return self.index < len(self.items)

    def get_next(self) -> int:
        if not self.has_next():
            raise StopIteration
        val = self.items[self.index]
        self.index += 1
        return val

class RangeIterator(Iterator):
    def __init__(self, start: int, end: int):
        self.current = start
        self.end = end

    def has_next(self) -> bool:
        return self.current < self.end

    def get_next(self) -> int:
        if not self.has_next():
            raise StopIteration
        val = self.current
        self.current += 1
        return val
```

**Complexity:** O(1) per call, O(1) extra space

### Level 3
**Core Idea:** Use a deque as a circular queue of active iterators. Pop from front, yield one element, push back to rear if not exhausted. Exhausted iterators are naturally dropped.

```python
from collections import deque

class InterleaveIterator(Iterator):
    def __init__(self, iterators: list[Iterator]):
        self.queue = deque(it for it in iterators if it.has_next())

    def has_next(self) -> bool:
        return bool(self.queue)

    def get_next(self) -> int:
        if not self.has_next():
            raise StopIteration
        it = self.queue.popleft()
        val = it.get_next()
        if it.has_next():
            self.queue.append(it)
        return val
```

**Complexity:** O(K) init, O(1) amortized per `get_next` — K = number of iterators

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Thread safety:** `get_next` is not atomic — two threads racing on `popleft` + `append` will corrupt the queue. Wrap the deque operations in a `threading.Lock` or use a thread-safe queue (`queue.Queue`).
- **Infinite iterators:** The design handles them naturally — an infinite iterator stays in the queue forever. Callers must track termination conditions themselves.
- **Back-pressure:** If the source iterators are I/O-bound (network, disk), round-robin will block on the slowest one. An async variant using `asyncio` + `asyncio.Queue` would allow non-blocking interleaving.
- **Error propagation:** If one iterator raises mid-flight, the deque is left in a partially consumed state. Define whether the error should propagate immediately or be skipped/logged.

### Common Interview Traps
- **Index-based round-robin alternative:** Using `current_index % len(iterators)` requires scanning over exhausted iterators every call. The deque avoids this entirely — make sure you can explain why.
- **Empty iterators at init:** Skip iterators with `has_next() == False` at construction time. Forgetting this causes `get_next` to raise on the first call even when other iterators have data.
- **`get_next` contract:** Must raise `StopIteration` (not return None) when empty. Callers rely on this for `while` loop termination.
- **Deque is O(1) popleft, list is O(N):** If you use a list and `pop(0)`, each call is O(K). Important distinction to call out.

### How to Push Forward as Staff+
- **Weighted interleaving:** "A natural extension is weighted round-robin — iterator A gets 2 slots per cycle, iterator B gets 1. I'd represent this as emitting each iterator's weight count before moving to the next, or using a priority queue keyed on `consumed / weight`."
- **Composability:** `InterleaveIterator` itself implements `Iterator`, so you can nest them: `InterleaveIterator([InterleaveIterator([a, b]), c])`. Demonstrate this to show the design is recursive/composable.
- **Connect to Coinbase domain:** This pattern appears in trade matching engines — interleaving order streams from multiple venues (Coinbase Advanced, Pro, L3 feeds) in round-robin or priority order before feeding into a single aggregated order book.
- **Async / streaming variant:** "In a streaming data pipeline, this becomes a fan-in merge of async generators. I'd use `asyncio.Queue` per source and a single consumer that polls them round-robin."
- **Lazy vs. eager tradeoff:** Eagerly materializing (Level 1) is fine for small in-memory arrays. Lazy iteration (Level 3) is essential when sources are large datasets or infinite streams — proactively mention this distinction before the interviewer asks.
