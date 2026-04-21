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

## Questions to Clarify (by stage)

You don't know what you don't know yet. Ask these AS you progress — not all upfront.

### While reading the problem (Stage 0)
- "What data does the state object contain? What fields are on the bird and pipe?"
- "What's the coordinate system — is y=0 the top or bottom of the screen?"
- "What does 'death' mean exactly — what are the collision conditions?"

### After reading, before coding (still Stage 0)
This is the most important question — it determines your entire approach:

> "How does movement work? Does the bird have velocity and acceleration, or does it simply move up/down by a fixed amount each frame?"

| Answer | Implication |
|---|---|
| Fixed amount (up N / down N) | **Simple grid.** State = just y. DFS is trivial. Solution is 15 lines. |
| Velocity but no acceleration | State = (y, v) but v is binary. Still simple. |
| Full physics (velocity + gravity) | State = (y, v) continuous. Need the full DFS below. |

### While implementing Stage 1
- "My bird seems to fly in the wrong direction — can you confirm if positive y means up or down?"
- "When the bird jumps, does the velocity get replaced (`v = jumpForce`) or added (`v += jumpForce`)?"

### While implementing Stage 2 (DFS)
- "How fast do pipes move — is it 1 pixel per frame?"
- "What happens at the screen edges — does the bird bounce or die?"
- "Are position and velocity integers or doubles?"
- "Is there only one pipe visible at a time, or can I see multiple pipes ahead?"

### While tuning / debugging
- "My bird gets close to the gap but misses by a few pixels — does the bird have a hitbox size, or is collision point-based?"
- "The DFS seems slow — is there a frame time budget, or does each frame wait for my function to return?"
- "Can I see multiple pipes ahead, or only the next one?"

---

---

## Stage 1: Fast Simple Solution (10 min)

**Goal:** Pass most test cases immediately. Bank a good score. Free up 50 min for the DFS upgrade.

### If simple grid physics (no velocity/acceleration)

```java
boolean shouldJump(GameState state) {
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
    return state.birdY > gapCenter;
}
```

Bird chases gap center every frame. Oscillates within ±STEP. Done.

### If full physics — jump replaces velocity (`v = JUMP_V`)

Rush toward gap center, oscillate. The offset accounts for the asymmetric jump arc.

```java
static final int OFFSET = 14;  // ≈ arcHeight / 2. Tune if constants differ.

boolean shouldJump(GameState state) {
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
    double trigger = Math.max(Math.min(gapCenter + OFFSET, state.screenHeight - OFFSET), OFFSET);
    return state.birdY > trigger;
}
```

Chain-jumping is safe because each jump resets velocity to the same value — no accumulation.

### If full physics — jump adds to velocity (`v += JUMP_V`)

**Critical difference:** Chain-jumping accumulates velocity (v=-8, -16, -24...) → bird rockets to ceiling. Need velocity-aware jumping.

**Good news:** Additive jump is actually easier to oscillate — the arc is smaller (~10px band vs 28px for replacement), so no offset is needed. But you need a distance-aware velocity threshold: jump aggressively when far from target (to travel fast), conservatively when close (to oscillate tight).

```java
boolean shouldJump(GameState state) {
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
    double dist = Math.abs(state.birdY - gapCenter);

    // Far: thresh=0 → climb/fall fast (wider oscillation ~21px, but traveling)
    // Near: thresh=2 → tight oscillation (~10px band, centered on gapCenter)
    int thresh = (dist > 20) ? 0 : 2;

    return state.birdY > gapCenter && state.birdV > thresh;
}
```

**Why no offset:** Additive jumps are weaker (at v=3, `v += -8` gives v=-5, not v=-8). Smaller impulse = smaller arc = band naturally centered. Offset would push the band to the wrong side.

**Why distance-aware threshold:** With `thresh=2`, the bird only gains ~4px per oscillation cycle — too slow to reach a distant gap. With `thresh=0`, it gains ~20px per cycle but oscillates wider. Switching at dist=20 balances speed vs precision.

