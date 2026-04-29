# Flappy Bird — Coin Budget Variant

**Category:** OA (Policy/Simulation)
**Difficulty:** Medium
**Key Topics:** Resource-constrained decision making, greedy heuristic, simulation

---

## Problem Statement

Side-scrolling jumping game. Each tick, decide jump or not. Gravity pulls the agent down. Jumping moves the agent up but **costs 1 coin**. Collecting coins on the map refills budget. Crash if height < 0 (floor) or height > H (ceiling). Maximize score (coins collected).

**Key difference from pipe variant:** No pipes to pass through. Instead, the constraint is jump budget — every jump spends a coin. The game is resource management, not oscillation.

---

## Interface

```java
boolean policy(State state)
// state contains: height, velocity, remaining coins, nearby coin positions, etc.
// return true = jump (costs 1 coin), false = fall
```

You don't implement physics — the evaluator does. You only implement decision logic.

---

## Core Tension

Every jump is a -1 to your budget. Gravity is free. The question is always: **is this jump worth the cost?**

| Action | Budget impact | When to do it |
|---|---|---|
| Fall (no jump) | Free | Default — gravity costs nothing |
| Jump to survive | -1 | About to hit floor, no choice |
| Jump to collect coin on arc | -1 + 1 = 0 | Coin is on natural jump trajectory — break-even |
| Jump to collect coin cluster | -1 + N | Multiple coins along the arc — net positive |
| Jump toward distant coin | -1 + 0 = -1 | Coin requires extra jumps to reach — net loss, skip |

---

## Strategy

### Decision hierarchy (check in this order)

1. **Survival — about to hit floor?** Jump if you have coins. Non-negotiable.
2. **Survival — about to hit ceiling?** Don't jump. Let gravity save you.
3. **Profitable coin?** Coin reachable on a natural jump arc → jump (free or net positive).
4. **No coin, safe height?** Don't jump. Conserve budget.
5. **Low budget, no coins nearby?** Minimize jumps — fall as long as safely possible before jumping.

### Coin ROI calculation

Not all coins are worth chasing:

| Coin position | Jumps needed | Net budget | Decision |
|---|---|---|---|
| Directly below (gravity path) | 0 | +1 | Collect for free |
| On natural jump arc | 1 | 0 | Break-even, collect if safe |
| 1 jump above arc | 2 | -1 | Skip unless desperate |
| Near ceiling | 3+ | -2 or worse | Skip — trap |

**Rule of thumb:** Only chase a coin if `coins_collected >= jumps_spent` along the trajectory.

---

## Solution Approach

### Stage 1: Greedy heuristic (5-10 min)

```java
boolean policy(State state) {
    // 1. survival: don't hit floor
    if (state.height <= survivalThreshold && state.coins > 0) return true;

    // 2. survival: don't hit ceiling
    if (state.height >= H - ceilingBuffer) return false;

    // 3. profitable coin nearby — jump arc will collect it
    if (coinOnJumpArc(state) && state.coins > 0) return true;

    // 4. default: conserve budget
    return false;
}
```

`coinOnJumpArc`: check if any coin's position is within the predicted jump trajectory (height after jump ± tolerance). Exact check depends on state fields available.

`survivalThreshold`: depends on velocity — if falling fast, need to jump earlier. Something like `Math.abs(state.velocity) * 2` gives a buffer proportional to fall speed.

### Stage 2: Simulation (15-20 min)

Same structure as pipe variant. Simulate N frames for jump vs no-jump. Score by:

```java
// per-frame scoring
score += coinsCollectedThisFrame;    // +1 per coin touched
if (jumpedThisFrame) score -= 0.8;   // slightly less than 1 — bias toward collecting
if (height <= 0 || height >= H) return score;  // death stops accumulation

// leaf bonus
score += remainingCoins * 0.5;  // future budget has value
```

**Why `jumpCost = 0.8` not `1.0`:** A survival jump that costs 1 coin but keeps you alive is always worth it. If cost = 1.0 and no coin is collected, the simulation scores it as -1 and might prefer not jumping → death. The 0.8 biases toward survival.

### Stage 3: DFS (if needed)

Same upgrade as pipe variant — branch at every frame instead of freefall. Only activate when coins are very close and the decision is tight (e.g., "jump now to grab coin A, or wait 2 frames for coin B").

Search space: bounded by coin visibility range, not pipe width. Should still be manageable.

---

## Edge Cases / Traps

| Trap | What happens | How to handle |
|---|---|---|
| Coin cluster near ceiling | Lures you into ceiling crash | Check ceiling distance before chasing |
| Coin below floor level | Can't reach without dying | Ignore coins at height < safe threshold |
| Long coin drought | No coins for 20+ frames, budget depletes | Minimize jumps — fall as long as possible, jump at last moment |
| Many cheap coins below | Free to collect on gravity path | Don't jump — let gravity deliver them |
| Coin requires 2 jumps up then 1 fall | Net cost = -1 (2 jumps, 1 coin) | Skip unless it's the only coin visible |
| Starting with 0 coins | Can't jump at all | Pray for a gravity-path coin; nothing you can do |
| Coins at same height | Jump arc overshoots one to collect the other | Simulate both trajectories, pick better net |

---

## Key Differences from Pipe Variant

| Aspect | Pipe variant | Coin budget variant |
|---|---|---|
| Constraint | Pass through gap | Don't run out of coins |
| Jump cost | Free (unlimited jumps) | 1 coin per jump |
| Scoring | Survive through pipe | Coins collected |
| Oscillation | Core strategy | Wasteful — every jump costs |
| Gravity | Must counteract | Your friend — free movement |
| Decision driver | Position relative to gap center | ROI of each jump |
| DFS target | Pipe right edge | Next profitable coin |

---

## What the Interviewer Is Testing

This is not a coding-heavy problem. The code is simple (`return true/false`). They're testing:

1. **Resource reasoning** — can you think about budgets and ROI, not just survival?
2. **Greedy vs optimal tradeoffs** — when to skip a coin for a better one later
3. **Edge case awareness** — ceiling traps, budget drought, unreachable coins
4. **Incremental approach** — start simple (survive), then optimize (collect profitably)

A clean greedy with good justification beats a complex DFS with shaky reasoning.
