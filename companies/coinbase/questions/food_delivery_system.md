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
```java
class FoodDeliverySystem {
    FoodDeliverySystem(double userX, double userY,
                       List<int[]> restaurants,   // {id, x, y}
                       List<Object[]> menu) {}    // {restaurantId, itemName, price}

    int[] findCheapest(String itemName) {...}     // returns {restaurantId, price} or null
    double[] findNearest(String itemName) {...}   // returns {restaurantId, distance} or null
}
```

### Level 2: Order Analytics
```java
void loadOrders(List<int[]> orders) {}
// orders: list of {orderId, itemId, totalPrice, timestamp}
// Multiple line items can share an orderId

double[] getOrderAnalytics(int start, int end) {}
// Returns {orderCount, totalRevenue, avgOrderValue} for [start, end]
```

### Level 3: Top-K Orders
```java
List<long[]> topKOrders(int start, int end, int k) {}
// Returns top K {orderId, revenue} pairs sorted by revenue desc
```

### Level 4: Top-K Items
```java
List<double[]> topKItems(int start, int end, int k) {}
// Returns top K {itemId, totalSalesVolume} pairs sorted by volume desc
```

---

## Solution Approach

### Level 1
**Core Idea:** Preprocess menu into an item -> [(restaurant_id, price)] index at construction time. Both queries are linear scans over that list.

**Data Structures:**
- `restaurantCoords: Map<Integer, double[]>` — O(1) distance lookup
- `itemToRestaurants: Map<String, List<int[]>>` — per-item candidate list

```java
import java.util.*;

class FoodDeliverySystem {
    private final double userX, userY;
    private final Map<Integer, double[]> restaurantCoords = new HashMap<>();
    private final Map<String, List<int[]>> itemToRestaurants = new HashMap<>();

    FoodDeliverySystem(double userX, double userY,
                       List<int[]> restaurants, List<Object[]> menu) {
        this.userX = userX;
        this.userY = userY;
        for (int[] r : restaurants) {
            restaurantCoords.put(r[0], new double[]{r[1], r[2]});
        }
        for (Object[] entry : menu) {
            int rId = (int) entry[0];
            String item = (String) entry[1];
            int price = (int) entry[2];
            itemToRestaurants.computeIfAbsent(item, k -> new ArrayList<>())
                             .add(new int[]{rId, price});
        }
    }

    private double distance(int rId) {
        double[] coords = restaurantCoords.get(rId);
        return Math.sqrt(Math.pow(coords[0] - userX, 2) + Math.pow(coords[1] - userY, 2));
    }

    int[] findCheapest(String itemName) {
        List<int[]> entries = itemToRestaurants.get(itemName);
        if (entries == null) return null;
        return entries.stream().min(Comparator.comparingInt(e -> e[1])).orElse(null);
    }

    double[] findNearest(String itemName) {
        List<int[]> entries = itemToRestaurants.get(itemName);
        if (entries == null) return null;
        int[] best = entries.stream()
            .min(Comparator.comparingDouble(e -> distance(e[0]))).orElse(null);
        return best == null ? null : new double[]{best[0], distance(best[0])};
    }
}
```

**Complexity:** O(M) init, O(K) per query — M = menu size, K = restaurants per item

### Level 2
**Core Idea:** Aggregate line items into per-order totals using a map. Range queries scan all orders.

```java
private Map<Integer, long[]> orders;   // orderId -> {timestamp, totalPrice * 100}
private List<int[]> lineItems;         // {orderId, itemId, price, timestamp}

void loadOrders(List<int[]> rawOrders) {
    this.lineItems = rawOrders;
    this.orders = new HashMap<>();
    for (int[] row : rawOrders) {
        int orderId = row[0], ts = row[3];
        long price = row[2];
        orders.merge(orderId, new long[]{ts, price},
                     (existing, val) -> { existing[1] += val[1]; return existing; });
    }
}

double[] getOrderAnalytics(int start, int end) {
    int count = 0;
    double revenue = 0;
    for (long[] data : orders.values()) {
        if (data[0] >= start && data[0] <= end) {
            count++;
            revenue += data[1];
        }
    }
    double avg = count > 0 ? revenue / count : 0.0;
    return new double[]{count, revenue, avg};
}
```

**Complexity:** O(L) load, O(N) query — L = line items, N = unique orders

