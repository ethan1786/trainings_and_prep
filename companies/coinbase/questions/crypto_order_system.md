# Crypto Order System

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 45-60 min
**Key Topics:** State Machine, HashMap, LinkedHashMap/OrderedDict, Sharding, Consistent Hashing

---

## Problem Statement

Build a crypto trading order management system. Orders can be placed, paused, resumed, and cancelled. The system must display all live orders in insertion order and support bulk operations by user. Eventually the system must shard orders across multiple streams.

## Requirements

### Level 1: Core Order Lifecycle

```python
class CryptoOrderSystem:
    def place(self, order_id: str, currency: str, amount: float, price: float) -> None:
        """Add order in ACTIVE state. Ignore if order_id already exists."""

    def pause(self, order_id: str) -> bool:
        """ACTIVE → PAUSED. False if missing or not ACTIVE."""

    def resume(self, order_id: str) -> bool:
        """PAUSED → ACTIVE. False if missing or not PAUSED."""

    def cancel(self, order_id: str) -> bool:
        """Remove order. True for both ACTIVE and PAUSED. False if missing."""

    def display_all_live_orders(self) -> list[str]:
        """
        Return all non-cancelled orders in insertion order.
        Format: ["order1", "order2(paused)", "order3"]
        Paused orders get "(paused)" suffix.
        """
```

**State machine:**
```
place() → ACTIVE ──pause()──→ PAUSED
             │                    │
          cancel()            resume() → ACTIVE
             │                    │
          REMOVED             cancel()
                                  │
                               REMOVED
```

### Level 2: User-Scoped Operations

```python
    def place(self, order_id: str, user_id: str, currency: str, amount: float, price: float) -> None:
        """place() now includes user_id."""

    def cancel_all_by_user(self, user_id: str) -> int:
        """Cancel all orders for user. Returns count cancelled. Cleans up user index."""
```

### Level 3: Multi-Stream Sharding

```python
class CryptoOrderSystem:
    def __init__(self, num_streams: int):
        """
        Distribute orders across num_streams shards.
        Routing: hash(user_id) % num_streams.
        All orders for a user go to the same stream.
        display_all_live_orders() aggregates across all streams.
        """
```

---

## Solution Approach

### Level 1

**Core Idea:** `OrderedDict` (or insertion-order `dict` in Python 3.7+) for O(1) lookup while preserving insertion order for `display_all_live_orders`. State is an enum on the `Order` object.

**Key Decisions:** Cancel removes from the dict immediately — no tombstone needed since cancelled orders aren't displayed and there's no history requirement. State validation lives in the system, not the order, because the system controls the transitions.

```python
from enum import Enum
from collections import OrderedDict

class OrderState(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"

class Order:
    def __init__(self, order_id: str, currency: str, amount: float, price: float):
        self.order_id = order_id
        self.currency = currency
        self.amount = amount
        self.price = price
        self.state = OrderState.ACTIVE

class CryptoOrderSystem:
    def __init__(self):
        self.orders: OrderedDict[str, Order] = OrderedDict()

    def place(self, order_id: str, currency: str, amount: float, price: float) -> None:
        if order_id not in self.orders:
            self.orders[order_id] = Order(order_id, currency, amount, price)

    def pause(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if not order or order.state != OrderState.ACTIVE:
            return False
        order.state = OrderState.PAUSED
        return True

    def resume(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if not order or order.state != OrderState.PAUSED:
            return False
        order.state = OrderState.ACTIVE
        return True

    def cancel(self, order_id: str) -> bool:
        if order_id not in self.orders:
            return False
        del self.orders[order_id]
        return True

    def display_all_live_orders(self) -> list[str]:
        result = []
        for order_id, order in self.orders.items():
            if order.state == OrderState.PAUSED:
                result.append(f"{order_id}(paused)")
            else:
                result.append(order_id)
        return result
```

**Example:**
```python
system.place("order1", "BTC", 10, 50000.0)
system.place("order2", "ETH", 100, 3000.0)
system.place("order3", "BTC", 5, 51000.0)
system.place("order4", "ETH", 50, 3100.0)
system.pause("order2")
system.pause("order3")
system.display_all_live_orders()
# ["order1", "order2(paused)", "order3(paused)", "order4"]
system.cancel("order2")
system.display_all_live_orders()
# ["order1", "order3(paused)", "order4"]
```

**Complexity:** All operations O(1) except display_all_live_orders O(N).

### Level 2

**Core Idea:** Add a `user_orders` index: `dict[user_id -> set[order_id]]`. Keep it consistent with `self.orders` on every mutation. `cancel_all_by_user` iterates the set and removes from both structures.

**Key Decisions:** The secondary index must be updated in `cancel()` too — if single-order cancels don't maintain the user index, it will contain stale references and `cancel_all_by_user` will fail silently or error.

