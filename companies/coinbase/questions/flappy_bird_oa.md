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
- `bird_v += GRAVITY` each frame (gravity accelerates downward)
- `bird_y += bird_v` each frame (position updates by velocity)
- On jump: `bird_v = JUMP_V` (velocity resets to a large negative = upward)
- Death: `bird_y <= 0` (ceiling), `bird_y >= screen_height` (floor), or bird overlaps pipe outside gap

**Key physics intuition:** The bird is always being pulled down by gravity. A jump doesn't "move" the bird — it resets the velocity to a large upward value. The bird then decelerates (gravity reduces the upward speed), stops momentarily, and begins falling again. With GRAVITY=1 and JUMP_V=-8, one jump creates a parabolic arc: rises for ~8 frames (covering ~28px upward), then falls symmetrically. The bird can never hover — it's always either rising or falling.

---

## Thinking Through the Problem

### What makes this hard?

The bird has only one action: jump or don't jump. But the effect of jumping is delayed and non-linear — jumping now affects position over the next 8-16 frames. You can't just react to where the bird IS; you need to think about where it WILL BE.

### What does the ideal trajectory look like?

The safest position is the center of the next pipe's gap. If you could hover there, you'd have maximum clearance on both sides. Since hovering is impossible, the next best thing is a tight oscillation centered on the gap — small bounces up and down around the center line.

### The core question each frame

"Given my current position and velocity, will I pass through the next gap safely? If not, does jumping NOW improve my chances?"

This breaks into three sub-problems:
1. **Am I about to die?** (boundary check — need immediate action)
2. **Where will I be when I reach the pipe?** (trajectory prediction)
3. **Is jumping or not jumping better for my trajectory?** (action selection)

---

## Approach 1: Simple Heuristic

**Idea in words:** Look one frame ahead. If not jumping would hit the floor, jump. If jumping would hit the ceiling, don't. Otherwise, jump whenever you're below the gap center — gravity will always pull you back down, so the bias should be toward jumping when low.

**Why it works:** Gravity is constant and always pulls down. The bird naturally falls. So the default state (no jump) trends downward. Jumping when below center counteracts this downward bias.

**Why it's limited:** It only looks one frame ahead. The bird has momentum — if it's falling at v=8, one frame of "should I jump?" doesn't account for the fact that it'll be 8px lower by next frame, then 9px lower the frame after that. By the time the heuristic says "jump!", it might be too late.

```java
static final double GRAVITY = 1.0;
static final double JUMP_V = -8.0;

boolean shouldJump(GameState state) {
    Pipe pipe = state.nextPipe;
    double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

    double noJumpY = state.birdY + state.birdV + GRAVITY;
    double jumpY = state.birdY + JUMP_V + GRAVITY;

    // don't jump into ceiling (but allow if gap demands it)
    if (jumpY <= Math.min(10, pipe.gapTop)) return false;
    // must jump if about to hit floor
    if (noJumpY >= Math.max(state.screenHeight - 10, pipe.gapBottom)) return true;
    // default: jump if below center
    return state.birdY > gapCenter;
}
```

**When to use:** First 5 minutes of the OA. Get something working, see the bird fly, understand the physics constants. Then upgrade.

---

## Approach 2: Simulation with Inner Policy (Recommended)

### The thought process

**Problem with Approach 1:** It asks "am I below center?" but should ask "will I ARRIVE at center when the pipe reaches me?" These are very different questions when the bird has velocity.

**First attempt (pure lookahead):** Simulate 25 frames of freefall for both "jump now" and "don't jump now". Compare final positions to gap center. Pick the closer one.

**Why pure lookahead fails:** It assumes no future jumps after the initial decision. But we'll jump again next frame if needed! So the simulation thinks "if I don't jump, I'll freefall to y=300 and die" — making jumping ALWAYS look better. The agent chain-jumps every frame and crashes into the ceiling.

**The fix (inner policy):** The simulation must model what the agent would ACTUALLY DO on future frames. We give the simulation a simple autopilot: "on future frames, jump when below center and falling moderately." Now the simulation predicts a realistic oscillating trajectory instead of freefall-to-death.

**Why the inner policy needs backward-DP:** The simple autopilot ("jump when below center and v>2") works when the bird is already near the gap center. But when the pipe is approaching and the bird needs to thread the needle precisely, "below center and falling" isn't precise enough — the bird grazes the pipe edges. So near the pipe, we switch the inner policy to use **target velocity**: compute what velocity we NEED to arrive at gap center, and jump if JUMP_V is closer to that target than our current velocity.

