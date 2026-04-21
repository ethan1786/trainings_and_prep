# Drone Food Delivery

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 30-45 min
**Key Topics:** Greedy, Simulation, Sorting, Binary Search

---

## Problem Statement

Simulate a drone delivery system on a 1D number line. A package starts at position 0 and must reach a target position. Charging stations are at fixed positions. The drone can only take off from a station and fly forward at most 10 units per flight.

Each round:
1. Find the nearest forward charging station `s >= current`
2. A human carries the package from `current` to `s` (manual distance)
3. Drone launches from `s`, flies forward at most 10 units, lands
4. Update `current = landing position`
5. Repeat until `current >= target`

Return total distance (clarify: manual only, or manual + drone).

## Example

```
target = 25, stations = [0, 7, 15]

Round 1: current=0, nearest station=0, carry=0, drone flies 0→10, current=10
Round 2: current=10, nearest station=15, carry=5, drone flies 15→25, current=25 ≥ target, done

Total manual carry = 0 + 5 = 5
Total drone flight = 10 + 10 = 20
Total combined = 25
```

---

## Solution

### Core Logic

Greedy: at each step, fly as far as possible (always use full 10 units unless target is closer). The only variable is which station to use — always the nearest forward one.

```java
int totalDistance(int target, int[] stations) {
    Arrays.sort(stations);
    int current = 0;
    int manualDist = 0;
    int droneDist = 0;
    int stationIdx = 0;

    while (current < target) {
        // find nearest station >= current
        while (stationIdx < stations.length && stations[stationIdx] < current) {
            stationIdx++;
        }

        if (stationIdx >= stations.length) {
            // no station ahead — can't proceed (edge case: problem may guarantee reachability)
            return -1;
        }

        int station = stations[stationIdx];
        manualDist += station - current;

        // drone flies forward by at most 10, but not past target
        int landing = Math.min(station + 10, target);
        droneDist += landing - station;

        current = landing;
    }

    // return manualDist, droneDist, or manualDist + droneDist — clarify with interviewer
    return manualDist + droneDist;
}
```

**Complexity:** O(N log N) for sort + O(N) for simulation = O(N log N)

### With Binary Search (if stations array is large)

Replace the linear scan with `Arrays.binarySearch` or `TreeSet.ceiling`:

```java
int totalDistance(int target, int[] stations) {
    TreeSet<Integer> stationSet = new TreeSet<>();
    for (int s : stations) stationSet.add(s);

    int current = 0;
    int totalDist = 0;

    while (current < target) {
        Integer station = stationSet.ceiling(current); // nearest >= current
        if (station == null) return -1;

        totalDist += station - current;                // manual carry
        int landing = Math.min(station + 10, target);
        totalDist += landing - station;                // drone flight
        current = landing;
    }
    return totalDist;
}
```

**Complexity:** O(N log N) for TreeSet build + O(R log N) per round, where R = number of rounds

---

## Follow-Up Questions

### "What if the drone can fly different distances based on battery?"
Replace the constant `10` with a per-station battery level. Each station has `(position, range)`. Same greedy logic, just variable flight distance.

### "What if we want to minimize total distance?"
This becomes an optimization problem. The greedy "nearest station" may not be optimal — sometimes skipping a nearby station to use a farther one with better positioning saves manual carry. This is a shortest-path problem:

```java
// DP: dp[i] = min distance to reach station i or target
// Transition: from station i, drone can reach any position in [station[i], station[i]+10]
//   → for each station j where station[j] >= station[i] and station[j] <= station[i]+10,
//     dp[j] = min(dp[j], dp[i] + (station[i] - prev_landing) + (station[j] - station[i]))
```

### "What if there are stations behind the current position?"
The problem says "forward station" — but if bidirectional, the human could carry backward to a station behind, and the drone flies forward. This adds a dimension: at each step, consider all stations within some radius, not just forward ones.

### "What if multiple drones?"
Parallel flights from different stations. Becomes a scheduling/assignment problem.

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- Station availability: what if a station is occupied or broken? Need fallback logic.
- Concurrency: multiple packages in flight simultaneously, station capacity limits.
- Real-world: 2D/3D coordinates, no-fly zones, wind, battery degradation.

### Common Interview Traps
- **Not sorting stations first.** The input may not be sorted.
- **Off-by-one on "nearest forward."** `>=` not `>` — the drone CAN take off from a station at exactly `current`.
- **Not handling unreachable target.** If there's a gap > 10 between the last station and target with no station in between.
- **Ambiguous "total distance."** Clarify: manual carry only, drone flight only, or both. This is the first thing to ask.

### How to Push Forward as Staff+
- Ask about the optimization variant before the interviewer does
- Mention the DP solution unprompted: "The greedy works but isn't always optimal — if we want minimum distance, this becomes a shortest-path problem"
- Connect to Coinbase: "This is similar to transaction routing — finding the cheapest path through a set of intermediaries, where each hop has constraints"
