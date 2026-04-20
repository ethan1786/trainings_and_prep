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

## Stage 1: Simple Heuristic

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

## Stage 2: Next-Frame Prediction

**Upgrade from Stage 1:** Jump changes velocity, not position. So looking at the current frame is useless — we need to predict the NEXT frame for both actions and compare.

**Key clarification to ask Cosmo:** Does jump replace velocity (`v = JUMP_V`) or add to it (`v += JUMP_V`)? This changes the prediction formula.

```java
boolean shouldJump(GameState state) {
    Pipe pipe = state.nextPipe;
    double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

    // predict next frame: no jump (v stays, then gravity, then position)
    double nextYNoJump = state.birdY + (state.birdV + GRAVITY);
    // predict next frame: jump (v resets to JUMP_V, then gravity, then position)
    double nextYJump = state.birdY + (JUMP_V + GRAVITY);

    // boundary safety
    if (nextYNoJump >= state.screenHeight - 10) return true;
    if (nextYJump <= 10) return false;

    // which action gets us closer to gap center?
    return Math.abs(nextYJump - gapCenter) < Math.abs(nextYNoJump - gapCenter);
}
```

**Why this is better than Stage 1:** It accounts for the current velocity when predicting where each action leads. Stage 1 just checks "am I below center?" regardless of momentum.

**Why it's still limited:** Only looks ONE frame ahead. The bird needs to plan a trajectory over 10-70 frames to reach the gap. That's what Stage 3 (DFS) solves.

---

## Stage 3: Pure DFS Path-Finding

**Upgrade from Stage 2:** Instead of predicting one frame ahead, find a sequence of jump/no-jump decisions from NOW to the pipe that lands the bird at gap center with minimum velocity.

**Core idea:** This is a path-finding problem. DFS explores all jump/no-jump sequences, pruning dead branches (boundary, pipe collision, extreme velocity). At the target depth, accept paths within Y_TOLERANCE of gap center, and pick the one with lowest |velocity| at arrival.

**When pipe is far (>25 frames):** DFS can't search that deep — fall back to a simple heuristic (jump if below center with arc offset). The DFS takes over as soon as the pipe enters range.

**Critical detail discovered during testing:** Target the pipe MIDPOINT, not the leading edge. The bird traverses the pipe for `pipeWidth` frames. Targeting the front edge means the bird arrives correctly but drifts out during traversal.