**Why target velocity can't be the OUTER decision:** JUMP_V = -8 is a huge discrete change. When the target velocity is -3, both options are bad: JUMP_V=-8 overshoots by 5, current v=+2 undershoots by 5. The formula says "jump" but the overshoot creates oscillation. Target velocity works INSIDE the simulation (where it makes many small corrections over many frames) but not as a single-frame outer decision.

### Architecture in words

The agent evaluates rules in priority order. The first rule that fires makes the decision.

**Layer 1 — Emergency rules (O(1), no simulation needed):**
- "If I don't jump, will I hit the floor next frame?" → Must jump. No time to think.
- "If I do jump, will I hit the ceiling next frame?" → Must NOT jump. Same logic.
- "Am I about to enter the pipe and I'm below the gap with downward velocity?" → Emergency jump. We're out of time to adjust smoothly.

The ceiling/floor thresholds are gap-aware: if the gap IS near the ceiling (gapTop=10), the ceiling check uses gapTop instead of a fixed buffer. Otherwise you'd never be able to reach high gaps.

**Layer 2 — Long-range steering (O(1), simple rule):**
- "Am I very far from where I need to be (>30px from gap center)?" → The 25-frame simulation can't plan a long traversal. Its inner policy approximation degrades over large distances. So we use basic rules: if below the gap, jump (unless already rising fast). If above the gap, let gravity do the work.

**Layer 3 — Simulation comparison (O(LOOKAHEAD), the main logic):**
- Run the physics forward 25 frames twice: once assuming we jump now, once assuming we don't.
- On each future frame, the inner policy decides whether to jump (modeling what the agent would actually do).
- Score each trajectory: Did we survive? How close did we stay to gap center? How much clearance did we have when passing through the pipe?
- Pick the action whose trajectory scored higher. If one dies and one survives, pick survival regardless of score.

### Inner policy logic in words

The inner policy runs inside each simulation step (for future frames only — frame 0 is decided by the outer agent).

**When the pipe is close (≤15 frames away):**
Use the backward-DP target velocity formula. "In T frames, I need to be at gap center. Given my current position and the acceleration from gravity, what velocity do I need RIGHT NOW to arrive there?" If JUMP_V is closer to that needed velocity than my current velocity, jump. Otherwise coast.

This is like working backwards from the destination: "If I need to be at y=100 in 10 frames, and gravity adds 55px of downward displacement, I need velocity = (100 - current_y - 55) / 10." If that needed velocity is -6 and I'm currently at +3, JUMP_V=-8 is closer to -6 than +3 is, so jump.

**When the pipe is far (>15 frames away):**
Simple heuristic: jump if below gap center AND falling at v>2. The "v>2" threshold prevents jumping when the bird is already rising — without it, the inner policy would chain-jump and send the bird to the ceiling. The value 2 means "only jump to arrest a meaningful fall, not to add more upward momentum when already moving up."

### Scoring logic in words

Each frame in the simulation accumulates a score:

