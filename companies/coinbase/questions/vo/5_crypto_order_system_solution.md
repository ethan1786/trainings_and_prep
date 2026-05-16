## Summary

Crypto order management with state machine (active/paused/cancelled), user-scoped operations, and multi-stream sharding. 3 levels: order lifecycle → user index + bulk cancel → shard by userId hash.

## Design

**Data model:** State machine on `Order` object (ACTIVE ↔ PAUSED, both → cancel). LinkedHashMap preserves insertion order for display. Shard wrapper delegates to independent per-shard systems.

**Maps / structures:**
- `orders`: LinkedHashMap<orderId → Order> (insertion order preserved)
- `userOrders`: userId → Set<orderId> (secondary index for bulk cancel)
- `shards[]`: array of independent ShardedCryptoOrderSystem instances (Level 3)

**Key pattern:** Dual-map consistency — every mutation (`place`, `cancel`, `cancelAllByUser`) must update BOTH `orders` and `userOrders`. Same pattern as cloud_file_system's `storageByUser`.

**Gotchas under pressure:**
- `cancel()` must remove from BOTH maps — forgetting `userOrders` cleanup leaves stale entries
- `cancelAllByUser` iterates user's set then removes from `orders` — do NOT call `cancel()` inside the loop, as it modifies the set being iterated (ConcurrentModificationException)
- Sharding: `Math.floorMod(userId.hashCode(), size)` not `%` — hashCode can be negative
- `displayAllLiveOrders` across shards loses global insertion order — mention as a tradeoff, don't implement unless asked
- `pause`/`resume` in Level 3 need userId for routing — either change the API or add a global orderId → shardIdx index

---

```java
class CryptoOrderSystem {
    private ShardedCryptoOrderSystem[] shards;
    private int size;

    CryptoOrderSystem(int numStreams) {
        shards = new ShardedCryptoOrderSystem[numStreams];
        size = numStreams;
        for (int i = 0; i < numStreams; i++) {
            shards[i] = new ShardedCryptoOrderSystem();
        }
    }

    ShardedCryptoOrderSystem getShard(String userId) {
        int index = Math.floorMod(userId.hashCode(), size);
        return shards[index];
    }

    void place(String orderId, String userId, String currency, double amount, double price) {
        ShardedCryptoOrderSystem shard = getShard(userId);
        shard.place(orderId, userId, currency, amount, price);
    }

    boolean pause(String orderId, String userId) {
        ShardedCryptoOrderSystem shard = getShard(userId);
        return shard.pause(orderId);
    }

    boolean resume(String orderId, String userId) {
        ShardedCryptoOrderSystem shard = getShard(userId);
        return shard.resume(orderId);
    }

    boolean cancel(String orderId, String userId) {
        ShardedCryptoOrderSystem shard = getShard(userId);
        return shard.cancel(orderId);
    }

    List<String> displayAllLiveOrders() {
        List<String> result = new ArrayList<>();
        for (ShardedCryptoOrderSystem s: shards) {
            result.addAll(s.displayAllLiveOrders());
        }
        return result;
    }

    int cancelAllByUser(String userId) {
        ShardedCryptoOrderSystem shard = getShard(userId);
        return shard.cancelAllByUser(userId);
    }

    private static class ShardedCryptoOrderSystem {
        private Map<String, Order> orders = new LinkedHashMap<>();
        private Map<String, Set<String>> userOrders = new HashMap<>();

        // Distribute orders across numStreams shards.
        // Routing: hash(userId) % numStreams.
        // All orders for a user go to the same stream.
        // displayAllLiveOrders() aggregates across all streams.

        void place(String orderId, String userId, String currency, double amount, double price) {
            if (orders.containsKey(orderId)) {
                return;
            }
            Order o = new Order(orderId, userId, currency, amount, price);
            orders.put(orderId, o);
            userOrders.computeIfAbsent(userId, k -> new HashSet<>()).add(orderId);
        }
        // Add order in ACTIVE state. Ignore if orderId already exists.

        boolean pause(String orderId) {
            if (!orders.containsKey(orderId)) {
                return false;
            }
            Order o = orders.get(orderId);
            return o.pause();
        }
        // ACTIVE → PAUSED. False if missing or not ACTIVE.

        boolean resume(String orderId) {
            if (!orders.containsKey(orderId)) {
                return false;
            }
            Order o = orders.get(orderId);
            return o.resume();
        }
        // PAUSED → ACTIVE. False if missing or not PAUSED.

        boolean cancel(String orderId) {
            if (!orders.containsKey(orderId)) {
                return false;
            }
            Order o = orders.remove(orderId);
            userOrders.get(o.userId).remove(orderId);
            if (userOrders.get(o.userId).isEmpty()) {
                userOrders.remove(o.userId);
            }
            return true;
        }
        // Remove order. True for both ACTIVE and PAUSED. False if missing.

        List<String> displayAllLiveOrders() {
            return orders.entrySet().stream()
                    .map(entry -> {
                        if (entry.getValue().status == OrderStatus.ACTIVE) {
                            return entry.getKey();
                        } else {
                            return entry.getKey() + "(paused)";
                        }
                    })
                    .toList();
        }
        // Return all non-cancelled orders in insertion order.
        // Format: ["order1", "order2(paused)", "order3"]
        // Paused orders get "(paused)" suffix.

        int cancelAllByUser(String userId) {
            Set<String> orderIds = userOrders.getOrDefault(userId, Set.of());
            for (String id : orderIds) {
                orders.remove(id);
            }
            userOrders.remove(userId);
            return orderIds.size();
        }
        // Cancel all orders for user. Returns count cancelled. Cleans up user index.

        private static class Order {
            String orderId;
            String userId;
            String currency;
            double amount;
            double price;
            OrderStatus status;

            Order(String id, String u, String c, double a, double p) {
                orderId = id;
                userId = u;
                currency = c;
                amount = a;
                price = p;
                status = OrderStatus.ACTIVE;
            }

            boolean pause() {
                if (status != OrderStatus.ACTIVE) {
                    return false;
                }
                status = OrderStatus.PAUSED;
                return true;
            }

            boolean resume() {
                if (status != OrderStatus.PAUSED) {
                    return false;
                }
                status = OrderStatus.ACTIVE;
                return true;
            }
        }

        enum OrderStatus {
            ACTIVE, PAUSED;
        }
    }
}