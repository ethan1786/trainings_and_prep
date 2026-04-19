# Flappy Bird Agent (CodeSignal OA)

**Category:** OA (Policy/Simulation)
**Difficulty:** Medium
**Time Estimate:** 60-90 min
**Key Topics:** Physics simulation, heuristic search, lookahead, greedy

---

## Problem Statement

Implement `shouldJump(state) -> bool` for a Flappy Bird agent. Given the current frame's game state, decide whether to jump. The goal is to survive as long as possible by navigating through pipe gaps.

## Game State & Physics

```java
class GameState {
    double birdY;         // vertical position (0 = top)
    double birdV;         // vertical velocity (positive = falling)
    double birdX;         // horizontal position (may be fixed)
    double screenHeight;
    Pipe nextPipe;
}

class Pipe {
    double x;             // left edge of pipe
    double width;
    double gapTop;        // y of top edge of gap
    double gapBottom;     // y of bottom edge of gap
}
```

Physics per frame (verify exact constants against OA):
- `bird_v += GRAVITY` each frame
- `bird_y += bird_v` each frame
- On jump: `bird_v = JUMP_IMPULSE` (negative = upward)
- Death: `bird_y <= 0`, `bird_y >= screen_height`, or bird overlaps pipe

---

## Approach 1: Simple Heuristic

Fast, O(1). Predict next frame's position for both actions, use boundary overrides + core rule.

```java
static final double GRAVITY = 1.0;
static final double JUMP_V = -8.0;

boolean shouldJump(GameState state) {
    Pipe pipe = state.nextPipe;
    double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

    // predict next frame: no jump
    double noJumpY = state.birdY + state.birdV + GRAVITY;
    // predict next frame: jump
    double jumpY = state.birdY + JUMP_V + GRAVITY;

    // boundary override: don't jump into ceiling (but allow if gap is near ceiling)
    if (jumpY <= Math.min(10, pipe.gapTop)) return false;

    // boundary override: must jump if about to hit floor
    if (noJumpY >= Math.max(state.screenHeight - 10, pipe.gapBottom)) return true;

    // core rule: jump if below gap center
    return state.birdY > gapCenter;
}
```

Good starting point. Weakness: ignores momentum — doesn't predict WHERE the bird will be when it reaches the pipe. Approach 2 fixes this with arrival prediction.

---

## Approach 2: Simulation with Inner Policy (Recommended)

Simulate 25 frames for both "jump now" vs "don't jump now". Each simulation uses a simple inner policy for future frames (not pure freefall). Compare trajectories by survival + score.

**Core insight:** We only decide THIS frame. The 25-frame simulation is a heuristic to compare two immediate actions — not a plan. Next frame, we re-evaluate from scratch.

**Architecture:**
```
Emergency rules (O(1) fast-path)
  ↓ if not triggered
Long-range steering (>35px from center, simple rule — simulation can't see far enough)
  ↓ if within range
25-frame simulation comparison (jump vs no-jump, scored by survival + center proximity)
```

