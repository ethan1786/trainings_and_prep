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

```python
class OrderEventProcessor:
    def consume_messages(self, messages: list[str]) -> None:
        """
        Process a batch of Kafka messages.
        Message format: "orderId, operation, symbol, quantity, orderType"
        orderType is one of: NEW, FILLED
        """

    def get_order_status(self, order_id: str) -> str:
        """
        Returns: "NEW" | "IN_PROGRESS" | "COMPLETED" | "NOT_FOUND"
        
        Status rules:
          NEW        — order placed, no fills yet
          IN_PROGRESS — partially filled (filled_qty < total_qty)
          COMPLETED  — fully filled (filled_qty >= total_qty)
        """
```

### Level 2: Cancellations

Add support for `CANCEL` events. A cancel only succeeds if the order has not been partially or fully filled. Cancelled orders remain queryable.

```python
# Additional orderType: CANCEL
# New status: "CANCELLED"
# Rule: only orders in NEW state can be cancelled.
```

---

## Solution Approach

### Level 1

**Core Idea:** Maintain a `dict[order_id -> Order]`. `Order` encapsulates all state and fill logic. Status is computed from `filled_quantity` vs `total_quantity`.

**Data Structures:** Single HashMap; O(1) lookup for status queries.

```python
from enum import Enum

class OrderStatus(Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class Order:
    def __init__(self, order_id: str, operation: str, symbol: str, total_qty: int):
        self.order_id = order_id
        self.operation = operation
        self.symbol = symbol
        self.total_qty = total_qty
        self.filled_qty = 0
        self.status = OrderStatus.NEW

    def fill(self, quantity: int) -> None:
        self.filled_qty += quantity
        self.status = (
            OrderStatus.COMPLETED if self.filled_qty >= self.total_qty
            else OrderStatus.IN_PROGRESS
        )

class OrderEventProcessor:
    def __init__(self):
        self.orders: dict[str, Order] = {}

    def consume_messages(self, messages: list[str]) -> None:
        for msg in messages:
            parts = [p.strip() for p in msg.split(",")]
            order_id, operation, symbol = parts[0], parts[1], parts[2]
            quantity, order_type = int(parts[3]), parts[4]

            if order_type == "NEW":
                self.orders[order_id] = Order(order_id, operation, symbol, quantity)
            elif order_type == "FILLED" and order_id in self.orders:
                self.orders[order_id].fill(quantity)

    def get_order_status(self, order_id: str) -> str:
        if order_id not in self.orders:
            return "NOT_FOUND"
        return self.orders[order_id].status.value
```

**Example trace:**
```
"1234, BUY, BTC, 10, NEW"    → order 1234, total=10, filled=0, status=NEW
"1234, BUY, BTC, 5, FILLED"  → filled=5,  status=IN_PROGRESS
"1234, BUY, BTC, 3, FILLED"  → filled=8,  status=IN_PROGRESS
"1234, BUY, BTC, 2, FILLED"  → filled=10, status=COMPLETED

get_order_status("0000")  → "NEW"       (no fills)
get_order_status("1234")  → "COMPLETED"
get_order_status("1111")  → "IN_PROGRESS" (filled 5 of 10)
get_order_status("9999")  → "NOT_FOUND"
```

**Complexity:** consume_messages O(M), get_order_status O(1). M = messages in batch, N = unique orders in memory.

### Level 2

**Core Idea:** Add `CANCELLED` state. Cancel is only allowed from `NEW` — this is the critical guard. The `cancel()` method on `Order` encapsulates the guard rather than putting it in the processor.

**Key Decisions:** Status check inside `Order.cancel()` keeps the state machine logic co-located with the state. The processor stays a thin dispatcher.

```python
from enum import Enum

class OrderStatus(Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Order:
    # ... same __init__ and fill() as Level 1 ...

    def cancel(self) -> bool:
        if self.status == OrderStatus.NEW:
            self.status = OrderStatus.CANCELLED
            return True
        return False  # Cannot cancel IN_PROGRESS or COMPLETED orders

class OrderEventProcessor:
    def __init__(self):
        self.orders: dict[str, Order] = {}

    def consume_messages(self, messages: list[str]) -> None:
        for msg in messages:
            parts = [p.strip() for p in msg.split(",")]
            order_id, operation, symbol = parts[0], parts[1], parts[2]
            quantity, order_type = int(parts[3]), parts[4]

            if order_type == "NEW":
                self.orders[order_id] = Order(order_id, operation, symbol, quantity)
            elif order_type == "FILLED" and order_id in self.orders:
                self.orders[order_id].fill(quantity)
            elif order_type == "CANCEL" and order_id in self.orders:
                self.orders[order_id].cancel()  # Silently ignored if not cancellable

    def get_order_status(self, order_id: str) -> str:
        if order_id not in self.orders:
            return "NOT_FOUND"
        return self.orders[order_id].status.value
```

**Cancel example trace:**
```
"1234, BUY, BTC, 10, NEW"
"1234, BUY, BTC, 5, FILLED"   → IN_PROGRESS
"1234, BUY, BTC, 10, CANCEL"  → cancel() returns False (IN_PROGRESS), status unchanged

"5678, SELL, BTC, 20, NEW"
"5678, SELL, BTC, 20, CANCEL" → cancel() returns True (NEW → CANCELLED)

get_order_status("1234") → "IN_PROGRESS"
get_order_status("5678") → "CANCELLED"
```

**Complexity:** consume_messages O(M), get_order_status O(1). Unchanged from Level 1.

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
