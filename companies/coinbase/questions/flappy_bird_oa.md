# Flappy Bird Agent (CodeSignal OA)

**Category:** OA (Policy/Simulation)
**Difficulty:** Medium
**Time Estimate:** 60 min
**Key Topics:** Physics simulation, DFS path-finding, oscillation control

---

## Problem Statement

Implement `shouldJump(state) -> bool` for a Flappy Bird agent. Each frame, decide jump or not. Bird dies if it hits ceiling, floor, or pipe outside the gap.

## Game State & Physics

```java
class GameState {
    double birdY;         // vertical position (0 = top, positive = down)
    double birdV;         // vertical velocity (positive = falling)
    double birdX;         // horizontal position
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

Physics per frame (**verify order against OA — this changes the kinematic formula**):
```
v += GRAVITY       // gravity accelerates downward
y += v             // position updates with new velocity
on jump: v = JUMP_V  // velocity resets (negative = upward)
```

**Key physics intuition:** Jump resets velocity, doesn't change position. A jump creates a parabolic arc — bird rises, decelerates, stops, falls back. With GRAVITY=1 and JUMP_V=-8: rises ~28px over 8 frames, full cycle ~15 frames.

---

## Clarify with Cosmo First (5 min)

Before writing any code, ask:
1. What's the coordinate system? (y=0 top or bottom?)
2. Does jump replace velocity (`v = JUMP_V`) or add (`v += JUMP_V`)?
3. Physics update order: `v += g` then `y += v`, or `y += v` then `v += g`?
4. How fast do pipes move? (`PIPE_SPEED`)
5. What are the actual GRAVITY and JUMP_V constants?

---

## Stage 1: Understand + Simple Heuristic (5-10 min)

Read the problem. Implement the simplest thing that makes the bird fly — validates your understanding of the physics and coordinate system.

```java
boolean shouldJump(GameState state) {
    Pipe pipe = state.nextPipe;
    double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

    // predict next frame for both actions
    double nextYNoJump = state.birdY + state.birdV + GRAVITY;
    double nextYJump = state.birdY + JUMP_V + GRAVITY;

    // boundary safety
    if (nextYNoJump >= state.screenHeight - 10) return true;  // floor
    if (nextYJump <= 10) return false;                         // ceiling

    // which action gets closer to gap center?
    return Math.abs(nextYJump - gapCenter) < Math.abs(nextYNoJump - gapCenter);
}
```

**Submit this.** Get a baseline score. Watch the bird fly. Verify physics constants match your assumptions.

**Tell Cosmo:** "Jump affects velocity not position, so I'm predicting next-frame positions for both actions and picking the one closer to gap center."

---

## Stage 2: DFS Path-Finding (20 min)

**The upgrade:** One frame ahead isn't enough. We need to find a SEQUENCE of jump/no-jump decisions that gets the bird from its current position to the gap center when the pipe arrives. This is DFS.

**Key design decisions:**
- Target the pipe's leading edge — DFS delivers bird to gapCenter with v≈0 at entry
- Optimize for minimum |velocity| at arrival — smoothest entry = best chance of surviving the next pipe
- Prune dead branches (boundary death, pipe collision, extreme velocity, node count limit)
- When pipe is far (>25 frames), fall back to heuristic — DFS can't search that deep

**Controllable range estimate:** Bird moves ~3.5 px/frame upward (chain jumping). For a 200px screen: 200/3.5 ≈ 57 frames worst case. But DFS finds optimal paths — **25 frames covers the full screen** in practice. Quick rule: `DFS_RANGE ≈ screenHeight / 8`.

```java
class FlappyAgent {
    static final int G = 1;           // verify against OA
    static final int JUMP_V = -8;     // verify against OA
    static final int PIPE_SPEED = 1;  // verify against OA
    static final int V_ALLOWANCE = 5;
    static final int Y_ALLOWANCE = 10;
    static final int V_MAX = 15;
    static final int DFS_RANGE = 25;
    static final int MAX_NODES = 500_000;

    int nodeCount;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        int gapCenter = (int) ((pipe.gapTop + pipe.gapBottom) / 2.0);
        int framesToPipe = Math.max((int) ((pipe.x - state.birdX) / PIPE_SPEED), 0);