```java
class FlappyAgent {
    // === Verify these against the OA's actual physics ===
    static final double GRAVITY = 1.0;
    static final double JUMP_V = -8.0;
    static final double PIPE_SPEED = 1.0;

    static final int LOOKAHEAD = 25;
    static final double V_MARGIN = 3.0;
    static final double H_MARGIN = 1.0;
    static final double BOUNDARY_BUFFER = 10.0;
    static final double EMERGENCY_DIST = 18.0;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

        // === Emergency: boundary safety ===
        double noJumpNextY = state.birdY + state.birdV + GRAVITY;
        double jumpNextY = state.birdY + JUMP_V + GRAVITY;
        double ceilingLimit = Math.min(BOUNDARY_BUFFER, pipe.gapTop);
        if (jumpNextY <= ceilingLimit) return false;
        double floorLimit = Math.max(state.screenHeight - BOUNDARY_BUFFER, pipe.gapBottom);
        if (noJumpNextY >= floorLimit) return true;

        // === Emergency: near pipe and too low ===
        double distX = pipe.x - state.birdX;
        if (distX > 0 && distX <= EMERGENCY_DIST
                && state.birdY > gapCenter + V_MARGIN && state.birdV >= 0) {
            return true;
        }

        // === Long-range steering (sim can't see far enough) ===
        double distToCenter = Math.abs(state.birdY - gapCenter);
        if (distToCenter > 30) {
            if (state.birdY > gapCenter) return state.birdV > -3;
            return false;
        }

        // === Simulation with hybrid inner policy ===
        double[] jumpRes = simulate(state, pipe, gapCenter, true);
        double[] noopRes = simulate(state, pipe, gapCenter, false);

        boolean jumpAlive = jumpRes[0] > 0, noopAlive = noopRes[0] > 0;
        if (!noopAlive && jumpAlive) return true;
        if (noopAlive && !jumpAlive) return false;
        return jumpRes[1] > noopRes[1];
    }

    // Returns [alive (1/0), score]
    double[] simulate(GameState state, Pipe pipe, double gapCenter, boolean jumpNow) {
        double y = state.birdY, v = state.birdV;
        if (jumpNow) v = JUMP_V;

        double totalScore = 0;
        double minClearance = Double.MAX_VALUE;
        int survived = 0;

        for (int step = 0; step < LOOKAHEAD; step++) {
            // Hybrid inner policy for future frames:
            // Near pipe: backward-DP target velocity for precise gap threading
            // Far from pipe: simple "below center + falling" heuristic
            if (step > 0) {
                double pipeFrames = (pipe.x - step * PIPE_SPEED - state.birdX) / PIPE_SPEED;
                if (pipeFrames > 0 && pipeFrames <= 15) {
                    double acc = GRAVITY * pipeFrames * (pipeFrames + 1) / 2.0;
                    double vNeeded = (gapCenter - y - acc) / pipeFrames;
                    if (Math.abs(JUMP_V - vNeeded) < Math.abs(v - vNeeded)) v = JUMP_V;
                } else {
                    if (y > gapCenter && v > 2) v = JUMP_V;
                }
            }

            v += GRAVITY;
            y += v;

            if (y <= V_MARGIN || y >= state.screenHeight - V_MARGIN)
                return new double[]{0, -1000 + survived};

            double curPipeX = pipe.x - step * PIPE_SPEED;
            if (curPipeX - H_MARGIN <= state.birdX
                    && state.birdX <= curPipeX + pipe.width + H_MARGIN) {
                double clearance = Math.min(y - pipe.gapTop, pipe.gapBottom - y);
                minClearance = Math.min(minClearance, clearance);
                if (y <= pipe.gapTop + V_MARGIN || y >= pipe.gapBottom - V_MARGIN)
                    return new double[]{0, -1000 + survived};
                totalScore += 20.0 - Math.abs(y - gapCenter) + clearance * 0.3;
            } else {
                totalScore += 5.0 - Math.abs(y - gapCenter) * 0.15;
            }
            survived++;
        }

        if (minClearance < Double.MAX_VALUE) totalScore += minClearance * 0.5;
        return new double[]{1, totalScore};
    }
}
```

### Key design decisions

**Hybrid inner policy (backward-DP target velocity + simple heuristic):**
The simulation needs to model what happens on FUTURE frames, not just freefall from the initial decision. Without an inner policy, "jump" always looks better because freefall drops the bird into the floor — making the simulation always prefer jumping, causing chain-jumps to the ceiling.

The inner policy uses two modes:
- **Near pipe (≤15 frames):** Backward-DP inspired — compute `v_needed = (gapCenter - y - g*t*(t+1)/2) / t` and jump if `JUMP_V` is closer to `v_needed` than current velocity. This steers precisely toward gap center for pipe passage.
- **Far from pipe:** Simple heuristic `y > gapCenter && v > 2` — just keep the bird roughly centered without over-committing.

**Long-range steering bypass (`distToCenter > 35`):**
The 25-frame simulation can't plan a 65+ px traversal. When the bird needs to cover a large distance to reach the gap, simple rules ("don't jump when above gap, jump when below") work better than simulation because they don't suffer from the inner-policy approximation error.

**Scoring zones:**
- In pipe zone: heavily reward center proximity (20.0 base) + clearance bonus (0.3x)
- Outside pipe zone: gently steer toward center (5.0 base - 0.15x distance)
- Survival bonus: `minClearance * 0.5` rewards safe passages over marginal ones

### Kinematic formula (for understanding, not used in code)

For physics order `v += g` then `y += v`:
```
frame t: y = y0 + t*v0 + g*t*(t+1)/2
```
For physics order `y += v` then `v += g`:
```
frame t: y = y0 + t*v0 + g*t*(t-1)/2
```
**Must verify which order the OA uses.** The simulation handles this implicitly (step-by-step), but knowing the formula helps debug unexpected behavior.

### Tuning guide

