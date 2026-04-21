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

| Metric | Replacement | Additive |
|---|---|---|
| Arc height from rest | 28px | 28px (but rarely starts from rest) |
| Arc height at v=3 | 28px (same — v resets) | 15px (v=-5, weaker) |
| Oscillation band | 28px | 10px |
| OFFSET needed | 14 (= band/2) | 0 (band already centered) |
| Velocity threshold | none | 2 (near target), 0 (far from target) |
| Period | ~15 frames | ~8 frames |
| Controllable range (25 frames) | ~400px | varies by v |

### OFFSET Formula

`OFFSET ≈ arcHeight / 2`

For replacement: arc = sum of 1+2+...+|JV|-1 = |JV|×(|JV|-1)/2. With JV=-8: 8×7/2 = 28. OFFSET = 14.

Don't memorize — if you know G and JV, compute: the bird rises for |JV/G| frames, covering |JV|×(|JV|-1)/(2×G) px.

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
  │   └─ return y > gapCenter              ← done in 2 min
  │
  ├─ Replacement (v = JV)
  │   ├─ Stage 1: return y > gapCenter + 14   ← 10 min
  │   └─ Stage 2: + short-range DFS            ← 30 min
  │
  ├─ Additive (v += JV)
  │   ├─ Stage 1: return y > gapCenter && v > (dist>20 ? 0 : 2)  ← 10 min
  │   └─ Stage 2: + short-range DFS            ← 30 min
  │
  └─ Unknown → start with y > gapCenter, observe, tune
      ├─ Clips top of gap → add OFFSET (replacement)
      ├─ Rockets to ceiling → add v > thresh (additive)
      └─ Neither → grid physics, already done
```

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