**In the pipe zone** (bird's horizontal position overlaps the pipe):
- Big reward for being close to gap center (20 points minus distance to center)
- Bonus for clearance (distance from nearest pipe edge × 0.3)
- This is where survival matters most — reward precision

**Outside the pipe zone:**
- Small reward for being near gap center (5 points minus gentle distance penalty)
- This gently steers the bird toward center without creating aggressive corrections that cause oscillation

**Survival bonus at the end:**
- If the bird passed through the pipe zone, the minimum clearance across all pipe-zone frames gets a 0.5x bonus
- This prefers "safely centered" over "barely scraped through"

**Death penalty:**
- If the bird dies during simulation, score = -1000 + frames_survived
- This ensures survival always beats death, but among two dead trajectories, surviving longer is less bad

### Why this beats the other approaches

| Approach | Strength | Weakness |
|---|---|---|
| Approach 1 (heuristic) | O(1), simple, good starting point | Ignores momentum, can't predict pipe arrival |
| Approach 2 (simulation) | Accounts for momentum, realistic trajectories | More code, needs tuning, inner policy matters |
| Approach 3 (minimax) | Theoretically optimal for short horizon | 2^N nodes, may timeout, overkill for this problem |

Approach 2 hits the sweet spot: it's sophisticated enough to handle momentum and edge cases, but simple enough to code in 15 minutes under time pressure.

### Code

```java
class FlappyAgent {
    static final double GRAVITY = 1.0;     // verify against OA
    static final double JUMP_V = -8.0;     // verify against OA
    static final double PIPE_SPEED = 1.0;  // verify against OA

    static final int LOOKAHEAD = 25;
    static final double V_MARGIN = 3.0;
    static final double H_MARGIN = 1.0;
    static final double BOUNDARY_BUFFER = 10.0;
    static final double EMERGENCY_DIST = 18.0;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

        // --- Layer 1: Emergency rules ---
        double noJumpNextY = state.birdY + state.birdV + GRAVITY;
        double jumpNextY = state.birdY + JUMP_V + GRAVITY;
        double ceilingLimit = Math.min(BOUNDARY_BUFFER, pipe.gapTop);
        if (jumpNextY <= ceilingLimit) return false;
        double floorLimit = Math.max(state.screenHeight - BOUNDARY_BUFFER, pipe.gapBottom);
        if (noJumpNextY >= floorLimit) return true;

        double distX = pipe.x - state.birdX;
        if (distX > 0 && distX <= EMERGENCY_DIST
                && state.birdY > gapCenter + V_MARGIN && state.birdV >= 0) {
            return true;
        }

        // --- Layer 2: Long-range steering ---
        double distToCenter = Math.abs(state.birdY - gapCenter);
        if (distToCenter > 30) {
            if (state.birdY > gapCenter) return state.birdV > -3;
            return false;
        }

        // --- Layer 3: Simulation comparison ---
        double[] jumpRes = simulate(state, pipe, gapCenter, true);
        double[] noopRes = simulate(state, pipe, gapCenter, false);

        boolean jumpAlive = jumpRes[0] > 0, noopAlive = noopRes[0] > 0;
        if (!noopAlive && jumpAlive) return true;
        if (noopAlive && !jumpAlive) return false;
        return jumpRes[1] > noopRes[1];
    }

    double[] simulate(GameState state, Pipe pipe, double gapCenter, boolean jumpNow) {
        double y = state.birdY, v = state.birdV;
        if (jumpNow) v = JUMP_V;

        double totalScore = 0;
        double minClearance = Double.MAX_VALUE;
        int survived = 0;

        for (int step = 0; step < LOOKAHEAD; step++) {
            // Inner policy for future frames
            if (step > 0) {
                double pipeFrames = (pipe.x - step * PIPE_SPEED - state.birdX) / PIPE_SPEED;
                if (pipeFrames > 0 && pipeFrames <= 15) {
                    // Near pipe: backward-DP target velocity
                    double acc = GRAVITY * pipeFrames * (pipeFrames + 1) / 2.0;
                    double vNeeded = (gapCenter - y - acc) / pipeFrames;
                    if (Math.abs(JUMP_V - vNeeded) < Math.abs(v - vNeeded)) v = JUMP_V;
                } else {
                    // Far from pipe: simple heuristic
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

### Kinematic formula reference

For physics order `v += g` then `y += v`:
```
frame t: y = y0 + t*v0 + g*t*(t+1)/2
```
For physics order `y += v` then `v += g`:
```
frame t: y = y0 + t*v0 + g*t*(t-1)/2
```
The simulation handles this implicitly (step-by-step), but knowing the formula helps debug. **Must verify which order the OA uses** — get this wrong and all predictions are off.

### Tuning guide

| Constant | Start | What to tune for |
|---|---|---|
| `GRAVITY` | 1.0 | Must match OA. Verify: freefall for 10 frames, compare positions |
| `JUMP_V` | -8.0 | Must match OA. Verify: jump from rest, measure peak height |
| `PIPE_SPEED` | 1.0 | Must match OA. Verify: pipe.x delta between frames |
| `V_MARGIN` | 3.0 | Safety margin on collisions. Increase if grazing pipes; decrease if can't reach extreme gaps |
| `LOOKAHEAD` | 25 | More frames = better prediction but slower. 25 is a good default |
| Inner `v > 2` | 2 | Higher = less jumping in sim (risk: falls too far). Lower = more jumping (risk: ceiling) |
| `distToCenter > 30` | 30 | Threshold for long-range steering bypass. Lower = more rule-based, less simulation |
| Scoring weights | 20/0.3/5/0.15/0.5 | Tune against simulator — start with these, adjust pipe-zone weight first |

### Test results (validated with `FlappyAgentTest.java`)

23/23 deterministic tests pass, including:
- 16 single-frame tests: boundary safety, anti-oscillation, overshoot prevention, gap-near-boundary edge cases
- 7 multi-frame simulations (200-300 frames each): centered gap, high gap from low start, low gap from high start, high initial downward velocity, gap near ceiling, gap near floor, back-to-back pipes

The backward-DP target velocity as the inner policy was the key insight — it fixed the extreme-position gap failures (bird starting 65+ px from center) that the simple `v > 2` heuristic couldn't handle.

---

## Approach 3: Minimax Tree Search

**Idea in words:** Instead of simulating one fixed trajectory, try ALL possible jump/no-jump sequences over the next N frames. Pick the first action of the best sequence. This is brute-force optimal within the horizon.

**How it works:** Build a binary tree. At each level, branch into "jump" and "don't jump". At the leaves (N frames deep), score the final position. Propagate scores upward by taking the max at each level (we control both choices, so we always pick the best). The root's two children give us: "best possible score if I jump now" vs "best possible score if I don't jump now."

**When to use:** Approach 2 oscillates or fails on unusual pipe configurations, and you have time to implement this. It's theoretically optimal but expensive.

**Complexity:** 2^N nodes. N=12 gives 4K nodes per frame (fast). N=15 gives 32K (marginal). N=20 gives 1M (too slow for real-time).

```java
static final double GRAVITY = 1.0;
static final double JUMP_IMPULSE = -8.0;
static final int HORIZON = 12;

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
        return -1000 + (HORIZON - depth);
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

---

## Debugging Strategy

CodeSignal's Cosmo grader runs the simulator and reports survival frames, not pass/fail. Use this loop:

1. **Start with Approach 1** — get something working in 5 minutes, see the bird fly, learn the physics.
2. **Observe the failure mode.** Does the bird oscillate wildly (overshooting up and down)? Does it drift into pipes? Does it crash at boundaries?
3. **Upgrade to Approach 2** if oscillation or momentum issues are visible.
4. **Tune physics constants first.** GRAVITY and JUMP_V must match the OA exactly. Everything else depends on getting these right. Verify: let the bird freefall for 10 frames with no jumps, compare predicted vs actual position.
5. **Tune scoring weights second.** If the bird survives pipes but oscillates too much, increase pipe-zone scoring weight. If it crashes at boundaries, check the V_MARGIN.
6. **Add print statements** to log `(bird_y, bird_v, gap_center, jumped)` per frame if the grader shows a low score. Look for the frame where things go wrong.

**Common failure modes and fixes:**
| Symptom | Cause | Fix |
|---|---|---|
| Bird always flies to ceiling | Chain-jumping — inner policy too aggressive | Increase inner policy `v > 2` threshold |
| Bird always falls to floor | Never jumping — inner policy too conservative | Decrease threshold, or check emergency rules |
| Bird oscillates wildly | Jump is too powerful relative to gravity | Verify GRAVITY/JUMP_V constants match OA |
| Bird grazes pipe edges | Safety margins too small | Increase V_MARGIN |
| Bird can't reach extreme gaps | Safety margins too large | Decrease V_MARGIN or BOUNDARY_BUFFER |
| Bird fine near center, dies at extreme gaps | Simulation can't plan long traversals | Decrease `distToCenter` threshold for long-range bypass |

---

## Staff+ Angle

- **Simulation fidelity:** The OA's exact `GRAVITY` and `JUMP_V` constants are the most important thing to get right. Getting them wrong invalidates all approaches. Verify by simulating a "no-jump" freefall and comparing final position to the spec.
- **Edge-case awareness:** Don't just optimize for the happy path. An agent that survives 1000 frames on normal gaps but dies immediately at screen boundaries is still a failing submission.
- **Systematic tuning vs. guessing:** Treat this like hyperparameter search. Fix one constant at a time and measure the change in survival frames.
- **Complexity budget:** The OA expects near-real-time decisions. Approach 3 is theoretically superior but may time out. Profile before committing to deep search.
- **Show your reasoning to Cosmo:** The chat log is evaluated. Say things like "I'm seeing the bird overshoot the gap — I think my inner policy is too aggressive, going to increase the velocity threshold."
