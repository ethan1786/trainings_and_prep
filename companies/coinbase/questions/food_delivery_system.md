# Food Delivery System

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 45-60 min
**Key Topics:** HashMap, Min-Heap, Euclidean Distance, Top-K, Time-Range Queries

---

## Problem Statement

Build an in-memory food delivery system that manages restaurants, menus, and orders. The system should support finding the cheapest or nearest restaurant for a given item, querying order analytics over time windows, and ranking top orders or items by revenue.

## Requirements

### Level 1: Find Food
```python
class FoodDeliverySystem:
    def __init__(self, user_x: float, user_y: float,
                 restaurants: list[tuple[int, float, float]],
                 menu: list[tuple[int, str, float]]): ...

    def find_cheapest(self, item_name: str) -> tuple[int, float] | None: ...
    # Returns (restaurant_id, price) or None

    def find_nearest(self, item_name: str) -> tuple[int, float] | None: ...
    # Returns (restaurant_id, distance) using Euclidean distance, or None
```

### Level 2: Order Analytics
```python
def load_orders(self, orders: list[tuple[int, int, float, int]]) -> None: ...
# orders: list of (order_id, item_id, total_price, timestamp)
# Multiple line items can share an order_id

def get_order_analytics(self, start: int, end: int) -> tuple[int, float, float]: ...
# Returns (order_count, total_revenue, avg_order_value) for [start, end]
```

### Level 3: Top-K Orders
```python
def top_k_orders(self, start: int, end: int, k: int) -> list[tuple[int, float]]: ...
# Returns top K (order_id, revenue) pairs sorted by revenue desc
```

### Level 4: Top-K Items
```python
def top_k_items(self, start: int, end: int, k: int) -> list[tuple[int, float]]: ...
# Returns top K (item_id, total_sales_volume) pairs sorted by volume desc
```

---

## Solution Approach

### Level 1
**Core Idea:** Preprocess menu into an item -> [(restaurant_id, price)] index at construction time. Both queries are linear scans over that list.

**Data Structures:**
- `restaurant_coords: dict[int, (float, float)]` — O(1) distance lookup
- `item_to_restaurants: dict[str, list[(int, float)]]` — per-item candidate list

```python
import math

class FoodDeliverySystem:
    def __init__(self, user_x, user_y, restaurants, menu):
        self.user_x = user_x
        self.user_y = user_y
        self.restaurant_coords = {r_id: (x, y) for r_id, x, y in restaurants}
        self.item_to_restaurants = {}
        for r_id, item_name, price in menu:
            self.item_to_restaurants.setdefault(item_name, []).append((r_id, price))

    def _distance(self, r_id):
        x, y = self.restaurant_coords[r_id]
        return math.sqrt((x - self.user_x) ** 2 + (y - self.user_y) ** 2)

    def find_cheapest(self, item_name):
        entries = self.item_to_restaurants.get(item_name)
        return min(entries, key=lambda e: e[1]) if entries else None

    def find_nearest(self, item_name):
        entries = self.item_to_restaurants.get(item_name)
        if not entries:
            return None
        best = min(entries, key=lambda e: self._distance(e[0]))
        return (best[0], self._distance(best[0]))
```

**Complexity:** O(M) init, O(K) per query — M = menu size, K = restaurants per item

### Level 2
**Core Idea:** Aggregate line items into per-order totals using a dict. Range queries scan all orders.

```python
def load_orders(self, orders):
    self.orders = {}
    self.line_items = orders  # keep raw for Level 4
    for order_id, item_id, price, ts in orders:
        if order_id not in self.orders:
            self.orders[order_id] = {"timestamp": ts, "total": 0.0}
        self.orders[order_id]["total"] += price

def get_order_analytics(self, start, end):
    count, revenue = 0, 0.0
    for data in self.orders.values():
        if start <= data["timestamp"] <= end:
            count += 1
            revenue += data["total"]
    avg = revenue / count if count else 0.0
    return (count, revenue, avg)
```

