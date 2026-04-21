# Flappy Bird Agent (CodeSignal OA)

**Category:** OA (Policy/Simulation)
**Difficulty:** Medium
**Time Estimate:** 60 min
**Key Topics:** Physics simulation, DFS path-finding, oscillation control

---

## Quick Reference

### Core Strategy

1. **Rush to gap center** as fast as possible (chain-jump up or chain-fall down)
2. **Oscillate around center** to stay safe through the pipe and beyond
3. **Add short-range DFS** if needed for tight gaps (last few frames only)

### Oscillation by Physics Model

| Physics | Jump trigger | Band width | Code |
|---|---|---|---|
| Grid (up N / down N) | `y > gapCenter` | 2 × STEP | `return y > gapCenter;` |
| Replacement (`v = JV`) | `y > gapCenter + OFFSET` | ~28px (G=1, JV=-8) | `return y > gapCenter + 14;` |
| Additive (`v += JV`) | `y > gapCenter && v > thresh` | ~10px (G=1, JV=-8) | `return y > gapCenter && v > thresh;` |

### Key Physics Numbers (G=1, JV=-8)

The physics update ORDER changes everything:

| Metric | Order A: `v+=g, y+=v` | Order B: `y+=v, v+=g` |
|---|---|---|
| Arc height (replacement) | 28px | 36px |
| Oscillation band | 28px | 36px |
| OFFSET needed | 14 | 18 |
| Band fits 40px gap? | Yes (6px clearance/side) | **Barely (2px/side)** |

