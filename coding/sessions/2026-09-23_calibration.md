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
- Language: **Java or TypeScript** — whichever you intend to interview in. Write
  compilable code, not pseudocode.
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

```java
// write here
```

## Debrief (fill together after)

- Time taken, where the minutes went:
- What got narrated vs. skipped:
- Verdict → which study-plan weeks to redo:
