# Plant Infection (BFS + State Machine)

**Category:** Coding — **#1 Most Frequent (18+ occurrences)**
**Difficulty:** Medium → Hard (5 progressive parts)
**Time:** 60 min — must complete parts 1-3 to pass, parts 4-5 are bonus
**Key Topics:** BFS, Grid Traversal, State Machine, HashMap for Time Tracking, Greedy/Optimization

---

## Problem Statement

Given a grid of plants:
- `"X"` = infected plant
- `"."` = healthy plant

Every day, each infected plant infects at most its **8 neighbors** (including diagonals).

### Part 1: Basic Infection
Output the number of days to reach balance state (no more plants can be infected).

### Part 2: Immune Plants
`"I"` stands for immune plants (cannot be infected). Output days to balance.

### Part 3: Recovery
Number `D` is given. Infected plants **recover** after exactly `D` days (become healthy again and can be re-infected). Balance = no more infections NOR recoveries.

### Part 4: Death
If an infected plant has at least `K` infected neighbors, it **dies** after exactly `D` days. Dead plants cannot infect or be infected. Balance = no more infections/recoveries/deaths.

### Part 5: Optimization (Greedy)
At the start of any day, you can pick any row/column and **burn** all plants on it (removes them). Design an algorithm to minimize total deaths.

---

## Solution

### Part 1: Basic BFS

**Core idea:** Multi-source BFS from all initially infected cells. Track the day each cell gets infected. Answer = max day.

```java
int plantInfection(char[][] grid) {
    int rows = grid.length, cols = grid[0].length;
    int[][] dirs = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};
    
    Queue<int[]> queue = new LinkedList<>();
    int[][] dayInfected = new int[rows][cols];
    for (int[] row : dayInfected) Arrays.fill(row, -1);
    
    // Seed all initially infected cells
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            if (grid[r][c] == 'X') {
                queue.offer(new int[]{r, c});
                dayInfected[r][c] = 0;
            }
        }
    }
    
    int maxDay = 0;
    while (!queue.isEmpty()) {
        int[] cell = queue.poll();
        int day = dayInfected[cell[0]][cell[1]];
        
        for (int[] d : dirs) {
            int nr = cell[0] + d[0], nc = cell[1] + d[1];
            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
            if (dayInfected[nr][nc] != -1) continue; // already infected
            if (grid[nr][nc] != '.') continue; // not a healthy plant
            
            dayInfected[nr][nc] = day + 1;
            maxDay = Math.max(maxDay, day + 1);
            queue.offer(new int[]{nr, nc});
        }
    }
    return maxDay;
}
```

**Complexity:** O(rows × cols) time and space.

---

### Part 2: Add Immune Plants

**Change:** Skip cells with `grid[r][c] == 'I'` — they can never be infected.

```java
// Only change: add this condition in the BFS neighbor check
if (grid[nr][nc] == 'I') continue; // immune, skip
```

Same structure as Part 1. Immune cells are just walls that block infection spread.

**Complexity:** Same O(rows × cols).

---

### Part 3: Recovery After D Days

**Key insight:** This is no longer simple BFS — cells can be infected, recover (become healthy), and get re-infected. Need simulation day-by-day.

**State per cell:** HEALTHY, INFECTED (with day-of-infection), IMMUNE

**Balance condition:** A day passes with no new infections AND no recoveries.

```java
int plantInfectionWithRecovery(char[][] grid, int D) {
    int rows = grid.length, cols = grid[0].length;
    int[][] dirs = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};
    
    // State: 0 = healthy, -1 = immune, >0 = day infected (1-indexed)
    int[][] state = new int[rows][cols];
    
    // Initialize
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            if (grid[r][c] == 'X') state[r][c] = 1; // infected on day 1
            else if (grid[r][c] == 'I') state[r][c] = -1; // immune
            // else stays 0 (healthy)
        }
    }
    
    int day = 1;
    while (true) {
        boolean changed = false;
        int[][] nextState = new int[rows][cols];
        for (int r = 0; r < rows; r++) {
            nextState[r] = state[r].clone();
        }
        
        // Step 1: Recovery — infected cells that have been infected for D days recover
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (state[r][c] > 0 && day - state[r][c] >= D) {
                    nextState[r][c] = 0; // recover to healthy
                    changed = true;
                }
            }
        }
        
        // Step 2: Infection — healthy cells adjacent to infected cells get infected
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (state[r][c] > 0 && (day - state[r][c] < D)) { // currently infected and not yet recovered
                    for (int[] d : dirs) {
                        int nr = r + d[0], nc = c + d[1];
                        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
                        if (nextState[nr][nc] == 0) { // healthy (including just-recovered)
                            nextState[nr][nc] = day + 1; // infected tomorrow
                            changed = true;
                        }
                    }
                }
            }
        }
        
        if (!changed) return day;
        state = nextState;
        day++;
        
        // Safety: prevent infinite loop (shouldn't happen if logic is correct)
        if (day > rows * cols * D * 2) return day;
    }
}
```

**Note on balance:** With recovery, the system CAN reach a true balance if all plants eventually become immune-through-geometry (surrounded by immune/empty) or if infection + recovery cycles stabilize. In practice, balance occurs when no infected cells can reach new healthy cells.

**Complexity:** O(days × rows × cols) — could be large. Part 3 is significantly harder.

**Potential issue:** The system might cycle infinitely (infect → recover → re-infect → ...). Need to detect this. Balance might mean "no new infections possible" which requires all reachable healthy cells to currently be infected or immune.