**Tested 12/12:** All test cases pass including extreme positions, high initial velocity, narrow gaps (20px), and back-to-back pipes.

### Tuning without knowing the physics model

1. Start with `return y > gapCenter` — no offset, no velocity check
2. If the bird clips the top of the gap → add `OFFSET` (replacement physics, try 10, then 14)
3. If the bird rockets to the ceiling → add `&& v > thresh` (additive physics, try thresh=0 then 2)
4. If the bird can't reach distant gaps → add distance-aware threshold (`dist > 20 ? 0 : 2`)

This tuning loop takes 2-3 submits, ~30 seconds each.

**Submit this.** If it passes most cases, you've banked a good score in 10 minutes.

**Tell Cosmo:** "I'm rushing toward the gap center and oscillating. If the bird clips the gap edges, I'll increase the offset to center the oscillation band."

---

## Stage 2: DFS Path-Finding (20 min)

**Why upgrade:** Stage 1 rushes to gap center and oscillates. This works for most gaps. But if the gap is narrower than the oscillation band (~28px), the bird can't oscillate through — it needs to curve through with controlled velocity.

**Key insight:** Stage 1 already does the hard work of getting the bird near gap center. The DFS only handles the last few frames — a short-range curve ball through the gap. Search depth = `pipeWidth / PIPE_SPEED` (e.g., 10 frames for a 10px-wide pipe). That's 2^10 = 1K nodes — instant, no memoization needed.

**How the two stages work together:**
1. Stage 1 runs every frame: rush to gap center, oscillate
2. When pipe is close (≤ pipe width + small buffer): DFS overrides with precise trajectory
3. After passing the pipe: back to Stage 1 oscillation

```java
class FlappyAgent {
    static final int G = 1;           // verify against OA
    static final int JUMP_V = -8;     // verify against OA
    static final int PIPE_SPEED = 1;  // verify against OA
    static final int V_ALLOWANCE = 5;
    static final int Y_ALLOWANCE = 10;
    static final int OFFSET = 14;

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        int gapCenter = (int) ((pipe.gapTop + pipe.gapBottom) / 2.0);
        int framesToPipe = Math.max((int) ((pipe.x - state.birdX) / PIPE_SPEED), 0);

        // Short-range DFS: pipe is close, curve through the gap
        int dfsRange = (int) (pipe.width / PIPE_SPEED) + 5; // pipe width + small buffer
        if (framesToPipe > 0 && framesToPipe <= dfsRange) {
            Optional<Boolean> result = findPath(
                    (int) state.birdY, (int) state.birdV,
                    gapCenter, framesToPipe, (int) state.screenHeight);
            if (result.isPresent()) return result.get();
        }

        // Default: Stage 1 oscillation (rush to center, oscillate)
        double trigger = Math.max(Math.min(gapCenter + OFFSET, state.screenHeight - OFFSET), OFFSET);
        return state.birdY > trigger;
    }

    Optional<Boolean> findPath(int y, int v, int targetY, int frames, int screenH) {
        int[] noJump = dfs(y, v, false, frames, targetY, screenH);
        int[] jump = dfs(y, v, true, frames, targetY, screenH);

        boolean nf = noJump[0] == 1, jf = jump[0] == 1;
        if (!nf && !jf) return Optional.empty();
        if (nf && !jf) return Optional.of(false);
        if (!nf && jf) return Optional.of(true);
        return Optional.of(jump[1] < noJump[1]);
    }

    // Returns [found (0/1), best |v| at arrival]
    int[] dfs(int y, int v, boolean jump, int framesLeft, int targetY, int screenH) {
        if (jump) v = JUMP_V;  // or v += JUMP_V if additive — verify with Cosmo
        v += G;
        y += v;

        if (y <= 0 || y >= screenH) return new int[]{0, Integer.MAX_VALUE};

        if (framesLeft <= 1) {
            if (Math.abs(y - targetY) <= Y_ALLOWANCE && Math.abs(v) <= V_ALLOWANCE)
                return new int[]{1, Math.abs(v)};
            return new int[]{0, Integer.MAX_VALUE};
        }

        int[] no = dfs(y, v, false, framesLeft - 1, targetY, screenH);
        int[] yes = dfs(y, v, true, framesLeft - 1, targetY, screenH);

        if (no[0] == 0) return yes;
        if (yes[0] == 0) return no;
        return no[1] <= yes[1] ? no : yes;
    }
}
```

