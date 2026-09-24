# Calibration Session — 2026-09-23

**Purpose:** measure what survived the break, so we know which weeks of
`coding/study_plan.md` to redo vs. skim. Part A only — if it lands fast and clean,
a Hard (Part B) follows in the chat.

## Rules

- **45:00 total**, self-timed, for Part A. Clock starts when you read the problem.
- **No AI tools.** This one measures the raw baseline; AI-enabled drills come later.
- **Narrate out loud** — and type decision points into the notes section below as you
  go (requirements you clarify, API choices, edge cases, complexity). Narration is
  scored as much as the code.
- Language: **Java** — the only interview language from here on.
- Don't peek at `coding/problems/` or any solution files while solving.

## Part A — LC 1396 · Design Underground System (Medium)

Design a system that tracks customer travel time between train stations:

- `checkIn(id, stationName, t)` — customer `id` starts a trip at `stationName` at time `t`
- `checkOut(id, stationName, t)` — customer `id` finishes a trip at `stationName` at time `t`
- `getAverageTime(startStation, endStation)` — average travel time across all
  **completed** trips in that direction (start → end), as a `double`

Guarantees (from the problem statement):
- All calls happen in chronological order; `t` is always increasing per customer.
- Every `checkOut` matches a prior `checkIn`.
- `getAverageTime` is only called for station pairs that have ≥ 1 completed trip.
- At most 2×10^4 total calls.

### Examples

```
checkIn(45, "Leyton", 3);  checkIn(32, "Paradise", 8);  checkIn(27, "Leyton", 10);
checkOut(45, "Waterloo", 15);  checkOut(27, "Waterloo", 20);  checkOut(32, "Cambridge", 22);
getAverageTime("Paradise", "Cambridge")  → 14.00000   (one trip: 8 → 22)
getAverageTime("Leyton", "Waterloo")     → 11.00000   (two trips: 3→15, 10→20)
checkIn(10, "Leyton", 24);  getAverageTime("Leyton", "Waterloo") → 11.00000
checkOut(10, "Waterloo", 38);  getAverageTime("Leyton", "Waterloo") → 12.00000
```

```
checkIn(10, "Leyton", 3);  checkOut(10, "Paradise", 8);  getAverageTime("Leyton", "Paradise") → 5.00000
checkIn(5, "Leyton", 10);  checkOut(5, "Paradise", 16);  getAverageTime("Leyton", "Paradise") → 5.50000
checkIn(2, "Leyton", 21);  checkOut(2, "Paradise", 30);  getAverageTime("Leyton", "Paradise") → 6.66667
```

## My notes (narration log)

<!-- Type decisions as you make them: clarifications, data structure choices,
     edge cases considered, time/space complexity, anything you'd say aloud. -->

## Solution

> Solved in the LeetCode editor (compile-check + autocomplete), pasted back here for the record.

```java
import java.math.BigInteger;
class UndergroundSystem {
    // so we need to keep track of the stations and time to get the average
    private Map<Integer, Pair<String, Integer>> customerTrips;
    private Map<String, Map<String, Pair<BigInteger, BigInteger>>> averages;
    public UndergroundSystem() {
        customerTrips = new HashMap<>();
        averages = new HashMap<>();
    }

    public void checkIn(int id, String stationName, int t) {
        if (customerTrips.containsKey(id) && !customerTrips.get(id).left.equals(stationName)) {
            throw new RuntimeException("Customer id " + id + " is checked into different places.");
        }
        customerTrips.put(id, Pair.of(stationName, t));
    }

    // question: for concurrent use cases, we need to lock on the customer trip, so it cannot check in a new trip before checking out the current trip.
    public void checkOut(int id, String stationName, int t) {
        if (!customerTrips.containsKey(id)) {
            throw new RuntimeException("Customer id " + id + " is not checked in before checking out.");
        }
        // question: what if check in station name is the same as check out station name
        int travelTime = t - customerTrips.get(id).right;
        String startStation = customerTrips.get(id).left;
        averages.putIfAbsent(startStation, new HashMap<>());
        Map<String, Pair<BigInteger, BigInteger>> trips = averages.get(startStation);
        trips.putIfAbsent(stationName, Pair.of(BigInteger.ZERO, BigInteger.ZERO));
        Pair<BigInteger, BigInteger> totalTime = trips.get(stationName);
        totalTime.left = totalTime.left.add(BigInteger.valueOf(travelTime));
        totalTime.right = totalTime.right.add(BigInteger.ONE);
    }

    public double getAverageTime(String startStation, String endStation) {
        // question 1: what if startStation equals endStation?
        // question 2: concurrent? call volume?
        Pair<BigInteger, BigInteger> totalTime = averages.computeIfAbsent(startStation, k -> new HashMap<>())
            .computeIfAbsent(endStation, k -> Pair.of(BigInteger.ZERO, BigInteger.ZERO));
        if (totalTime.right.intValue() == 0) {
            return 0d;
        } else {
            return totalTime.left.doubleValue() / totalTime.right.doubleValue();
        }
    }

    private static class Pair<T, R> {
        T left;
        R right;
        static <T, R> Pair<T, R> of(T l, R r) {
            Pair<T, R> p = new Pair<>();
            p.left = l;
            p.right = r;
            return p;
        }
    }
}
```

## Debrief

- **Time taken, where the minutes went:** ~35 min, solved in the LeetCode editor. Most minutes went to Java syntax recall (months of TypeScript only), not algorithm. Verified against the examples; passing all test cases assumed (not yet re-confirmed).
- **What got narrated vs. skipped:** three typed `question:` comments — concurrency lock per customer, same-station check-in/out, call volume. Good staff-level instincts, but surfaced as code comments mid-solve rather than spoken requirement clarifications upfront. No complexity statement (O(1) per op, O(n) space) and no spoken tradeoff reasoning.
- **Verdict → which study-plan weeks to redo:** Algorithm memory intact — the two-map design was immediate and correct. **Week 1 = skim, not redo.** Java syntax re-warm is confirmed as a real need (`languages/java_playbook.md` pitfalls before Java drills). Narration remains the primary gap, same as the round-2 diagnosis.

### Interviewer notes on the solution

- Correct canonical approach: two maps (customer → checkin, stationPair → total/count), O(1) all ops.
- **Overflow instinct is right but overbuilt:** total travel time ≤ 2×10^4 calls × 10^6 t = 2×10^10 > int, fits `long` easily. `BigInteger` is heavy — expect "why BigInteger, why not long?" and be ready to state the bound math out loud (that's the signal they want, not the type choice).
- **Mutable shared `Pair` accumulation works single-threaded but is subtle** — and you yourself raised concurrency. Under concurrency it's broken; the per-customer lock answer you wrote is the right shape (LC 2043 Level 1). Cleaner read: small `Stats {long total; int count;}` and reassign via `put`.
- **The guard throws are dead code per the problem's guarantees** (chronological events, checkout matches checkin). Fine to keep, but have the answer ready: "the contract guarantees it; the guard fails loudly during development and costs nothing."
- **The three `question:` comments are the best part of the solve** — move them *before* coding next time. That's exactly the Coinbase feedback: "more proactive on requirements."