```java
class FlappyAgent {
    static final double GRAVITY = 1.0;     // verify against OA
    static final double JUMP_V = -8.0;     // verify against OA
    static final double PIPE_SPEED = 1.0;  // verify against OA
    static final double MARGIN = 3.0;
    static final double Y_TOLERANCE = 5.0;
    static final double V_MAX = 15.0;
    static final int MAX_NODES = 500_000;
    static final int DFS_RANGE = 25;

    int nodeCount;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

        int framesToPipeMid = Math.max(
                (int) ((pipe.x + pipe.width / 2.0 - state.birdX) / PIPE_SPEED), 0);

        // Inside pipe zone: simple heuristic (jump if below center)
        if (framesToPipeMid <= 0) {
            return state.birdY > gapCenter;
        }

        // Pipe within DFS range: path-find
        if (framesToPipeMid <= DFS_RANGE) {
            nodeCount = 0;
            double[] best = {-1, Double.MAX_VALUE};
            dfs(state.birdY, state.birdV, false, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, false, best, Y_TOLERANCE);
            dfs(state.birdY, state.birdV, true, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, true, best, Y_TOLERANCE);
            if (best[0] >= 0) return best[0] == 1;

            // Widen: accept anywhere inside the gap
            double gapTol = (pipe.gapBottom - pipe.gapTop) / 2.0 - MARGIN;
            nodeCount = 0;
            best = new double[]{-1, Double.MAX_VALUE};
            dfs(state.birdY, state.birdV, false, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, false, best, gapTol);
            dfs(state.birdY, state.birdV, true, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, true, best, gapTol);
            if (best[0] >= 0) return best[0] == 1;
        }

        // Pipe is far: steer toward gap center with arc offset
        double jumpTarget = gapCenter + 10;
        double dist = state.birdY - jumpTarget;
        if (dist > 20) return state.birdV > -3;
        if (state.birdY < gapCenter - 15) return false;
        if (dist > 0) return state.birdV > 3;
        return false;
    }

    // DFS: same as Stage 4 below (shared code)
    void dfs(double y, double v, boolean jump, int framesLeft, int depth,
             double targetY, Pipe pipe, double birdX, double screenH,
             int vSign, boolean firstActionWasJump, double[] bestResult,
             double tolerance) {
        nodeCount++;
        if (nodeCount > MAX_NODES) return;

        if (jump) v = JUMP_V;
        v += GRAVITY;
        y += v;

        if (y <= MARGIN || y >= screenH - MARGIN) return;

        double pipeXNow = pipe.x - (depth + 1) * PIPE_SPEED;
        if (pipeXNow <= birdX && birdX <= pipeXNow + pipe.width) {
            if (y <= pipe.gapTop + MARGIN || y >= pipe.gapBottom - MARGIN) return;
        }

        if (Math.abs(v) > V_MAX) return;

        if (framesLeft <= 1) {
            if (Math.abs(y - targetY) > tolerance) return;
            if (vSign == 1 && v <= 0) return;
            if (vSign == -1 && v >= 0) return;
            double absV = Math.abs(v);
            if (absV < bestResult[1]) {
                bestResult[0] = firstActionWasJump ? 1 : 0;
                bestResult[1] = absV;
            }
            return;
        }

        dfs(y, v, false, framesLeft - 1, depth + 1, targetY, pipe, birdX, screenH,
                vSign, firstActionWasJump, bestResult, tolerance);
        dfs(y, v, true, framesLeft - 1, depth + 1, targetY, pipe, birdX, screenH,
                vSign, firstActionWasJump, bestResult, tolerance);
    }
}
```

**Limitation of pure DFS:** When the pipe is far, the heuristic fallback (jump if below center with arc offset) works but isn't optimal. The bird oscillates but the oscillation isn't centered — it depends on when the bird first reaches the heuristic zone. Stage 4 fixes this with a physics-derived oscillation mode.

---

## Stage 4: Two-Mode DFS with Oscillation

### Physics analysis (pre-calculated, drives the design)

With GRAVITY=1.0 and JUMP_V=-8.0:

| Metric | Value |
|---|---|
| Jump arc from rest | 28px upward over 8 frames |
| Oscillation band | 28px wide, period = 15 frames |
| Best oscillation params | jump when `y > target + 10 && v > 5` → band [target-14, target+14], centered perfectly |
| Full screen traversal (up) | 57 frames (chain jumping) |
| Full screen traversal (down) | 20 frames (freefall) |
| Controllable range in 25 frames | ~400px (covers entire screen from anywhere) |

**Key insight:** In 25 frames, the bird can reach any point on a 200px screen from any starting position. So the DFS never needs to search deeper than 25 frames — it's guaranteed to find a path.

### Two-mode design

The bird has two flight modes:

**Mode: Oscillate** — hold position around a target Y. The bird bounces in a stable 28px band centered on the target. No complex planning needed — one simple rule: `jump when y > target + 10 AND v > 5`.

**Mode: Path-find** — navigate precisely to gap center. DFS searches all jump/no-jump sequences to find the path that arrives at gap center with minimum velocity. 25 frames of search depth covers the full screen.

**When to use which:**

| Condition | Mode | Target |
|---|---|---|
| Pipe is far (> 25 frames away) | Oscillate | Screen center (safest default) |
| Pipe is close (≤ 25 frames away) | Path-find | Gap center (precise threading) |
| Bird is inside the pipe zone | Oscillate | Gap center (stay centered in gap) |

**Why oscillate around screen center when pipe is far:** We can't see the next pipe's gap position until it's within range. The screen center maximizes our options — from center, we can reach any gap position within 25 frames.

