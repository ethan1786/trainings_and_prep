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

Fast, near-O(1). Targets the center of the gap and adds emergency overrides.

```java
boolean shouldJump(GameState state) {
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;

    // Emergency: about to hit the floor
    if (state.birdY > state.screenHeight * 0.85 && state.birdV > 0) return true;

    // Emergency: about to hit the ceiling
    if (state.birdY < state.screenHeight * 0.15 && state.birdV < 0) return false;

    // Jump if below gap center and falling
    if (state.birdY > gapCenter && state.birdV > 0) return true;

    return false;
}
```

Weakness: ignores trajectory — may commit to a jump that overshoots the gap.

---

## Approach 2: Lookahead Simulation

Simulate N frames for both actions, score the outcomes, pick the better one.

```java
static final double GRAVITY = 0.5;
static final double JUMP_IMPULSE = -8.0;
static final int LOOKAHEAD_FRAMES = 20;

double simulate(double birdY, double birdV, boolean jumpNow, GameState state, int frames) {
    double y = birdY, v = birdV;
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
    Pipe pipe = state.nextPipe;

    for (int i = 0; i < frames; i++) {
        if (i == 0 && jumpNow) v = JUMP_IMPULSE;
        v += GRAVITY;
        y += v;

        // Death check
        if (y <= 0 || y >= state.screenHeight) return Double.NEGATIVE_INFINITY;

        // Pipe collision (rough: check if bird x overlaps pipe)
        if (pipe.x <= state.birdX && state.birdX <= pipe.x + pipe.width) {
            if (y < pipe.gapTop || y > pipe.gapBottom) return Double.NEGATIVE_INFINITY;
        }
    }

    // Score: proximity to gap center
    return -Math.abs(y - gapCenter);
}

boolean shouldJump(GameState state) {
    double scoreJump = simulate(state.birdY, state.birdV, true, state, LOOKAHEAD_FRAMES);
    double scoreNoop = simulate(state.birdY, state.birdV, false, state, LOOKAHEAD_FRAMES);
    return scoreJump > scoreNoop;
}
```

Tune `LOOKAHEAD_FRAMES` and scoring weights against the simulator.

---

## Approach 3: Minimax Tree Search

Enumerate all binary jump/no-jump sequences over a horizon. Use when simple lookahead oscillates or fails edge cases.

```java
static final double GRAVITY = 0.5;
static final double JUMP_IMPULSE = -8.0;
static final int HORIZON = 15;

boolean shouldJump(GameState state) {
    double scoreJump = search(state.birdY, state.birdV, HORIZON, true, state);
    double scoreNoop = search(state.birdY, state.birdV, HORIZON, false, state);
    return scoreJump > scoreNoop;
}

double search(double y, double v, int depth, boolean jumpedThisFrame, GameState state) {
    if (jumpedThisFrame) v = JUMP_IMPULSE;
    v += GRAVITY;
    y += v;

    if (isDead(y, v, state.nextPipe, state.birdX, state.screenHeight)) {
        return Double.NEGATIVE_INFINITY;
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

boolean isDead(double y, double v, Pipe pipe, double birdX, double screenHeight) {
    if (y <= 0 || y >= screenHeight) return true;
    if (pipe.x <= birdX && birdX <= pipe.x + pipe.width) {
        if (y < pipe.gapTop || y > pipe.gapBottom) return true;
    }
    return false;
}
```

Note: 2^15 = 32K nodes per frame. Add memoization or alpha-beta pruning if this is too slow for the OA's time budget.

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
