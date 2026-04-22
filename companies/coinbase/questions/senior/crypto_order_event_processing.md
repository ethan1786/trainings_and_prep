# Crypto Order Event Processing

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 45 min
**Key Topics:** State Machine, Event Processing, Kafka, HashMap, Idempotency

---

## Problem Statement

You are building a Coinbase order management system. The system broadcasts events to a Kafka topic whenever an order is placed or a trade executes (fully or partially). Your processor reads these events and maintains the current state of every order.

Orders transition through states: `NEW → IN_PROGRESS → COMPLETED` (or `NEW → CANCELLED`).

Each Kafka message has the format: `orderId, operation, symbol, quantity, orderType`

Example: `"1234, BUY, BTC, 10, NEW"`

## Requirements

### Level 1: Basic Order Tracking

```java
class OrderEventProcessor {
    void consumeMessages(List<String> messages);
    // Process a batch of Kafka messages.
    // Message format: "orderId, operation, symbol, quantity, orderType"
    // orderType is one of: NEW, FILLED

    String getOrderStatus(String orderId);
    // Returns: "NEW" | "IN_PROGRESS" | "COMPLETED" | "NOT_FOUND"
    //
    // Status rules:
    //   NEW         — order placed, no fills yet
    //   IN_PROGRESS — partially filled (filledQty < totalQty)
    //   COMPLETED   — fully filled (filledQty >= totalQty)
}
```

### Level 2: Cancellations

Add support for `CANCEL` events. A cancel only succeeds if the order has not been partially or fully filled. Cancelled orders remain queryable.

```java
// Additional orderType: CANCEL
// New status: "CANCELLED"
// Rule: only orders in NEW state can be cancelled.
```

---

## Solution Approach

### Level 1

**Core Idea:** Maintain a `Map<String, Order>`. `Order` encapsulates all state and fill logic. Status is computed from `filledQty` vs `totalQty`.

**Data Structures:** Single HashMap; O(1) lookup for status queries.

```java
enum OrderStatus { NEW, IN_PROGRESS, COMPLETED }

class Order {
    String orderId, operation, symbol;
    int totalQty, filledQty;
    OrderStatus status;

    Order(String orderId, String operation, String symbol, int totalQty) {
        this.orderId = orderId;
        this.operation = operation;
        this.symbol = symbol;
        this.totalQty = totalQty;
        this.filledQty = 0;
        this.status = OrderStatus.NEW;
    }

    void fill(int quantity) {
        filledQty += quantity;
        status = filledQty >= totalQty ? OrderStatus.COMPLETED : OrderStatus.IN_PROGRESS;
    }
}

class OrderEventProcessor {
    private Map<String, Order> orders = new HashMap<>();

    void consumeMessages(List<String> messages) {
        for (String msg : messages) {
            String[] parts = Arrays.stream(msg.split(","))
                .map(String::trim).toArray(String[]::new);
            String orderId = parts[0], operation = parts[1], symbol = parts[2];
            int quantity = Integer.parseInt(parts[3]);
            String orderType = parts[4];

            if (orderType.equals("NEW")) {
                orders.put(orderId, new Order(orderId, operation, symbol, quantity));
            } else if (orderType.equals("FILLED") && orders.containsKey(orderId)) {
                orders.get(orderId).fill(quantity);
            }
        }
    }

    String getOrderStatus(String orderId) {
        Order order = orders.get(orderId);
        return order == null ? "NOT_FOUND" : order.status.name();
    }
}
```

**Example trace:**
```
"1234, BUY, BTC, 10, NEW"    → order 1234, total=10, filled=0, status=NEW
"1234, BUY, BTC, 5, FILLED"  → filled=5,  status=IN_PROGRESS
"1234, BUY, BTC, 3, FILLED"  → filled=8,  status=IN_PROGRESS
"1234, BUY, BTC, 2, FILLED"  → filled=10, status=COMPLETED

getOrderStatus("0000")  → "NEW"         (no fills)
getOrderStatus("1234")  → "COMPLETED"
getOrderStatus("1111")  → "IN_PROGRESS" (filled 5 of 10)
getOrderStatus("9999")  → "NOT_FOUND"
```

**Complexity:** consumeMessages O(M), getOrderStatus O(1). M = messages in batch, N = unique orders in memory.

### Level 2

**Core Idea:** Add `CANCELLED` state. Cancel is only allowed from `NEW` — this is the critical guard. The `cancel()` method on `Order` encapsulates the guard rather than putting it in the processor.

**Key Decisions:** Status check inside `Order.cancel()` keeps the state machine logic co-located with the state. The processor stays a thin dispatcher.