**Order B (from a recent test-taker's blog) has a 36px band that barely fits a 40px gap.** This is why the blog used the simulation approach — simple oscillation clips the gap edges with Order B physics.

| Metric | Replacement | Additive |
|---|---|---|
| Oscillation band (Order A) | 28px | 10px |
| Oscillation band (Order B) | 36px | ~12px |
| OFFSET needed (Order A) | 14 | 0 |
| OFFSET needed (Order B) | 18 | 0 |
| Velocity threshold | none | 2 (near), 0 (far) |

### OFFSET Formula

`OFFSET ≈ arcHeight / 2`

Arc height depends on physics order:
- Order A (`v+=g, y+=v`): arc = |JV|×(|JV|-1)/2 = 8×7/2 = **28**. OFFSET = 14.
- Order B (`y+=v, v+=g`): arc = |JV|×(|JV|+1)/2 = 8×9/2 = **36**. OFFSET = 18.

Don't memorize — let the bird freefall or jump once and measure the arc. Adjust OFFSET from there.

### When simple oscillation ISN'T enough

If the oscillation band is close to the gap size (e.g., 36px band vs 40px gap = 2px margin), simple oscillation clips edges. Options:
1. **Simulation approach** (proven by test-taker): simulate 25 frames for both jump/no-jump, score by survival + center proximity, pick better action. No inner policy needed if margins are tight enough that freefall already stays close.
2. **Short-range DFS**: finds exact path through the gap with minimal velocity.
3. **Tighter oscillation**: use `y > target + OFFSET && v >= vThresh` — the velocity threshold delays the jump, producing a smaller arc. But this may be too slow to reach distant gaps.

### Gotchas

| Surprise | Impact | How to detect | Fix |
|---|---|---|---|
| Additive jump (`v += JV`) | Chain-jump rockets to ceiling | Bird crashes ceiling in <10 frames | Add `&& v > thresh` |
| y=0 is bottom (not top) | All comparisons inverted | Bird always goes wrong direction | Flip `>` to `<` |
| Physics order `y += v` then `v += g` | Arc height shifts, OFFSET wrong | Bird clips one side of gap consistently | Change OFFSET ± 2-3 |
| Bird has hitbox (not point) | Effective gap shrinks by hitbox height | Bird dies at gap edges despite being "centered" | Reduce OFFSET or widen Y_ALLOWANCE |
| Jump adds AND resets partially | Hybrid — `v = max(v + JV, JV)` | Oscillation is wrong width | Test: jump at v=0 vs v=5, compare arcs |
| Second pipe visible in state | Need to plan for two gaps | First pipe passes fine, second kills | Oscillate between two gap centers |
| Score = precision, not survival | Simple solution passes but scores low | Score barely improves despite surviving | Add DFS for precise arrival |
| Pipe speed varies | `framesToPipe` calculation wrong | Bird arrives early or late | Measure pipe.x across two frames |
| Non-integer positions | DFS rounding errors | DFS finds no path even when close | Increase Y_ALLOWANCE |

### Decision Tree During Assessment

```
Read problem → Clarify physics model with Cosmo
  │
  ├─ Grid (up/down fixed amount)
  │   └─ return y > gapCenter                     ← done in 2 min
  │
  ├─ Replacement (v = JV)
  │   ├─ Stage 1: return y > gapCenter + OFFSET   ← 10 min
  │   │   ├─ Works (gap > band + 10px margin)? → done, tune OFFSET
  │   │   └─ Clips edges (gap ≈ band)? → Stage 2
  │   └─ Stage 2: + short-range DFS or simulation ← 30 min
  │
  ├─ Additive (v += JV)
  │   ├─ Stage 1: return y > gapCenter && v > (dist>20 ? 0 : 2)  ← 10 min
  │   └─ Stage 2: + short-range DFS               ← 30 min
  │
  └─ Unknown → start with y > gapCenter, observe, tune
      ├─ Clips top of gap → add OFFSET (replacement)
      ├─ Rockets to ceiling → add v > thresh (additive)
      ├─ Clips both edges (tight gap) → switch to simulation or DFS
      └─ Neither → grid physics, already done
```

### Simulation Approach (fallback for tight margins)

If simple oscillation clips gap edges (band ≈ gap size), use the simulation approach from the test-taker's blog. This compares 25-frame trajectories for jump vs no-jump and picks the higher-scoring one:

```java
boolean shouldJump(GameState state) {
    // emergency: near floor
    if (state.birdY >= state.screenHeight - 8 && state.birdV > 0) return true;

    double[] jumpScore = simulate(state, true);
    double[] noopScore = simulate(state, false);

    // survival priority: alive > dead
    if (jumpScore[0] > 0 && noopScore[0] <= 0) return true;
    if (noopScore[0] > 0 && jumpScore[0] <= 0) return false;

    return jumpScore[1] > noopScore[1];
}

// returns [alive (1/0), score]
double[] simulate(GameState state, boolean jumpNow) {
    double y = state.birdY, v = state.birdV;
    if (jumpNow) v = JUMP_V;

    double score = 0;
    int survived = 0;
    double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;

    for (int step = 0; step < 25; step++) {
        y += v; v += GRAVITY;  // Order B physics (verify!)

        if (y <= 0 || y >= state.screenHeight)
            return new double[]{0, -1000 + survived};

        double pipeX = state.nextPipe.x - step * PIPE_SPEED;
        if (pipeX <= state.birdX && state.birdX <= pipeX + state.nextPipe.width) {
            double clearance = Math.min(y - state.nextPipe.gapTop, state.nextPipe.gapBottom - y);
            if (clearance <= 0) return new double[]{0, -1000 + survived};
            score += 20 - Math.abs(y - gapCenter) + clearance * 0.3;
        } else {
            score += 5 - Math.abs(y - gapCenter) * 0.15;
        }
        survived++;
    }
    return new double[]{1, score};
}
```

**When to switch from oscillation to simulation:** If Stage 1 passes most tests but clips edges on some, add the simulation as a refinement. The simulation handles tight margins that oscillation can't. It's ~30 lines on top of Stage 1.

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
    return state.birdY > gapCenter + OFFSET;
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

## Stage 2: Simulation (20 min) — Proven on actual OA

**Why upgrade:** With Order B physics (`y+=v, v+=g`), the oscillation band is 36px. If the gap is 40px, that's only 2px clearance per side — simple oscillation clips edges. The simulation approach was used by a test-taker who passed the actual Coinbase OA a few weeks ago.

**How it works:** Each frame, simulate 25 frames of freefall for both "jump now" and "don't jump now". Score each trajectory by survival + proximity to gap center. Pick the higher score. No inner policy, no DFS — just a for loop.

**Why simulation beats DFS here:**
- Less code (~30 lines vs ~40 lines), no recursion, fewer bugs under pressure
- Handles unknown physics naturally — just run the physics forward, no formula needed
- Proven to work on the actual OA
- Scoring by clearance naturally avoids tight margins

```java
class FlappyAgent {
    static final double GRAVITY = 1.0;
    static final double JUMP_V = -8.0;
    static final double PIPE_SPEED = 1.0;
    static final int LOOKAHEAD = 25;

    boolean shouldJump(GameState state) {
        // emergency: near floor and falling
        if (state.birdY >= state.screenHeight - 8 && state.birdV > 0) return true;

        // emergency: near pipe and too low
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;
        double distX = pipe.x - state.birdX;
        if (distX > 0 && distX <= 18 && state.birdY > gapCenter + 3 && state.birdV >= 0)
            return true;

        // simulate both actions, pick better score
        double[] jumpRes = simulate(state, true);
        double[] noopRes = simulate(state, false);

        boolean jumpAlive = jumpRes[0] > 0, noopAlive = noopRes[0] > 0;
        if (!noopAlive && jumpAlive) return true;
        if (noopAlive && !jumpAlive) return false;
        return jumpRes[1] > noopRes[1];
    }

    // returns [alive (1/0), score]
    double[] simulate(GameState state, boolean jumpNow) {
        double y = state.birdY, v = state.birdV;
        Pipe pipe = state.nextPipe;
        double gapCenter = (pipe.gapTop + pipe.gapBottom) / 2.0;

        if (jumpNow) v = JUMP_V;  // or v += JUMP_V if additive

        double score = 0;
        double minClearance = Double.MAX_VALUE;
        int survived = 0;

        for (int step = 0; step < LOOKAHEAD; step++) {
            // physics — VERIFY ORDER against OA
            y += v; v += GRAVITY;  // Order B (from test-taker blog)
            // v += GRAVITY; y += v;  // Order A (alternative — test both)

            // boundary death
            if (y <= 3 || y >= state.screenHeight - 3)
                return new double[]{0, -1000 + survived};

            // pipe zone check
            double pipeX = pipe.x - step * PIPE_SPEED;
            if (pipeX <= state.birdX && state.birdX <= pipeX + pipe.width) {
                double clearance = Math.min(y - pipe.gapTop, pipe.gapBottom - y);
                minClearance = Math.min(minClearance, clearance);
                if (clearance <= 3)
                    return new double[]{0, -1000 + survived};
                score += 20.0 - Math.abs(y - gapCenter) + clearance * 0.3;
            } else {
                score += 5.0 - Math.abs(y - gapCenter) * 0.15;
            }
            survived++;
        }

        if (minClearance < Double.MAX_VALUE) score += minClearance * 0.5;
        return new double[]{1, score};
    }
}
```

**Tell Cosmo:** "I'm simulating 25 frames for both jump and no-jump, scoring by survival and proximity to gap center. This handles tight margins better than pure oscillation."

**Known limitation:** The simulation assumes pure freefall after the initial decision (no future jumps). This works when gaps have enough margin, but for very tight gaps the simulation may not distinguish well between jump and no-jump since both freefall trajectories miss. That's when DFS (Stage 3) helps.

---

## Stage 3: DFS Path-Finding (optional, if time permits)

**Why upgrade from simulation:** The simulation assumes freefall — no future jumps after frame 0. For very tight gaps, DFS explores all possible jump sequences and finds the actual optimal path. It's the same principle as the simulation (compare scores) but searches deeper.

**The spectrum:**
```
Simulation = DFS with depth 1, evaluate by 25-frame freefall scoring
DFS        = DFS with depth N, evaluate by single-frame scoring at leaf
```
Same algorithm, different tradeoff: simulation trades search depth for evaluation quality, DFS trades evaluation quality for search depth.

**Key insight:** Stage 1 already gets the bird near gap center. The DFS only handles the last few frames — a short-range curve ball through the gap. Search depth = `pipeWidth / PIPE_SPEED` + small buffer. That's 2^15 max = 32K nodes — instant, no memoization needed.

**Score-based DFS** (simpler than the binary found/not-found version — same scoring principle as simulation):

```java
class FlappyAgent {
    static final int G = 1;
    static final int JUMP_V = -8;
    static final int PIPE_SPEED = 1;
    static final int OFFSET = 14;  // or 18 for Order B physics

    boolean shouldJump(GameState state) {
        Pipe pipe = state.nextPipe;
        int gapCenter = (int) ((pipe.gapTop + pipe.gapBottom) / 2.0);
        int framesToPipe = Math.max((int) ((pipe.x - state.birdX) / PIPE_SPEED), 0);

        // Short-range DFS: pipe is close, find optimal path through the gap
        int dfsRange = (int) (pipe.width / PIPE_SPEED) + 5;
        if (framesToPipe > 0 && framesToPipe <= dfsRange) {
            double noJumpScore = dfs((int) state.birdY, (int) state.birdV,
                    false, framesToPipe, (int) state.screenHeight, gapCenter);
            double jumpScore = dfs((int) state.birdY, (int) state.birdV,
                    true, framesToPipe, (int) state.screenHeight, gapCenter);
            return jumpScore > noJumpScore;
        }

        // Default: Stage 1 oscillation
        return state.birdY > gapCenter + OFFSET;
    }

    double dfs(int y, int v, boolean jump, int framesLeft, int screenH, int gapCenter) {
        if (jump) v = JUMP_V;  // or v += JUMP_V if additive
        y += v; v += G;        // Order B — swap if Order A

        // death
        if (y <= 0 || y >= screenH) return -10000 + framesLeft;

        // leaf: score by center proximity + velocity penalty
        if (framesLeft <= 1) {
            return -Math.abs(y - gapCenter) - Math.abs(v) * 0.5;
        }

        // recurse: pick the better future
        double noJump = dfs(y, v, false, framesLeft - 1, screenH, gapCenter);
        double jumped = dfs(y, v, true, framesLeft - 1, screenH, gapCenter);
        return Math.max(noJump, jumped);
    }
}
```

**What's simpler vs the old binary DFS:**
- Returns `double` score instead of `int[]` — no found/not-found tracking
- No Y_ALLOWANCE, V_ALLOWANCE — score is continuous, no threshold tuning
- No `Optional<Boolean>`, no `findPath` wrapper — just compare two scores directly
- Same scoring principle as simulation: center proximity matters, velocity is a penalty
- Death returns `-10000 + framesLeft` (same as simulation: survived longer = less bad)

**Tell Cosmo:** "The DFS explores all jump/no-jump sequences for the last few frames before the pipe. Each leaf is scored by proximity to gap center and velocity. It picks the first action of the best-scoring path."

---

## Timing Strategy

| Time | What | Safety net |
|---|---|---|
| 0-5 min | Read + clarify physics model with Cosmo | — |
| 5-10 min | Stage 1: oscillation. **Submit.** Should pass most cases. | Working agent |
| 10-15 min | Observe failures. Tune OFFSET if needed. | Tuned agent |
| 15-35 min | Stage 2: simulation (if Stage 1 clips edges). **Proven on actual OA.** | If stuck, Stage 1 still works |
| 35-50 min | Stage 3: DFS (if simulation can't handle very tight gaps). Optional. | If stuck, Stage 2 still works |
| 50-60 min | Tune, test edge cases, polish Cosmo chat log | — |

**Critical rule:** Each stage is a working improvement. The simulation (Stage 2) is the highest-value upgrade — it's what the test-taker used to pass. DFS (Stage 3) is theoretical overkill unless gaps are extremely tight. If Stage 2 works, spend remaining time on Cosmo chat quality, not more engineering.

---

## Edge Cases & Surprises

### Physics model surprises

| Surprise | What breaks | How to detect | Fix |
|---|---|---|---|
| Additive jump (`v += JV`) | Chain-jump → v=-40 → ceiling crash | Bird crashes ceiling in <10 frames | Add `&& v > thresh` (see additive variant) |
| Physics order: `y += v` then `v += g` | OFFSET is wrong, bird clips one gap side | Consistently misses on same side | Adjust OFFSET by ±2-3 |
| Jump is partial (`v = max(v+JV, JV)`) | Hybrid model, oscillation band differs | Jump at v=0 vs v=5 gives different arcs | Test both, pick the wider OFFSET |
| Gravity changes mid-game | Constants you tuned for are wrong | Bird suddenly starts failing | Read gravity from state each frame if available |
| Jump has cooldown (can't jump every frame) | Chain-jumping impossible, oscillation widens | Bird falls further than expected between jumps | Increase OFFSET, plan for longer cycles |
| Fractional/float physics | DFS integer rounding errors | DFS finds no path despite being close | Increase Y_ALLOWANCE; use double not int |

### Coordinate system surprises

| Surprise | What breaks | How to detect | Fix |
|---|---|---|---|
| y=0 is bottom (not top) | All `>` should be `<` and vice versa | Bird always goes wrong direction | Flip comparisons OR negate y internally |
| x/y are swapped | Bird moves horizontally instead of vertically | Pipe never approaches | Swap x and y reads from state |
| Position is center of bird (not top-left) | Collision math is off by half hitbox | Dies at edges despite being "inside" gap | Subtract hitbox/2 from gap boundaries |
| Positions are doubles, pipe checks are strict `<` not `<=` | Off-by-one on exact gap boundaries | Dies at exactly gapTop or gapBottom | Use gapTop+1 and gapBottom-1 as safe zone |

### Pipe surprises

| Surprise | What breaks | How to detect | Fix |
|---|---|---|---|
| Bird has hitbox (10x10 px) | Effective gap = gap - hitboxHeight | Dies at gap edges "inside" the gap | Shrink gap by hitbox: `gapTop += hitH/2, gapBot -= hitH/2` |
| Pipe has no width (instant check) | `pipeWidth` field is 0 or missing | DFS range calculation is wrong | Use pipeWidth=1 as default |
| Multiple pipes on screen at once | Only planning for nextPipe, die on second | Pass first pipe, immediately hit second | Check state for second pipe; oscillate toward midpoint of both |
| Pipes have variable gap sizes | One-size OFFSET doesn't fit all | Works on wide gaps, fails on narrow | Compute per-pipe: if gap < oscillation band, use DFS |
| Pipe gap is asymmetric (top != bottom width) | gapCenter isn't the safe center | Clips one pipe side more than other | Use `(gapTop + gapBottom) / 2` — this already handles it |
| New pipe appears at random Y after passing | Can't pre-plan for unknown gap | First pipe is fine, second is random | Oscillate around screen center between pipes |

### Scoring surprises

| Surprise | What breaks | How to detect | Fix |
|---|---|---|---|
| Score = distance traveled (not just alive/dead) | Simple solution survives but scores low | Score barely improves between submits | DFS gives tighter trajectory, higher precision |
| Score = time alive (frames survived) | Slower approach scores better | Faster isn't better | Don't rush; oscillate safely |
| Score penalizes distance from center | Off-center oscillation costs points | Check scoring rubric if visible | DFS with min-velocity arrival |
| Score has a maximum (pass/fail) | Over-engineering wastes time | Score hits ceiling with simple solution | Stop optimizing, polish Cosmo chat |
| Multiple test cases with different physics | One set of constants doesn't work for all | Passes some tests, fails others | Read constants from state if possible; tune adaptively |

### Environment / tool surprises

| Surprise | What breaks | How to detect | Fix |
|---|---|---|---|
| `shouldJump` is called BEFORE the frame updates | Your physics prediction is off by one frame | Bird is always 1 frame late | Adjust: predict from current state, not next state |
| `shouldJump` is called AFTER physics, before collision | Position already updated when you decide | Jump has no effect on current frame position | This is normal — just affects next frame |
| State object has different field names | Code doesn't compile | Immediate compile error | Read state class definition carefully; ask Cosmo |
| State contains extra useful fields (score, frame#, second pipe) | Missing optimization opportunities | Read the full state object | Always `System.out.println(state)` first |
| Function must return int (0/1) not boolean | Type mismatch | Compile error | `return (y > trigger) ? 1 : 0;` |
| Time limit per frame (real-time constraint) | DFS too slow | Agent freezes or skips frames | Reduce DFS depth; add MAX_NODES cap |
| No print/debug output visible | Can't debug by logging | Blind debugging | Use Cosmo: "my bird dies around frame 70, what could cause this?" |
| Cosmo gives wrong advice | Code breaks after following suggestion | Things worked before Cosmo's suggestion | Always test after applying Cosmo's advice; revert if worse |

### Game mechanic surprises

| Surprise | What breaks | How to detect | Fix |
|---|---|---|---|
| Bird wraps around screen (no ceiling/floor death) | Boundary checks are unnecessary | Bird passes through top, appears at bottom | Remove boundary checks; adjust oscillation |
| Gravity increases over time | Bird falls faster as game progresses | Works initially, fails later | Re-read gravity from state each frame |
| Pipe speed increases | `framesToPipe` estimate drifts | Bird arrives early/late at gap | Calculate speed from pipe.x deltas; use latest speed |
| Gap shrinks over time | Oscillation band that fit early doesn't fit later | Passes early pipes, fails later ones | Monitor gap size; switch to DFS when gap < band |
| Bonus objects / coins in the gap | Higher score for hitting them | Score doesn't improve despite surviving | Add coin position to DFS target |
| Wind / horizontal force | Bird drifts left or right | Bird x-position changes unexpectedly | Track birdX changes; adjust framesToPipe |
| Jump has animation delay (takes effect next frame) | Jump timing is off by 1 | Bird jumps late consistently | Jump 1 frame earlier than calculated |

---

## Debugging Strategy

| Symptom | Likely cause | Fix |
|---|---|---|
| Bird always jumps / flies to ceiling | Additive physics or wrong constants | Check: is it `v = JV` or `v += JV`? Verify G and JV values |
| Bird always falls / never jumps | Coordinate system inverted (y=0 bottom) | Flip `>` to `<` in trigger |
| Bird goes in right direction but clips pipe edges | OFFSET wrong for this physics model | Tune OFFSET: start at 0, increase by 5 |
| Bird oscillates fine but dies on first pipe | Not reaching gapCenter in time | Bird starts too far from gap; increase travel speed (lower thresh) |
| DFS never finds a path | Y_ALLOWANCE too small or physics constants wrong | Increase Y_ALLOWANCE to 15-20; verify G/JV |
| DFS times out (agent freezes) | Search depth too large | Reduce DFS range; add MAX_NODES=500K cap |
| Bird passes first pipe, dies immediately after | New pipe gap is very different from first | Oscillate around screen center between pipes, not around old gap |
| Score doesn't improve despite surviving longer | Scoring is precision-based, not survival | Add DFS for precise gap-center arrival |
| Code compiles but bird doesn't respond | Field names don't match state object | Print state object; verify field names with Cosmo |

---

## Staff+ Angle

- **Physics-first approach:** Verify constants before writing complex logic. Wrong GRAVITY invalidates everything.
- **Path-finding framing:** Presenting this as DFS (not just "jump when low") shows algorithmic depth.
- **Two-mode design:** Show engineering maturity — oscillation for stability, DFS for precision, clean transition between modes.
- **Adaptive tuning:** Show you can diagnose and fix problems systematically, not just guess. "The bird clips the top → probably need offset → let me calculate the arc height."
- **Show reasoning to Cosmo:** The chat log is evaluated. Narrate your progression: "I started with a heuristic, realized I need path-finding, now I'm adding oscillation for long-range stability."
- **Over-preparation signal:** Proactively mention edge cases before they happen: "I'm checking if the state has a hitbox field, because that would shrink the effective gap."