        // Inside pipe zone or pipe passed: heuristic
        if (framesToPipe <= 0) {
            return state.birdY > gapCenter;
        }

        // Pipe within DFS range: path-find
        if (framesToPipe <= DFS_RANGE) {
            nodeCount = 0;
            Optional<Boolean> jumpResult = findPath(
                    (int) state.birdY, (int) state.birdV, gapCenter, framesToPipe,
                    (int) pipe.gapTop, (int) pipe.gapBottom,
                    (int) pipe.x, (int) pipe.width, (int) state.birdX,
                    (int) state.screenHeight);
            if (jumpResult.isPresent()) return jumpResult.get();
        }

        // Pipe far: steer toward gap center (jump if below, coast if above)
        return state.birdY > gapCenter + 14;
    }

    Optional<Boolean> findPath(int y, int v, int targetY, int frames,
                               int gapTop, int gapBottom,
                               int pipeX, int pipeW, int birdX, int screenH) {
        int[] noJumpResult = dfs(y, v, false, frames, 0, targetY,
                gapTop, gapBottom, pipeX, pipeW, birdX, screenH);
        int[] jumpResult = dfs(y, v, true, frames, 0, targetY,
                gapTop, gapBottom, pipeX, pipeW, birdX, screenH);

        // result: [found (0/1), absV at arrival]
        boolean noJumpFound = noJumpResult[0] == 1;
        boolean jumpFound = jumpResult[0] == 1;

        if (!noJumpFound && !jumpFound) return Optional.empty();
        if (noJumpFound && !jumpFound) return Optional.of(false);
        if (!noJumpFound && jumpFound) return Optional.of(true);

        // Both found: pick the one arriving with lower |v|
        return Optional.of(jumpResult[1] < noJumpResult[1]);
    }

    // Returns [found (0/1), best |v| at arrival]
    int[] dfs(int y, int v, boolean jump, int framesLeft, int depth,
              int targetY, int gapTop, int gapBottom,
              int pipeX, int pipeW, int birdX, int screenH) {
        nodeCount++;
        if (nodeCount > MAX_NODES) return new int[]{0, Integer.MAX_VALUE};

        // apply action + physics
        if (jump) v = JUMP_V;
        v += G;
        y += v;

        // prune: boundary death
        if (y <= 0 || y >= screenH) return new int[]{0, Integer.MAX_VALUE};

        // prune: pipe collision
        int pipeXNow = pipeX - (depth + 1) * PIPE_SPEED;
        if (pipeXNow <= birdX && birdX <= pipeXNow + pipeW) {
            if (y <= gapTop || y >= gapBottom) return new int[]{0, Integer.MAX_VALUE};
        }

        // prune: velocity too extreme
        if (Math.abs(v) > V_MAX) return new int[]{0, Integer.MAX_VALUE};

        // base case: reached target frame
        if (framesLeft <= 1) {
            if (Math.abs(y - targetY) <= Y_ALLOWANCE && Math.abs(v) <= V_ALLOWANCE) {
                return new int[]{1, Math.abs(v)};
            }
            return new int[]{0, Integer.MAX_VALUE};
        }

        // recurse both actions
        int[] noJump = dfs(y, v, false, framesLeft - 1, depth + 1, targetY,
                gapTop, gapBottom, pipeX, pipeW, birdX, screenH);
        int[] jumped = dfs(y, v, true, framesLeft - 1, depth + 1, targetY,
                gapTop, gapBottom, pipeX, pipeW, birdX, screenH);

        // pick better result
        if (noJump[0] == 0) return jumped;
        if (jumped[0] == 0) return noJump;
        return noJump[1] <= jumped[1] ? noJump : jumped;
    }
}
```

**Tell Cosmo:** "I'm framing this as path-finding. DFS from current state to gap center, pruning dead branches. Optimizing for minimum arrival velocity so the bird enters the gap smoothly."

---

## Stage 3: Add Oscillation Mode (15 min)

**The problem with pure DFS:** When the pipe is far (>25 frames), the heuristic fallback `y > gapCenter + 14` works but isn't principled. And inside the pipe zone, `y > gapCenter` is crude.

**The fix:** Physics analysis shows the oscillation band is always 28px wide. With `y > target + 14` as the jump trigger, the band is [target-14, target+14], centered perfectly. This is one line of code.

**Two modes:**

| Condition | Mode | Target |
|---|---|---|
| Pipe far (> DFS_RANGE frames) | Oscillate | Screen center |
| Pipe close (≤ DFS_RANGE frames) | DFS path-find | Gap center |
| Inside pipe zone | Oscillate | Gap center |

Only change to the `shouldJump` method:

```java
boolean shouldJump(GameState state) {
    Pipe pipe = state.nextPipe;
    int gapCenter = (int) ((pipe.gapTop + pipe.gapBottom) / 2.0);
    int screenCenter = (int) (state.screenHeight / 2.0);
    int framesToPipe = Math.max((int) ((pipe.x - state.birdX) / PIPE_SPEED), 0);

    // Inside pipe zone: oscillate around gap center
    if (framesToPipe <= 0) {
        return state.birdY > gapCenter + 14;
    }

    // Pipe within DFS range: path-find (same as Stage 2)
    if (framesToPipe <= DFS_RANGE) {
        nodeCount = 0;
        Optional<Boolean> result = findPath(/* same args as Stage 2 */);
        if (result.isPresent()) return result.get();
        return state.birdY > gapCenter + 14;  // DFS failed, oscillate toward gap
    }

    // Pipe far: oscillate around screen center
    return state.birdY > screenCenter + 14;
}
```

**Tell Cosmo:** "I calculated the oscillation band is 28px. With `y > target + 14` the band centers on the target. When the pipe is far I oscillate around screen center, when close I use DFS, when inside the pipe I oscillate around gap center."

**Why +14:** Half the oscillation band width. The bird falls 14px below the jump trigger, then the arc carries it 14px above. Net: symmetric around the target.

---

## Timing Strategy

| Time | What | Safety net |
|---|---|---|
| 0-5 min | Read + clarify physics with Cosmo | — |
| 5-10 min | Stage 1: simple heuristic. **Submit for baseline score.** | Working agent |
| 10-30 min | Stage 2: DFS. Test, debug. **Submit when working.** | If stuck, Stage 1 still works |
| 30-45 min | Stage 3: Add oscillation. Small change on top of working DFS. | If stuck, Stage 2 still works |
| 45-60 min | Tune constants, test edge cases, clean up | — |

**Critical rule:** Each stage is a working improvement. Never delete the previous stage until the new one is tested. If Stage 2 has bugs at minute 30, submit Stage 1 and debug — don't spend Stage 3 time fixing Stage 2.

---

## Debugging Strategy

| Symptom | Likely cause | Fix |
|---|---|---|
| Bird always jumps / flies to ceiling | Physics constants wrong (GRAVITY or JUMP_V) | Verify: freefall 10 frames, compare positions |
| Bird always falls / never jumps | Coordinate system inverted (y=0 bottom not top) | Flip the comparison direction |
| DFS never finds a path | Y_ALLOWANCE too small or constants wrong | Increase Y_ALLOWANCE; verify physics |
| DFS times out (agent freezes) | Search depth too large | Reduce DFS_RANGE; check MAX_NODES |
| Bird passes first pipe, dies on second | DFS finds path but arrival velocity too high | DFS should optimize for min |v| (already does) |
| Bird oscillates but clips pipe edge | Oscillation band wider than gap | Gap < 28px — reduce offset from 14 to smaller |

---

## Staff+ Angle

- **Physics-first approach:** Verify constants before writing complex logic. Wrong GRAVITY invalidates everything.
- **Path-finding framing:** Presenting this as DFS (not just "jump when low") shows algorithmic depth.
- **Two-mode design:** Show engineering maturity — oscillation for stability, DFS for precision, clean transition between modes.
- **Show reasoning to Cosmo:** The chat log is evaluated. Narrate your progression: "I started with a heuristic, realized I need path-finding, now I'm adding oscillation for long-range stability."