**Better approach for balance detection:** If after a full cycle (D days), the set of infected cells is exactly the same as D days ago → we're in a cycle → balance will never be reached. Need to handle this edge case.

---

### Part 4: Death Mechanic

**Clarified rule (from forum):** If a plant is **alive and not immune** at ANY point, and it has ≥ K infected neighbors at that moment, it becomes **severely infected**. Severely infected plants die after exactly N days. Dead = permanent (cannot infect, cannot be infected).

**Key distinction:** This applies to ANY alive non-immune plant — not just already-infected ones. A healthy plant surrounded by K infected neighbors also becomes severely infected.

**Return:** Days until balance AND total number of deaths.

**State per cell:** HEALTHY, INFECTED(day_infected), SEVERELY_INFECTED(day_marked), IMMUNE, DEAD

```java
// State tracking:
// - Normal infection: HEALTHY → INFECTED (can still recover after D days)
// - Severe infection: any alive non-immune cell with >= K infected neighbors
//   → marked SEVERELY_INFECTED → dies N days later
// - Dead cells are permanent walls

// Day-by-day simulation:
// 1. Check deaths: severely infected cells marked N days ago → DEAD
// 2. Check recoveries: infected cells infected D days ago → HEALTHY  
// 3. Spread infection: infected → adjacent healthy
// 4. Check severe: any alive non-immune cell with >= K infected neighbors → mark SEVERELY_INFECTED
// 5. Balance: no changes in this tick

// Key data structures:
Map<Cell, Integer> severeDay = new HashMap<>(); // cell → day it became severely infected
int totalDeaths = 0;
```

**Approach:** Day-by-day simulation:
1. Process deaths: cells in `severeDay` where `currentDay - severeDay[cell] >= N` → mark DEAD, increment totalDeaths
2. Process recoveries: infected cells where `currentDay - infectedDay[cell] >= D` → HEALTHY (unless already dead/severe)
3. Spread infection: infected cells infect adjacent healthy cells
4. Check severe condition: for EVERY alive, non-immune cell, count infected neighbors. If >= K and not already severely marked → add to `severeDay`
5. If no changes occurred → balance reached. Return (day, totalDeaths)

**Variant confirmations (multiple posts agree):**
> "For any plant, at any time when it is alive and not immune, if it has >= k infected neighboring plants, it becomes severely infected. A severely infected plant will die after n days, counted from the moment it became severely infected. Return: how many days for process to finish (no further state changes: new infections / severe infections / deaths), and total number of plants that end up dead."

**Edge cases:**
- A cell can be marked severe BEFORE it's infected (healthy but surrounded by K infected neighbors)
- A cell marked severe that recovers from infection — does it still die? (Likely yes — "severely infected" is a separate death sentence once marked)
- Death countdown starts from moment of severe marking, NOT from infection day
- Order of operations within a day matters — clarify with interviewer if needed
- "Process finished" = no infections + no new severe markings + no deaths in this tick

---

### Part 5: Greedy Optimization (Minimize Deaths)

**This is the hardest part.** At the start of any day, burn an entire row or column (all plants removed = can't infect or be infected or die).

**Approach (greedy heuristic):**
- At each day, evaluate: "if I burn row R or column C, how many deaths does it prevent?"
- Pick the row/column that prevents the most future deaths
- This is likely NP-hard for optimal solution — greedy/heuristic is expected

**Greedy strategy:**
1. Simulate without burning → identify which cells will die and when
2. For each potential burn (row or column), calculate: how many deaths it prevents
3. Burn the one with max prevented deaths
4. Re-simulate and repeat

**Simpler heuristic (likely expected in interview):**
- Burn the row/column with the most currently-infected cells that are about to cause deaths
- Or: burn to create a "firebreak" that isolates the heavily-infected region from healthy regions

**For interview:** Explain the greedy approach, acknowledge it's not optimal, and discuss tradeoffs. Time permitting, implement a simplified version.

---

## Interview Strategy

| Part | Time Target | Difficulty | Must Pass? |
|---|---|---|---|
| Part 1 | 8-10 min | Easy (standard BFS) | ✅ Yes |
| Part 2 | 3-5 min (small change) | Easy | ✅ Yes |
| Part 3 | 15-20 min | Medium-Hard | ✅ Yes (to pass) |
| Part 4 | 10-15 min | Hard | Bonus |
| Part 5 | 10-15 min | Very Hard (greedy) | Bonus (discuss approach) |

**Tips:**
- Part 1 + 2 should take < 15 min combined. If you're spending more, you're too slow.
- Part 3 is the critical one — the state machine + day-by-day simulation is where most people get stuck.
- For Part 3, use a clean state representation. Don't try to be clever — simulate day by day.
- Parts 4-5: if you get here, you're already passing. Discuss approach clearly even if you don't finish coding.

---

## Key Patterns to Recognize

1. **Multi-source BFS** (Part 1) — same as "Rotting Oranges" (LC 994)
2. **State machine per cell** (Parts 3-4) — HEALTHY → INFECTED → RECOVERED/DEAD
3. **Day-by-day simulation** (Parts 3+) — can't do pure BFS anymore, need tick-based simulation
4. **HashMap for scheduling** — "this cell was infected on day X, so it recovers on day X+D"
5. **Neighbor counting** (Part 4) — at each tick, count infected neighbors per cell
6. **Greedy optimization** (Part 5) — evaluate impact of each action, pick best