**Complexity:** O(L) load, O(N) query — L = line items, N = unique orders

### Level 3
**Core Idea:** Min-heap of size K. When heap is full and current order beats the minimum, replace it. Avoids sorting all N orders.

```python
import heapq

def top_k_orders(self, start, end, k):
    heap = []
    for order_id, data in self.orders.items():
        if start <= data["timestamp"] <= end:
            if len(heap) < k:
                heapq.heappush(heap, (data["total"], order_id))
            elif data["total"] > heap[0][0]:
                heapq.heapreplace(heap, (data["total"], order_id))
    return sorted([(oid, t) for t, oid in heap], key=lambda x: -x[1])
```

**Complexity:** O(N log K) time, O(K) space

### Level 4
**Core Idea:** Scan raw line items to aggregate per-item volume, then apply the same top-K heap pattern.

```python
from collections import defaultdict

def top_k_items(self, start, end, k):
    item_volume = defaultdict(float)
    for order_id, item_id, price, ts in self.line_items:
        if start <= ts <= end:
            item_volume[item_id] += price

    heap = []
    for item_id, vol in item_volume.items():
        if len(heap) < k:
            heapq.heappush(heap, (vol, item_id))
        elif vol > heap[0][0]:
            heapq.heapreplace(heap, (vol, item_id))
    return sorted([(iid, v) for v, iid in heap], key=lambda x: -x[1])
```

**Complexity:** O(L + I log K) time, O(I) space — I = distinct items in range

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Concurrency:** `load_orders` replaces the entire `orders` dict — concurrent reads mid-swap will see stale or partial data. Use a read-write lock or swap atomically with a reference replace.
- **Analytics at scale:** O(N) scans per query don't scale to millions of orders. Sort orders by timestamp on load, then use binary search to narrow the window. Or use a sorted structure like a SortedList (from `sortedcontainers`).
- **Streaming orders:** Real systems get orders as a stream. Maintain a sorted list or time-partitioned structure that supports O(log N) inserts and O(log N + K) range queries.
- **Geo queries:** Euclidean distance doesn't scale. Production would use a spatial index (R-tree, geohash, PostGIS) for nearest-neighbor lookups.
- **Price volatility:** Menu prices change. If prices are cached at init time, find_cheapest will return stale results. Design for invalidation or reindexing.

### Common Interview Traps
- **Order aggregation:** The input has multiple line items per order_id. Forgetting to aggregate by order_id makes order_count wrong in `get_order_analytics`.
- **Top-K sort direction:** The heap returns smallest-first by default. Easy to return the list in the wrong order.
- **Tie-breaking in find_cheapest/find_nearest:** If two restaurants have the same price or distance, which wins? Clarify with the interviewer.
- **`load_orders` idempotency:** Should calling `load_orders` twice append or replace? The naive implementation replaces — make this explicit.

### How to Push Forward as Staff+
- **Proactively flag the O(N) scan:** "For an analytics query in production, I'd sort orders by timestamp at load time so range queries are O(log N + K). I'll implement the simple version first to get correctness."
- **Mention keyset pagination:** If the interviewer adds "return results page by page," this is a natural connection to cursor-based pagination over the sorted order list.
- **Connect to Coinbase domain:** This is directly analogous to Coinbase's transaction history queries — user asks for all BTC trades between two timestamps. Same time-range query pattern, same pagination concerns, same currency/pair filtering.
- **Knapsack variant:** If the interviewer asks "given a budget, what's the best meal combination?", name it as the 0/1 knapsack problem. Mention it's NP-hard in general, but tractable with small item counts.
- **Offline vs. real-time analytics:** "If queries are frequent, I'd consider materializing aggregates (e.g., hourly revenue buckets) so range queries become prefix-sum lookups — O(1) per query after O(N) preprocessing."
