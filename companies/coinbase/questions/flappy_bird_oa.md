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
static final double JUMP_IMPULSE = -8.0;

boolean shouldJump(GameState state) {
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;

    // predict next position if we DON'T jump
    double nextV = state.birdV + GRAVITY;
    double nextY = state.birdY + nextV;

    // predict next position if we DO jump
    double jumpV = JUMP_IMPULSE + GRAVITY;
    double jumpY = state.birdY + jumpV;

    // boundary override: don't jump into ceiling
    if (jumpY <= 0) return false;

    // boundary override: must jump if about to hit floor
    if (nextY >= state.screenHeight) return true;

    // core rule: jump if below gap center
    return state.birdY > gapCenter;
}
```

Good enough to get a passing score. Weakness: ignores momentum — if the bird has high downward velocity, one jump isn't enough to reach the gap. That's what Approach 2 fixes.

---

## Approach 2: Lookahead Simulation (Recommended)

Simulate N frames for both "jump now" vs "don't jump now", score each trajectory, pick the better one. **Key insight:** this only decides the current frame — next frame we re-evaluate from scratch with fresh state. The simulation is a heuristic for comparing two immediate actions, not a plan for the future.

Decision priority:
1. Both alive → pick higher score
2. One alive, one dead → pick alive
3. Both dead → pick the one that survived longer

```java
class FlappyAgent {
    static final double GRAVITY = 1.0;
    static final double JUMP_IMPULSE = -8.0;
    static final int LOOKAHEAD = 25;
    static final double V_MARGIN = 3.0;   // safety margin for boundary/pipe collision
    static final double H_MARGIN = 1.0;
    static final double EMERGENCY_DIST = 18.0;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

        // emergency: about to hit floor
        if (state.birdY >= state.screenHeight - 8 && state.birdV > 0) return true;

        // emergency: near pipe and too low
        double distX = pipe.x - state.birdX;
        if (distX <= EMERGENCY_DIST && state.birdY > gapCenter + V_MARGIN && state.birdV >= 0) {
            return true;
        }

        // simulate both actions
        SimResult jumpRes = simulate(state, true);
        SimResult noopRes = simulate(state, false);

        // survival takes priority over score
        if (!noopRes.alive && jumpRes.alive) return true;
        if (noopRes.alive && !jumpRes.alive) return false;

        return jumpRes.score > noopRes.score;
    }

    SimResult simulate(GameState state, boolean jumpNow) {
        double y = state.birdY, v = state.birdV, x = state.birdX;
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

        if (jumpNow) v = JUMP_IMPULSE;

        double totalScore = 0;
        double minClearance = Double.MAX_VALUE;
        int survived = 0;

        for (int step = 0; step < LOOKAHEAD; step++) {
            y += v;
            v += GRAVITY;

            // boundary death (with safety margin)
            if (y <= V_MARGIN || y >= state.screenHeight - V_MARGIN) {
                return new SimResult(false, -1000 + survived, minClearance);
            }

            // pipe zone check (pipe moves left each frame — adjust speed to match OA)
            double pipeX = pipe.x - step;  // assumes pipe speed = 1 px/frame
            if (pipeX - H_MARGIN <= x && x <= pipeX + pipe.width + H_MARGIN) {
                double clearance = Math.min(y - pipe.gapTop, pipe.gapBottom - y);
                minClearance = Math.min(minClearance, clearance);

                // pipe collision (with safety margin)
                if (y <= pipe.gapTop + V_MARGIN || y >= pipe.gapBottom - V_MARGIN) {
                    return new SimResult(false, -1000 + survived, minClearance);
                }

                // in pipe zone: reward center proximity + clearance
                totalScore += 20.0 - Math.abs(y - gapCenter) + clearance * 0.3;
            } else {
                // outside pipe: gently steer toward gap center
                totalScore += 5.0 - Math.abs(y - gapCenter) * 0.15;
            }
            survived++;
        }

        // bonus for sustained clearance
        if (minClearance < Double.MAX_VALUE) totalScore += minClearance * 0.5;

        return new SimResult(true, totalScore, minClearance);
    }

    static class SimResult {
        boolean alive;
        double score;
        double minClearance;
        SimResult(boolean alive, double score, double minClearance) {
            this.alive = alive;
            this.score = score;
            this.minClearance = minClearance;
        }
    }
}
```

**Tuning notes:**
- `GRAVITY` and `JUMP_IMPULSE` must match the OA's physics — verify by simulating freefall and comparing to expected position
- `pipe_x - step` assumes pipe moves 1px/frame — replace with actual pipe speed from the OA
- Physics order (`y += v` then `v += gravity` vs the reverse) matters — verify against the OA spec
- Scoring weights (20.0, 0.3, 5.0, 0.15) are starting points — tune against the simulator

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