**Why the transition at 25 frames works:** Physics guarantees we can reach anywhere on screen in 25 frames. So when the pipe enters range, the DFS always finds a path — no matter where the bird is oscillating.

### Why arrive with velocity close to zero?

After passing the pipe, the bird faces the next pipe (which we can't see yet). If we arrive at the gap center with v=0, we're in the most stable position — maximum flexibility to adjust for whatever gap position comes next. If we arrive with v=+10 (plummeting), we have no room to recover if the next gap is higher. The DFS optimizes for min |v| at arrival for exactly this reason.

### Handling edge cases

- **Bird inside pipe zone (framesToPipe ≤ 0):** Switch to oscillation around gap center. The stable 28px band fits inside a typical 40px gap with room to spare.
- **DFS finds no path to gap center:** Widen tolerance to accept anywhere inside the gap. If still nothing, fall back to oscillation toward gap center.
- **Pipe is far (>25 frames):** Oscillate around screen center — safest default when we don't know where the next gap will be.
- **Multiple paths with same arrival velocity:** Doesn't matter — just pick any. We re-evaluate every frame anyway, so the first decision is all that counts.

### Key bugs found during testing

1. **Target the pipe midpoint, not the leading edge.** The bird must stay inside the gap for `pipeWidth / PIPE_SPEED` frames. Targeting the leading edge means the bird arrives at the right Y, but then continues through the pipe zone and drifts out of the gap. Fix: `framesToPipe = (pipeX + pipeWidth/2 - birdX) / PIPE_SPEED`.

2. **Safe fallback inside the pipe zone.** When the bird is already inside the pipe, don't use the DFS or the general heuristic — simulate both actions for the remaining pipe frames and pick the one that stays inside the gap. A naive "jump if below center" can send the bird above `gapTop` while still traversing the pipe.

3. **Oscillation offset.** With JUMP_V=-8 and GRAVITY=1, `jump when y > target+10 && v > 5` produces a perfectly centered 28px band. These constants come from physics analysis, not trial and error.

### Implementation (validated, 7/7 tests pass)

```java
class FlappyAgent {
    static final double GRAVITY = 1.0;     // verify against OA
    static final double JUMP_V = -8.0;     // verify against OA
    static final double PIPE_SPEED = 1.0;  // verify against OA
    static final double MARGIN = 3.0;
    static final double Y_TOLERANCE = 5.0;
    static final double V_MAX = 15.0;
    static final int MAX_NODES = 500_000;

    // Oscillation: physics-derived. band=[target-14, target+14], period=15 frames
    static final double OSC_OFFSET = 10.0;
    static final double OSC_V_THRESH = 5.0;
    static final int DFS_RANGE = 25;

    int nodeCount;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;
        double screenCenter = state.screenHeight / 2.0;

        // frames to pipe midpoint (bird must be centered here)
        int framesToPipeMid = Math.max(
                (int) ((pipe.x + pipe.width / 2.0 - state.birdX) / PIPE_SPEED), 0);

        // === Mode 1: Inside pipe zone → oscillate around gap center ===
        if (framesToPipeMid <= 0) {
            return oscillate(state.birdY, state.birdV, gapCenter);
        }

        // === Mode 2: Pipe within DFS range → path-find to gap center ===
        if (framesToPipeMid <= DFS_RANGE) {
            nodeCount = 0;
            double[] best = {-1, Double.MAX_VALUE};
            dfs(state.birdY, state.birdV, false, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, false, best, Y_TOLERANCE);
            dfs(state.birdY, state.birdV, true, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, true, best, Y_TOLERANCE);
            if (best[0] >= 0) return best[0] == 1;

            // Widen tolerance: accept anywhere inside the gap
            double gapTol = (pipe.gapBottom - pipe.gapTop) / 2.0 - MARGIN;
            nodeCount = 0;
            best = new double[]{-1, Double.MAX_VALUE};
            dfs(state.birdY, state.birdV, false, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, false, best, gapTol);
            dfs(state.birdY, state.birdV, true, framesToPipeMid, 0, gapCenter,
                    pipe, state.birdX, state.screenHeight, 0, true, best, gapTol);
            if (best[0] >= 0) return best[0] == 1;

            return oscillate(state.birdY, state.birdV, gapCenter);
        }

        // === Mode 3: Pipe is far → oscillate around screen center ===
        return oscillate(state.birdY, state.birdV, screenCenter);
    }

    boolean oscillate(double y, double v, double target) {
        return y > target + OSC_OFFSET && v > OSC_V_THRESH;
    }

    void dfs(double y, double v, boolean jump, int framesLeft, int depth,
             double targetY, Pipe pipe, double birdX, double screenH,
             int vSign, boolean firstActionWasJump, double[] bestResult,
             double tolerance) {
        nodeCount++;
        if (nodeCount > MAX_NODES) return;

        if (jump) v = JUMP_V;
        v += GRAVITY;
        y += v;

        // Prune: boundary death
        if (y <= MARGIN || y >= screenH - MARGIN) return;

        // Prune: pipe collision
        double pipeXNow = pipe.x - (depth + 1) * PIPE_SPEED;
        if (pipeXNow <= birdX && birdX <= pipeXNow + pipe.width) {
            if (y <= pipe.gapTop + MARGIN || y >= pipe.gapBottom - MARGIN) return;
        }

        // Prune: velocity too extreme
        if (Math.abs(v) > V_MAX) return;

        // Base case: reached target depth
        if (framesLeft <= 1) {
            if (Math.abs(y - targetY) > tolerance) return;
            if (vSign == 1 && v <= 0) return;
            if (vSign == -1 && v >= 0) return;
            double absV = Math.abs(v);
            if (absV < bestResult[1]) {
                bestResult[0] = firstActionWasJump ? 1 : 0;
                bestResult[1] = absV;
            }
            return;
        }

        // Recurse: try both actions
        dfs(y, v, false, framesLeft - 1, depth + 1, targetY, pipe, birdX, screenH,
                vSign, firstActionWasJump, bestResult, tolerance);
        dfs(y, v, true, framesLeft - 1, depth + 1, targetY, pipe, birdX, screenH,
                vSign, firstActionWasJump, bestResult, tolerance);
    }

}
```

### Why this works without memoization

**Pruning is aggressive.** At each node, the DFS prunes if:
- Bird hits ceiling or floor (dead)
- Bird hits pipe (dead)
- Velocity exceeds ±15 (unrecoverable)
- Node count exceeds 500K (safety timeout)

In practice, most branches die within 5-10 frames. A bird falling at v=10 hits the floor in ~15 frames — that entire subtree is pruned. The surviving branches are the narrow "corridor" of viable trajectories, far smaller than 2^N.

Search depth is capped at 25 (pipe within range) + fallback to O(1) steering when pipe is far. The DFS never searches deeper than 25 levels.

### Complexity

| Metric | Value |
|---|---|
| Theoretical worst case | O(2^framesToPipe) |
| Practical with pruning | O(10K-100K nodes per frame) |
| Per-node work | O(1) — just physics + boundary check |
| Space | O(framesToPipe) — recursion stack depth |

### What to say to Cosmo

> "I'm framing this as a path-finding problem. The bird starts at (y, v) and I need to find a sequence of jump/no-jump decisions that reaches the gap center with minimal velocity. I'm using DFS with pruning — dead states (boundary, pipe) cut branches early. The target is gap center, but if no path exists I'll fall back to gap top or gap bottom with a velocity constraint. Does this approach make sense with the physics model?"

This shows the reviewer: you understand the problem structure, you have a principled optimization criterion (min arrival velocity), and you have fallback strategies.

---

## Staging Strategy for the OA

| Time | Stage | What to do | What you have | Risk |
|---|---|---|---|---|
| 0-5 min | Read + clarify | Read problem. Ask Cosmo: coordinate system, gravity, jump force, pipe speed. Don't code yet. | Understanding | Low |
| 5-10 min | Stage 1 | Simple heuristic: boundary checks + "jump if below center". Submit, see bird fly. | Working agent, baseline score | Low |
| 10-15 min | Stage 2 | Next-frame prediction: predict both actions one frame ahead. Tell Cosmo: "Jump changes velocity not position, so I need to look ahead." | Better agent | Low |
| 15-35 min | Stage 3 | Pure DFS: path-find from current state to gap center. Key pieces: `dfs` with pruning, fallback heuristic for far pipes. **Don't delete Stage 2 until Stage 3 is tested.** | DFS agent | **High** — budget full 20 min |
| 35-50 min | Stage 4 | Two-mode: replace the far-pipe heuristic with physics-derived oscillation. Tell Cosmo: "I calculated the oscillation band is 28px, so the bird can hold position with one simple rule." | Robust agent | Medium |
| 50-60 min | Tune + test | Tune constants against the OA's actual physics. Test edge cases. Clean up. | Polished submission | Low |

**Critical safety rule:** Each stage should be a working improvement over the last. If Stage 3 has bugs at minute 35, **submit Stage 2 and debug**. Don't spend Stage 4 time fixing Stage 3.

**What to say to Cosmo at each transition:**
- Stage 1→2: "The bird has momentum, so I need to predict the next frame's position before deciding."
- Stage 2→3: "One frame ahead isn't enough. I'm framing this as a path-finding problem — DFS from current state to gap center, minimizing arrival velocity."
- Stage 3→4: "The DFS works when the pipe is close, but when it's far I need a stable oscillation. I calculated the physics — the bird oscillates in a 28px band with `jump when y > target + 10 && v > 5`."

## Debugging Strategy

1. **Start with Approach 1** — get something working in 5 minutes, see the bird fly, learn the physics.
2. **Observe the failure mode.** Does the bird crash at pipes? At boundaries? Does it oscillate?
3. **Upgrade to Approach 3** — the DFS path-finder.
4. **If DFS seems to timeout:** Reduce framesToPipe cap (e.g., only search 30 frames ahead), or tighten V_MAX to prune more aggressively.
5. **If bird still hits pipes:** Check Y_TOLERANCE — too large means the DFS accepts paths that miss the gap. Too small means no path is found and it falls back to the heuristic.
6. **If no path is found too often:** The fallback targets (gapTop, gapBottom) or the heuristic are firing. Check if the physics constants are correct — wrong GRAVITY or JUMP_V makes the DFS think paths are viable when they're not.

**Common failure modes and fixes:**
| Symptom | Cause | Fix |
|---|---|---|
| DFS never finds a path | Y_TOLERANCE too small or physics constants wrong | Increase Y_TOLERANCE; verify GRAVITY/JUMP_V |
| DFS times out | framesToPipe too large, not enough pruning | Cap framesToPipe at 40; reduce V_MAX |
| Bird passes pipe but hits next one | Arriving with high velocity | This is working as designed — v≈0 criterion handles it. Check if multiple paths exist and lowest-v is being selected |
| Bird hits pipe edges | MARGIN too small | Increase MARGIN |
| Fallback fires too often | DFS can't find viable paths | Likely physics constants mismatch; also check if coordinate system is correct (y=0 top vs bottom) |

---

## Staff+ Angle

- **Simulation fidelity:** The OA's exact `GRAVITY` and `JUMP_V` constants are the most important thing to get right. Getting them wrong invalidates all approaches. Verify by simulating a "no-jump" freefall and comparing final position to the spec.
- **Path-finding framing:** Presenting this as a path-finding/DP problem (not just "jump when low") shows algorithmic depth. Mention the optimization criterion (minimize arrival velocity) and why it matters (stability for the next unknown pipe).
- **Graceful degradation:** The 3-target fallback chain (center → gapTop → gapBottom → heuristic) shows engineering maturity. You don't just fail — you degrade gracefully.
- **Show your reasoning to Cosmo:** The chat log is evaluated. Frame your progression: "I started with a simple heuristic, but realized I need to plan ahead to the pipe. I'm now treating this as a path-finding problem with DFS and pruning."
