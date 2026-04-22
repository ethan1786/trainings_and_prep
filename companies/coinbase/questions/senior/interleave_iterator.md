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
```java
List<Integer> interleave(List<List<Integer>> arrays) {
    // Round-robin across arrays; skip exhausted arrays
    // interleave([[1, 2, 3], [6], [7, 8]]) -> [1, 6, 7, 2, 8, 3]
}
```

### Level 2: Iterator Abstraction
```java
interface MyIterator {
    boolean hasNext();
    int getNext();  // throws NoSuchElementException if empty
}

class ListIterator implements MyIterator {
    ListIterator(List<Integer> items) {...}
}

class RangeIterator implements MyIterator {
    RangeIterator(int start, int end) {...}  // [start, end), exclusive end
}
```

### Level 3: Composable Interleave Iterator
```java
class InterleaveIterator implements MyIterator {
    InterleaveIterator(List<MyIterator> iterators) {...}
    // Cycles through iterators round-robin, dropping exhausted ones
    // it1=[1,2,3], it2=range(10,12), it3=[20] -> 1,10,20,2,11,3
}
```

---

## Solution Approach

### Level 1
**Core Idea:** Outer loop over position index (0 to max_len-1), inner loop over each array — bounds-check to skip exhausted arrays.

```java
List<Integer> interleave(List<List<Integer>> arrays) {
    List<Integer> result = new ArrayList<>();
    int maxLen = arrays.stream().mapToInt(List::size).max().orElse(0);
    for (int i = 0; i < maxLen; i++) {
        for (List<Integer> a : arrays) {
            if (i < a.size()) result.add(a.get(i));
        }
    }
    return result;
}
```

**Complexity:** O(N) time, O(N) space — N = total elements

### Level 2
**Core Idea:** Encapsulate traversal state. Both implementations maintain a pointer/counter; `hasNext` is a bounds check; `getNext` advances state.

```java
import java.util.NoSuchElementException;

interface MyIterator {
    boolean hasNext();
    int getNext();
}

class ListIterator implements MyIterator {
    private final List<Integer> items;
    private int index = 0;

    ListIterator(List<Integer> items) { this.items = items; }

    public boolean hasNext() { return index < items.size(); }

    public int getNext() {
        if (!hasNext()) throw new NoSuchElementException();
        return items.get(index++);
    }
}

class RangeIterator implements MyIterator {
    private int current;
    private final int end;

    RangeIterator(int start, int end) { this.current = start; this.end = end; }

    public boolean hasNext() { return current < end; }

    public int getNext() {
        if (!hasNext()) throw new NoSuchElementException();
        return current++;
    }
}
```

**Complexity:** O(1) per call, O(1) extra space

### Level 3
**Core Idea:** Use a deque as a circular queue of active iterators. Pop from front, yield one element, push back to rear if not exhausted. Exhausted iterators are naturally dropped.

```java
import java.util.ArrayDeque;
import java.util.Deque;

class InterleaveIterator implements MyIterator {
    private final Deque<MyIterator> queue = new ArrayDeque<>();

    InterleaveIterator(List<MyIterator> iterators) {
        for (MyIterator it : iterators) {
            if (it.hasNext()) queue.addLast(it);
        }
    }

    public boolean hasNext() { return !queue.isEmpty(); }

    public int getNext() {
        if (!hasNext()) throw new NoSuchElementException();
        MyIterator it = queue.removeFirst();
        int val = it.getNext();
        if (it.hasNext()) queue.addLast(it);
        return val;
    }
}
```

**Complexity:** O(K) init, O(1) amortized per `getNext` — K = number of iterators

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Thread safety:** `getNext` is not atomic — two threads racing on `removeFirst` + `addLast` will corrupt the queue. Wrap the deque operations in a `ReentrantReadWriteLock` or use a `ConcurrentLinkedDeque`.
- **Infinite iterators:** The design handles them naturally — an infinite iterator stays in the queue forever. Callers must track termination conditions themselves.
- **Back-pressure:** If the source iterators are I/O-bound (network, disk), round-robin will block on the slowest one. An async variant using reactive streams or `CompletableFuture` would allow non-blocking interleaving.
- **Error propagation:** If one iterator raises mid-flight, the deque is left in a partially consumed state. Define whether the error should propagate immediately or be skipped/logged.

### Common Interview Traps
- **Index-based round-robin alternative:** Using `currentIndex % iterators.size()` requires scanning over exhausted iterators every call. The deque avoids this entirely — make sure you can explain why.
- **Empty iterators at init:** Skip iterators with `hasNext() == false` at construction time. Forgetting this causes `getNext` to throw on the first call even when other iterators have data.
- **`getNext` contract:** Must throw `NoSuchElementException` (not return null) when empty. Callers rely on this for `while` loop termination.
- **Deque is O(1) removeFirst, ArrayList is O(N):** If you use an `ArrayList` and `remove(0)`, each call is O(K). Important distinction to call out.

### How to Push Forward as Staff+
- **Weighted interleaving:** "A natural extension is weighted round-robin — iterator A gets 2 slots per cycle, iterator B gets 1. I'd represent this as emitting each iterator's weight count before moving to the next, or using a priority queue keyed on `consumed / weight`."
- **Composability:** `InterleaveIterator` itself implements `MyIterator`, so you can nest them: `new InterleaveIterator(List.of(new InterleaveIterator(List.of(a, b)), c))`. Demonstrate this to show the design is recursive/composable.
- **Connect to Coinbase domain:** This pattern appears in trade matching engines — interleaving order streams from multiple venues (Coinbase Advanced, Pro, L3 feeds) in round-robin or priority order before feeding into a single aggregated order book.
- **Async / streaming variant:** "In a streaming data pipeline, this becomes a fan-in merge of async generators. I'd use a blocking queue per source and a single consumer that polls them round-robin."
- **Lazy vs. eager tradeoff:** Eagerly materializing (Level 1) is fine for small in-memory arrays. Lazy iteration (Level 3) is essential when sources are large datasets or infinite streams — proactively mention this distinction before the interviewer asks.
