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

```java
class CryptoOrderSystem {
    void place(String orderId, String currency, double amount, double price);
    // Add order in ACTIVE state. Ignore if orderId already exists.

    boolean pause(String orderId);
    // ACTIVE → PAUSED. False if missing or not ACTIVE.

    boolean resume(String orderId);
    // PAUSED → ACTIVE. False if missing or not PAUSED.

    boolean cancel(String orderId);
    // Remove order. True for both ACTIVE and PAUSED. False if missing.

    List<String> displayAllLiveOrders();
    // Return all non-cancelled orders in insertion order.
    // Format: ["order1", "order2(paused)", "order3"]
    // Paused orders get "(paused)" suffix.
}
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

```java
    void place(String orderId, String userId, String currency, double amount, double price);
    // place() now includes userId.

    int cancelAllByUser(String userId);
    // Cancel all orders for user. Returns count cancelled. Cleans up user index.
```

### Level 3: Multi-Stream Sharding

```java
class CryptoOrderSystem {
    CryptoOrderSystem(int numStreams);
    // Distribute orders across numStreams shards.
    // Routing: hash(userId) % numStreams.
    // All orders for a user go to the same stream.
    // displayAllLiveOrders() aggregates across all streams.
}
```

---

## Solution Approach

### Level 1

**Core Idea:** `LinkedHashMap` for O(1) lookup while preserving insertion order for `displayAllLiveOrders`. State is an enum on the `Order` object.

**Key Decisions:** Cancel removes from the map immediately — no tombstone needed since cancelled orders aren't displayed and there's no history requirement. State validation lives in the system, not the order, because the system controls the transitions.

```java
enum OrderState { ACTIVE, PAUSED }

class Order {
    String orderId, currency;
    double amount, price;
    OrderState state;

    Order(String orderId, String currency, double amount, double price) {
        this.orderId = orderId;
        this.currency = currency;
        this.amount = amount;
        this.price = price;
        this.state = OrderState.ACTIVE;
    }
}

class CryptoOrderSystem {
    private Map<String, Order> orders = new LinkedHashMap<>();

    void place(String orderId, String currency, double amount, double price) {
        orders.putIfAbsent(orderId, new Order(orderId, currency, amount, price));
    }

    boolean pause(String orderId) {
        Order order = orders.get(orderId);
        if (order == null || order.state != OrderState.ACTIVE) return false;
        order.state = OrderState.PAUSED;
        return true;
    }

    boolean resume(String orderId) {
        Order order = orders.get(orderId);
        if (order == null || order.state != OrderState.PAUSED) return false;
        order.state = OrderState.ACTIVE;
        return true;
    }

    boolean cancel(String orderId) {
        return orders.remove(orderId) != null;
    }

    List<String> displayAllLiveOrders() {
        List<String> result = new ArrayList<>();
        for (Map.Entry<String, Order> e : orders.entrySet()) {
            String label = e.getKey() + (e.getValue().state == OrderState.PAUSED ? "(paused)" : "");
            result.add(label);
        }
        return result;
    }
}
```

**Example:**
```java
system.place("order1", "BTC", 10, 50000.0);
system.place("order2", "ETH", 100, 3000.0);
system.place("order3", "BTC", 5, 51000.0);
system.place("order4", "ETH", 50, 3100.0);
system.pause("order2");
system.pause("order3");
system.displayAllLiveOrders();
// ["order1", "order2(paused)", "order3(paused)", "order4"]
system.cancel("order2");
system.displayAllLiveOrders();
// ["order1", "order3(paused)", "order4"]
```

**Complexity:** All operations O(1) except displayAllLiveOrders O(N).

### Level 2

**Core Idea:** Add a `userOrders` index: `Map<String, Set<String>>`. Keep it consistent with `orders` on every mutation. `cancelAllByUser` iterates the set and removes from both structures.

**Key Decisions:** The secondary index must be updated in `cancel()` too — if single-order cancels don't maintain the user index, it will contain stale references and `cancelAllByUser` will fail silently or error.

```java
class Order {
    String orderId, userId, currency;
    double amount, price;
    OrderState state;

    Order(String orderId, String userId, String currency, double amount, double price) {
        this.orderId = orderId;
        this.userId = userId;
        this.currency = currency;
        this.amount = amount;
        this.price = price;
        this.state = OrderState.ACTIVE;
    }
}

class CryptoOrderSystem {
    private Map<String, Order> orders = new LinkedHashMap<>();
    private Map<String, Set<String>> userOrders = new HashMap<>(); // userId -> {orderId}

    void place(String orderId, String userId, String currency, double amount, double price) {
        if (orders.containsKey(orderId)) return;
        orders.put(orderId, new Order(orderId, userId, currency, amount, price));
        userOrders.computeIfAbsent(userId, k -> new HashSet<>()).add(orderId);
    }

    boolean cancel(String orderId) {
        Order order = orders.remove(orderId);
        if (order == null) return false;
        Set<String> userSet = userOrders.get(order.userId);
        if (userSet != null) {
            userSet.remove(orderId);
            if (userSet.isEmpty()) userOrders.remove(order.userId);
        }
        return true;
    }