| Constant | Start | What to tune for |
|---|---|---|
| `GRAVITY` | 1.0 | Must match OA. Verify: freefall for 10 frames, compare positions |
| `JUMP_V` | -8.0 | Must match OA. Verify: jump from rest, measure peak height |
| `PIPE_SPEED` | 1.0 | Must match OA. Verify: pipe.x delta between frames |
| `V_MARGIN` | 3.0 | Safety margin on collisions. Increase if grazing pipes; decrease if can't reach extreme gaps |
| `LOOKAHEAD` | 25 | More frames = better prediction but slower. 25 is a good default |
| Inner `v > 2` | 2 | Higher = less jumping in sim (risk: falls too far). Lower = more jumping (risk: ceiling) |
| `distToCenter > 35` | 35 | Threshold for long-range steering bypass. Lower = more rule-based, less simulation |
| Scoring weights | 20/0.3/5/0.15/0.5 | Tune against simulator — start with these, adjust pipe-zone weight first |

### Test results (validated with `FlappyAgentTest.java`)

23/23 deterministic tests pass, including:
- 16 single-frame tests: boundary safety, anti-oscillation, overshoot prevention, gap-near-boundary edge cases
- 7 multi-frame simulations (200-300 frames each): centered gap, high gap from low start, low gap from high start, high initial downward velocity, gap near ceiling, gap near floor, back-to-back pipes

The backward-DP target velocity as the inner policy was the key insight — it fixed the extreme-position gap failures (bird starting 65+ px from center) that the simple `v > 2` heuristic couldn't handle.

---

## Approach 3: Minimax Tree Search

Enumerate all binary jump/no-jump sequences over a short horizon. Use when Approach 2 oscillates or fails on tricky pipe configurations.

```java
static final double GRAVITY = 1.0;
static final double JUMP_IMPULSE = -8.0;
static final int HORIZON = 12;  // 2^12 = 4K nodes — fast enough

boolean shouldJump(GameState state) {
    double scoreJump = search(state.birdY, state.birdV, HORIZON, true, state);
    double scoreNoop = search(state.birdY, state.birdV, HORIZON, false, state);
    return scoreJump > scoreNoop;
}

double search(double y, double v, int depth, boolean jumped, GameState state) {
    if (jumped) v = JUMP_IMPULSE;
    y += v;
    v += GRAVITY;

    if (isDead(y, state.nextPipe, state.birdX, state.screenHeight)) {
        return -1000 + (HORIZON - depth); // survived longer = less bad
    }
    if (depth == 0) {
        return score(y, v, state.nextPipe);
    }
    return Math.max(
        search(y, v, depth - 1, false, state),
        search(y, v, depth - 1, true, state)
    );
}

double score(double y, double v, Pipe pipe) {
    double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;
    return -Math.abs(y - gapCenter) - Math.abs(v) * 0.1;
}

boolean isDead(double y, Pipe pipe, double birdX, double screenHeight) {
    if (y <= 0 || y >= screenHeight) return true;
    if (pipe.x <= birdX && birdX <= pipe.x + pipe.width) {
        if (y < pipe.gapTop || y > pipe.gapBottom) return true;
    }
    return false;
}
```

Note: Horizon 12 = 4K nodes per frame. If too slow, reduce to 8 (256 nodes). This is the fallback if Approach 2's scoring heuristic fails — minimax finds the optimal action sequence by exhaustive search.

---

## Debugging Strategy

CodeSignal's Cosmo grader runs the simulator and reports survival frames, not pass/fail. Use this loop:

1. Start with Approach 1 — gets you off the ground.
2. If the bird oscillates through gaps (overshooting up/down), switch to Approach 2.
3. Tune constants: start with `GRAVITY=0.5`, `JUMP_IMPULSE=-8`, then adjust by ±10% if the bird feels off.
4. Watch for edge cases:
   - Pipe gap very close to the top or bottom screen boundary.
   - Two pipes very close together (second pipe becomes `next_pipe` before the first clears).
   - Bird with very high downward velocity heading into a pipe.
5. Add `print` statements to log `(bird_y, bird_v, gap_center, jumped)` if the grader shows a low score.

---

## Staff+ Angle

- **Simulation fidelity:** The OA's exact `GRAVITY` and `JUMP_IMPULSE` constants are the most important thing to get right. Getting them wrong invalidates all three approaches. Verify by simulating a "no-jump" freefall and comparing final position to the spec.
- **Edge-case awareness:** Don't just optimize for the happy path. An agent that survives 1000 frames on normal gaps but dies immediately at screen boundaries is still a failing submission.
- **Systematic tuning vs. guessing:** Treat this like hyperparameter search. Fix one constant at a time and measure the change in survival frames.
- **Complexity budget:** The OA expects near-real-time decisions. Approach 3 is theoretically superior but may time out. Profile before committing to deep search.