```python
class Order:
    def __init__(self, order_id, user_id, currency, amount, price):
        self.order_id = order_id
        self.user_id = user_id
        self.currency = currency
        self.amount = amount
        self.price = price
        self.state = OrderState.ACTIVE

class CryptoOrderSystem:
    def __init__(self):
        self.orders: OrderedDict[str, Order] = OrderedDict()
        self.user_orders: dict[str, set] = {}  # user_id -> {order_id}

    def place(self, order_id: str, user_id: str, currency: str, amount: float, price: float) -> None:
        if order_id in self.orders:
            return
        self.orders[order_id] = Order(order_id, user_id, currency, amount, price)
        self.user_orders.setdefault(user_id, set()).add(order_id)

    def cancel(self, order_id: str) -> bool:
        if order_id not in self.orders:
            return False
        user_id = self.orders[order_id].user_id
        del self.orders[order_id]
        if user_id in self.user_orders:
            self.user_orders[user_id].discard(order_id)
            if not self.user_orders[user_id]:
                del self.user_orders[user_id]
        return True

    def cancel_all_by_user(self, user_id: str) -> int:
        order_ids = list(self.user_orders.pop(user_id, set()))
        for order_id in order_ids:
            self.orders.pop(order_id, None)
        return len(order_ids)

    # pause() and resume() unchanged
```

**Complexity:** cancel_all_by_user O(K) where K = orders for that user. All other operations unchanged.

### Level 3

**Core Idea:** Create `num_streams` independent `CryptoOrderSystem` instances (Level 2). Route each user to `streams[hash(user_id) % num_streams]`. All single-order operations route to the correct stream. `display_all_live_orders` aggregates across all streams.

**Key Decisions:** Sharding by `user_id` (not `order_id`) is critical so that `cancel_all_by_user` only touches one stream. If sharded by `order_id`, a user's orders would scatter, requiring a full cross-stream scan for bulk cancel.

```python
class CryptoOrderSystem:
    def __init__(self, num_streams: int):
        self.num_streams = num_streams
        self.streams = [_StreamOrderSystem() for _ in range(num_streams)]

    def _stream(self, user_id: str) -> "_StreamOrderSystem":
        return self.streams[hash(user_id) % self.num_streams]

    def place(self, order_id: str, user_id: str, currency: str, amount: float, price: float) -> None:
        self._stream(user_id).place(order_id, user_id, currency, amount, price)

    def pause(self, order_id: str, user_id: str) -> bool:
        return self._stream(user_id).pause(order_id)

    def resume(self, order_id: str, user_id: str) -> bool:
        return self._stream(user_id).resume(order_id)

    def cancel(self, order_id: str, user_id: str) -> bool:
        return self._stream(user_id).cancel(order_id)

    def cancel_all_by_user(self, user_id: str) -> int:
        return self._stream(user_id).cancel_all_by_user(user_id)

    def display_all_live_orders(self) -> list[str]:
        result = []
        for stream in self.streams:
            result.extend(stream.display_all_live_orders())
        return result

# _StreamOrderSystem is the Level 2 implementation
```

**Complexity:** All routed operations remain O(1) or O(K). display_all_live_orders is O(N) across all streams, but parallelizable.

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Thread safety:** In a concurrent environment, each stream needs its own lock. Locking at the stream level (not the whole system) allows streams to operate in parallel — this is the key benefit of the sharded design. Use `threading.RLock` per stream.
- **Consistent hashing:** `hash(user_id) % N` breaks when `N` changes — nearly all users reroute to a different stream. Consistent hashing (e.g., using a virtual node ring) minimizes user movement when streams are added/removed.
- **Cross-stream display ordering:** `display_all_live_orders` with multiple streams loses global insertion order. If total order is required, include a sequence number in each order and merge-sort on display.
- **Single-order cancel without user_id:** In Level 3, `cancel(order_id)` requires knowing `user_id` to route to the right stream. If only `order_id` is known, you need a global order→user index or broadcast to all streams. Ask the interviewer which access pattern they expect.
- **Persistence:** In production, each stream would correspond to a Kafka partition or a DB shard, not an in-memory dict. Crash recovery via Kafka offset replay or DB WAL.

### Common Interview Traps

- **Forgetting to update `user_orders` in single `cancel()`:** The most common Level 2 bug. Results in stale entries in the user index, making `cancel_all_by_user` undercounting.
- **Sharding by order_id instead of user_id:** Conceptually simpler but makes `cancel_all_by_user` O(N) across all streams. The interviewer is specifically testing whether you reason about which access pattern to optimize for.
- **`display_all_live_orders` ordering across streams:** The aggregated display is not globally ordered unless you add a sequence counter. Most candidates don't notice this.
- **`pause()` / `resume()` in Level 3:** The spec doesn't give `user_id` for these in Level 3. Either the interface must change to include it, or you maintain a global `order_id → stream_idx` index. Worth raising before coding.

### How to Push Forward as Staff+

- Propose per-stream locks immediately when discussing Level 3: "Each stream can be its own goroutine/thread with its own lock — this gives us parallelism without a global bottleneck."
- Ask about rebalancing: "If a new stream is added, do we need to migrate existing orders? Consistent hashing avoids most of the migration but we'd still need a brief dual-read period."
- Connect to Coinbase's real architecture: Coinbase's matching engine is partitioned by trading pair (BTC-USD, ETH-USD). Orders for the same symbol go to the same partition, which is equivalent to sharding by `symbol` instead of `user_id`. Ask whether the product requirement favors user-centric or symbol-centric sharding.
- Raise the `display_all_live_orders` latency concern: "In production, a cross-shard scan for display purposes would be too slow for a live UI. We'd maintain a separate read model (e.g., a denormalized view in Redis or Elasticsearch) that aggregates order state asynchronously."