```java
enum OrderStatus { NEW, IN_PROGRESS, COMPLETED, CANCELLED }

class Order {
    // ... same fields and constructor as Level 1 ...

    void fill(int quantity) {
        filledQty += quantity;
        status = filledQty >= totalQty ? OrderStatus.COMPLETED : OrderStatus.IN_PROGRESS;
    }

    boolean cancel() {
        if (status == OrderStatus.NEW) {
            status = OrderStatus.CANCELLED;
            return true;
        }
        return false; // Cannot cancel IN_PROGRESS or COMPLETED orders
    }
}

class OrderEventProcessor {
    private Map<String, Order> orders = new HashMap<>();

    void consumeMessages(List<String> messages) {
        for (String msg : messages) {
            String[] parts = Arrays.stream(msg.split(","))
                .map(String::trim).toArray(String[]::new);
            String orderId = parts[0], operation = parts[1], symbol = parts[2];
            int quantity = Integer.parseInt(parts[3]);
            String orderType = parts[4];

            if (orderType.equals("NEW")) {
                orders.put(orderId, new Order(orderId, operation, symbol, quantity));
            } else if (orderType.equals("FILLED") && orders.containsKey(orderId)) {
                orders.get(orderId).fill(quantity);
            } else if (orderType.equals("CANCEL") && orders.containsKey(orderId)) {
                orders.get(orderId).cancel(); // Silently ignored if not cancellable
            }
        }
    }

    String getOrderStatus(String orderId) {
        Order order = orders.get(orderId);
        return order == null ? "NOT_FOUND" : order.status.name();
    }
}
```

**Cancel example trace:**
```
"1234, BUY, BTC, 10, NEW"
"1234, BUY, BTC, 5, FILLED"   → IN_PROGRESS
"1234, BUY, BTC, 10, CANCEL"  → cancel() returns false (IN_PROGRESS), status unchanged

"5678, SELL, BTC, 20, NEW"
"5678, SELL, BTC, 20, CANCEL" → cancel() returns true (NEW → CANCELLED)

getOrderStatus("1234") → "IN_PROGRESS"
getOrderStatus("5678") → "CANCELLED"
```

**Complexity:** consumeMessages O(M), getOrderStatus O(1). Unchanged from Level 1.

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Idempotency / duplicate messages:** Kafka provides at-least-once delivery. The same `FILLED` event could arrive twice, causing double-counting of `filled_qty`. Fix: track processed message offsets (or event IDs), and deduplicate before applying fills.
- **Out-of-order delivery:** A `FILLED` arriving before its `NEW` (e.g., cross-partition ordering). Options: buffer `FILLED` events and retry when the `NEW` arrives; use Kafka partition key = `orderId` to guarantee ordering within a partition.
- **Overfill guard:** What if cumulative `FILLED` quantities exceed `total_qty`? The current code allows `filled_qty > total_qty`. Production systems should clamp or alert on this.
- **Persistence / crash recovery:** The in-memory `orders` dict is lost on restart. In production: commit Kafka consumer offsets only after writing to a durable store (e.g., a DB), enabling replay-based recovery. Alternatively, snapshot state periodically and replay from the last snapshot offset.
- **Scaling:** Partition the Kafka topic by `orderId`. Each partition is consumed by one worker. This gives horizontal scale while preserving per-order message ordering.

### Common Interview Traps

- **Cancel guard placement:** The spec says "only cancel if no fills" — some candidates check `filled_qty == 0` instead of `status == NEW`. These are equivalent here but `status` is more robust if the state machine grows (e.g., a NEW order with zero fills might be in a different sub-state).
- **NEW message for existing ID:** The current code silently overwrites an existing order if a second `NEW` arrives. Ask the interviewer whether this should be rejected.
- **FILLED with no preceding NEW:** The guard `if order_id in self.orders` handles this but it's worth calling out explicitly.
- **`quantity` field on CANCEL:** The message still carries a quantity field for CANCEL events, but it's irrelevant. Don't use it for any cancel logic.

### How to Push Forward as Staff+

- Raise the offset vs. cursor trade-off unprompted: "At the bottom of the `order_manager_system` notes there's a mention of 'offset vs cursor' — in Kafka, committing offsets after DB writes gives at-least-once with idempotent processing. A cursor-based approach (pointer in DB) gives exactly-once but requires a two-phase commit. Which does Coinbase prefer here?"
- Propose a more robust state machine: define valid transitions explicitly (`{NEW: [IN_PROGRESS, CANCELLED], IN_PROGRESS: [COMPLETED], COMPLETED: [], CANCELLED: []}`) and reject invalid transitions rather than silently ignoring them.
- Connect to Coinbase's matching engine: in production, a Coinbase order has more states (PENDING, OPEN, DONE with done_reason: filled/cancelled/expired). Ask whether the interviewer wants the simplified model or something closer to the real Coinbase Advanced Trade API schema.
- Discuss the `consumed_qty` vs `filled_qty` distinction: Coinbase's actual API distinguishes between `filled_size` (already executed) and `leaves_qty` (remaining open). Over-delivery handling is a real compliance concern.