### Level 3
**Core Idea:** Min-heap of size K. When heap is full and current order beats the minimum, replace it. Avoids sorting all N orders.

```java
List<long[]> topKOrders(int start, int end, int k) {
    // Min-heap keyed on revenue
    PriorityQueue<long[]> heap = new PriorityQueue<>(Comparator.comparingLong(e -> e[1]));
    for (Map.Entry<Integer, long[]> entry : orders.entrySet()) {
        long[] data = entry.getValue();
        if (data[0] < start || data[0] > end) continue;
        long[] candidate = {entry.getKey(), data[1]};
        if (heap.size() < k) {
            heap.offer(candidate);
        } else if (data[1] > heap.peek()[1]) {
            heap.poll();
            heap.offer(candidate);
        }
    }
    List<long[]> result = new ArrayList<>(heap);
    result.sort((a, b) -> Long.compare(b[1], a[1]));
    return result;
}
```

**Complexity:** O(N log K) time, O(K) space

### Level 4
**Core Idea:** Scan raw line items to aggregate per-item volume, then apply the same top-K heap pattern.

```java
List<double[]> topKItems(int start, int end, int k) {
    Map<Integer, Double> itemVolume = new HashMap<>();
    for (int[] row : lineItems) {
        if (row[3] >= start && row[3] <= end) {
            itemVolume.merge(row[1], (double) row[2], Double::sum);
        }
    }

    PriorityQueue<double[]> heap = new PriorityQueue<>(Comparator.comparingDouble(e -> e[1]));
    for (Map.Entry<Integer, Double> entry : itemVolume.entrySet()) {
        double[] candidate = {entry.getKey(), entry.getValue()};
        if (heap.size() < k) {
            heap.offer(candidate);
        } else if (entry.getValue() > heap.peek()[1]) {
            heap.poll();
            heap.offer(candidate);
        }
    }
    List<double[]> result = new ArrayList<>(heap);
    result.sort((a, b) -> Double.compare(b[1], a[1]));
    return result;
}
```

**Complexity:** O(L + I log K) time, O(I) space — I = distinct items in range

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Concurrency:** `loadOrders` replaces the entire `orders` map — concurrent reads mid-swap will see stale or partial data. Use a read-write lock or swap atomically with a reference replace.
- **Analytics at scale:** O(N) scans per query don't scale to millions of orders. Sort orders by timestamp on load, then use binary search to narrow the window. Or use a sorted structure like a SortedList (from `sortedcontainers`).
- **Streaming orders:** Real systems get orders as a stream. Maintain a sorted list or time-partitioned structure that supports O(log N) inserts and O(log N + K) range queries.
- **Geo queries:** Euclidean distance doesn't scale. Production would use a spatial index (R-tree, geohash, PostGIS) for nearest-neighbor lookups.
- **Price volatility:** Menu prices change. If prices are cached at init time, find_cheapest will return stale results. Design for invalidation or reindexing.

### Common Interview Traps
- **Order aggregation:** The input has multiple line items per order_id. Forgetting to aggregate by order_id makes order_count wrong in `getOrderAnalytics`.
- **Top-K sort direction:** The heap returns smallest-first by default. Easy to return the list in the wrong order.
- **Tie-breaking in findCheapest/findNearest:** If two restaurants have the same price or distance, which wins? Clarify with the interviewer.
- **`loadOrders` idempotency:** Should calling `loadOrders` twice append or replace? The naive implementation replaces — make this explicit.

### How to Push Forward as Staff+
- **Proactively flag the O(N) scan:** "For an analytics query in production, I'd sort orders by timestamp at load time so range queries are O(log N + K). I'll implement the simple version first to get correctness."
- **Mention keyset pagination:** If the interviewer adds "return results page by page," this is a natural connection to cursor-based pagination over the sorted order list.
- **Connect to Coinbase domain:** This is directly analogous to Coinbase's transaction history queries — user asks for all BTC trades between two timestamps. Same time-range query pattern, same pagination concerns, same currency/pair filtering.
- **Knapsack variant:** If the interviewer asks "given a budget, what's the best meal combination?", name it as the 0/1 knapsack problem. Mention it's NP-hard in general, but tractable with small item counts.
- **Offline vs. real-time analytics:** "If queries are frequent, I'd consider materializing aggregates (e.g., hourly revenue buckets) so range queries become prefix-sum lookups — O(1) per query after O(N) preprocessing."