**Tell Cosmo:** "Stage 1 gets the bird to gap center fast. Now I'm adding short-range DFS for the last few frames before the pipe — it finds the optimal curve to thread through tight gaps with minimal velocity."

---

## Timing Strategy

| Time | What | Safety net |
|---|---|---|
| 0-5 min | Read + clarify physics model with Cosmo | — |
| 5-10 min | Stage 1: oscillation. **Submit.** Should pass most cases. | Working agent |
| 10-15 min | Observe failures. Tune OFFSET/MAX_V if needed. | Tuned agent |
| 15-35 min | Stage 2: add short-range DFS for tight gaps. Small addition on top of Stage 1. | If stuck, Stage 1 still works |
| 35-60 min | Tune, test edge cases, polish Cosmo chat log | — |

**Critical rule:** Stage 1 should pass most cases in 10 minutes. Only invest in DFS if Stage 1 fails on tight gaps. If the simple solution scores 90%, spend the remaining time polishing your Cosmo chat log — the reviewer reads it.

---

## Things That Could Surprise You

These are scenarios we haven't tested but could break the solution:

**Bird has a hitbox (not a point).** If the bird is 10x10 pixels, the effective gap shrinks by 10. A 40px gap becomes 30px — oscillation band (28px) barely fits, 2px clearance. DFS becomes important. **Ask Cosmo: "Does the bird have a hitbox size, or is it a single point?"**

**Additive jump (`v += JUMP_V`).** Our tests use replacement (`v = JUMP_V`). If additive, chain-jumping accumulates: v=-8, -16, -24. The MAX_V cap in Stage 1 handles this, but the oscillation dynamics change entirely — the offset and band width need re-tuning. **The first thing to verify after Stage 1 fails.**

**Physics update order reversed.** We use `v += g; y += v`. If the OA uses `y += v; v += g`, the oscillation shifts. OFFSET might need to be different. **If bird consistently clips one side of the gap, try changing the physics order.**

**Score is precision-based, not just survival.** If the OA measures how centered the bird is when passing through the gap (not just alive/dead), DFS is worth the investment even for wide gaps — it arrives with lower velocity and tighter oscillation.

**Second pipe visible.** If the state provides two pipes, plan for both. If next two gaps are at y=50 and y=150, oscillating around y=100 (midpoint) gives fastest access to both. **Check if `state` has a `secondPipe` field.**

---

## Debugging Strategy

| Symptom | Likely cause | Fix |
|---|---|---|
| Bird always jumps / flies to ceiling | Physics constants wrong (GRAVITY or JUMP_V) | Verify: freefall 10 frames, compare positions |
| Bird always falls / never jumps | Coordinate system inverted (y=0 bottom not top) | Flip the comparison direction |
| DFS never finds a path | Y_ALLOWANCE too small or constants wrong | Increase Y_ALLOWANCE; verify physics |
| DFS times out (agent freezes) | Search depth too large | Reduce DFS_RANGE; lower MAX_NODES |
| Bird passes first pipe, dies on second | DFS_RANGE too small — not enough frames to plan a low-velocity arrival | Increase DFS_RANGE |
| Bird oscillates but clips pipe edge | Oscillation band (28px) wider than gap | Reduce offset from 14 to smaller value |

---

## Staff+ Angle

- **Physics-first approach:** Verify constants before writing complex logic. Wrong GRAVITY invalidates everything.
- **Path-finding framing:** Presenting this as DFS (not just "jump when low") shows algorithmic depth.
- **Two-mode design:** Show engineering maturity — oscillation for stability, DFS for precision, clean transition between modes.
- **Show reasoning to Cosmo:** The chat log is evaluated. Narrate your progression: "I started with a heuristic, realized I need path-finding, now I'm adding oscillation for long-range stability."