    int cancelAllByUser(String userId) {
        Set<String> ids = userOrders.remove(userId);
        if (ids == null) return 0;
        for (String orderId : ids) orders.remove(orderId);
        return ids.size();
    }

    // pause() and resume() unchanged
}
```

**Complexity:** cancelAllByUser O(K) where K = orders for that user. All other operations unchanged.

### Level 3

**Core Idea:** Create `numStreams` independent `StreamOrderSystem` instances (Level 2). Route each user to `streams[hash(userId) % numStreams]`. All single-order operations route to the correct stream. `displayAllLiveOrders` aggregates across all streams.

**Key Decisions:** Sharding by `userId` (not `orderId`) is critical so that `cancelAllByUser` only touches one stream. If sharded by `orderId`, a user's orders would scatter, requiring a full cross-stream scan for bulk cancel.

```java
class CryptoOrderSystem {
    private final int numStreams;
    private final StreamOrderSystem[] streams;

    CryptoOrderSystem(int numStreams) {
        this.numStreams = numStreams;
        this.streams = new StreamOrderSystem[numStreams];
        for (int i = 0; i < numStreams; i++) streams[i] = new StreamOrderSystem();
    }

    private StreamOrderSystem stream(String userId) {
        return streams[Math.floorMod(userId.hashCode(), numStreams)];
    }

    void place(String orderId, String userId, String currency, double amount, double price) {
        stream(userId).place(orderId, userId, currency, amount, price);
    }

    boolean pause(String orderId, String userId) {
        return stream(userId).pause(orderId);
    }

    boolean resume(String orderId, String userId) {
        return stream(userId).resume(orderId);
    }

    boolean cancel(String orderId, String userId) {
        return stream(userId).cancel(orderId);
    }

    int cancelAllByUser(String userId) {
        return stream(userId).cancelAllByUser(userId);
    }

    List<String> displayAllLiveOrders() {
        List<String> result = new ArrayList<>();
        for (StreamOrderSystem s : streams) result.addAll(s.displayAllLiveOrders());
        return result;
    }
}

// StreamOrderSystem is the Level 2 implementation
```

**Complexity:** All routed operations remain O(1) or O(K). displayAllLiveOrders is O(N) across all streams, but parallelizable.

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Thread safety:** In a concurrent environment, each stream needs its own lock. Locking at the stream level (not the whole system) allows streams to operate in parallel — this is the key benefit of the sharded design. Use `ReentrantLock` per stream.
- **Consistent hashing:** `hash(userId) % N` breaks when `N` changes — nearly all users reroute to a different stream. Consistent hashing (e.g., using a virtual node ring) minimizes user movement when streams are added/removed.
- **Cross-stream display ordering:** `displayAllLiveOrders` with multiple streams loses global insertion order. If total order is required, include a sequence number in each order and merge-sort on display.
- **Single-order cancel without user_id:** In Level 3, `cancel(orderId)` requires knowing `userId` to route to the right stream. If only `orderId` is known, you need a global order→user index or broadcast to all streams. Ask the interviewer which access pattern they expect.
- **Persistence:** In production, each stream would correspond to a Kafka partition or a DB shard, not an in-memory map. Crash recovery via Kafka offset replay or DB WAL.

### Common Interview Traps

- **Forgetting to update `userOrders` in single `cancel()`:** The most common Level 2 bug. Results in stale entries in the user index, making `cancelAllByUser` undercounting.
- **Sharding by order_id instead of user_id:** Conceptually simpler but makes `cancelAllByUser` O(N) across all streams. The interviewer is specifically testing whether you reason about which access pattern to optimize for.
- **`displayAllLiveOrders` ordering across streams:** The aggregated display is not globally ordered unless you add a sequence counter. Most candidates don't notice this.
- **`pause()` / `resume()` in Level 3:** The spec doesn't give `userId` for these in Level 3. Either the interface must change to include it, or you maintain a global `orderId → streamIdx` index. Worth raising before coding.

### How to Push Forward as Staff+

- Propose per-stream locks immediately when discussing Level 3: "Each stream can be its own goroutine/thread with its own lock — this gives us parallelism without a global bottleneck."
- Ask about rebalancing: "If a new stream is added, do we need to migrate existing orders? Consistent hashing avoids most of the migration but we'd still need a brief dual-read period."
- Connect to Coinbase's real architecture: Coinbase's matching engine is partitioned by trading pair (BTC-USD, ETH-USD). Orders for the same symbol go to the same partition, which is equivalent to sharding by `symbol` instead of `userId`. Ask whether the product requirement favors user-centric or symbol-centric sharding.
- Raise the `displayAllLiveOrders` latency concern: "In production, a cross-shard scan for display purposes would be too slow for a live UI. We'd maintain a separate read model (e.g., a denormalized view in Redis or Elasticsearch) that aggregates order state asynchronously."
