# Flappy Bird Agent (CodeSignal OA)

**Category:** OA (Policy/Simulation)
**Difficulty:** Medium
**Time Estimate:** 60-90 min
**Key Topics:** Physics simulation, heuristic search, lookahead, greedy

---

## Problem Statement

Implement `shouldJump(state) -> bool` for a Flappy Bird agent. Given the current frame's game state, decide whether to jump. The goal is to survive as long as possible by navigating through pipe gaps.

## Game State & Physics

```python
@dataclass
class GameState:
    bird_y: float        # vertical position (0 = top)
    bird_v: float        # vertical velocity (positive = falling)
    bird_x: float        # horizontal position (may be fixed)
    screen_height: float
    next_pipe: Pipe

@dataclass
class Pipe:
    x: float             # left edge of pipe
    width: float
    gap_top: float       # y of top edge of gap
    gap_bottom: float    # y of bottom edge of gap
```

Physics per frame (verify exact constants against OA):
- `bird_v += GRAVITY` each frame
- `bird_y += bird_v` each frame
- On jump: `bird_v = JUMP_IMPULSE` (negative = upward)
- Death: `bird_y <= 0`, `bird_y >= screen_height`, or bird overlaps pipe

---

## Approach 1: Simple Heuristic

Fast, near-O(1). Targets the center of the gap and adds emergency overrides.

```python
def shouldJump(state) -> bool:
    gap_center = (state.next_pipe.gap_top + state.next_pipe.gap_bottom) / 2

    # Emergency: about to hit the floor
    if state.bird_y > state.screen_height * 0.85 and state.bird_v > 0:
        return True

    # Emergency: about to hit the ceiling
    if state.bird_y < state.screen_height * 0.15 and state.bird_v < 0:
        return False

    # Jump if below gap center and falling
    if state.bird_y > gap_center and state.bird_v > 0:
        return True

    return False
```

Weakness: ignores trajectory — may commit to a jump that overshoots the gap.

---

## Approach 2: Lookahead Simulation

Simulate N frames for both actions, score the outcomes, pick the better one.

```python
GRAVITY = 0.5
JUMP_IMPULSE = -8.0
LOOKAHEAD_FRAMES = 20

def simulate(bird_y, bird_v, jump_now, state, frames):
    y, v = bird_y, bird_v
    gap_center = (state.next_pipe.gap_top + state.next_pipe.gap_bottom) / 2
    pipe = state.next_pipe

    for i in range(frames):
        if i == 0 and jump_now:
            v = JUMP_IMPULSE
        v += GRAVITY
        y += v

        # Death check
        if y <= 0 or y >= state.screen_height:
            return -float('inf')

        # Pipe collision (rough: check if bird x overlaps pipe)
        if pipe.x <= state.bird_x <= pipe.x + pipe.width:
            if y < pipe.gap_top or y > pipe.gap_bottom:
                return -float('inf')

    # Score: proximity to gap center + upward bias when below center
    return -(abs(y - gap_center))

def shouldJump(state) -> bool:
    score_jump = simulate(state.bird_y, state.bird_v, True, state, LOOKAHEAD_FRAMES)
    score_noop = simulate(state.bird_y, state.bird_v, False, state, LOOKAHEAD_FRAMES)
    return score_jump > score_noop
```

Tune `LOOKAHEAD_FRAMES` and scoring weights against the simulator.

---

## Approach 3: Minimax Tree Search

Enumerate all binary jump/no-jump sequences over a horizon. Use when simple lookahead oscillates or fails edge cases.

```python
from functools import lru_cache

GRAVITY = 0.5
JUMP_IMPULSE = -8.0
HORIZON = 15

def shouldJump(state) -> bool:
    gap_center = (state.next_pipe.gap_top + state.next_pipe.gap_bottom) / 2

    def score(y, v, pipe):
        return -(abs(y - gap_center)) - abs(v) * 0.1

    def is_dead(y, v, pipe, bird_x):
        if y <= 0 or y >= state.screen_height:
            return True
        if pipe.x <= bird_x <= pipe.x + pipe.width:
            if y < pipe.gap_top or y > pipe.gap_bottom:
                return True
        return False

    def search(y, v, depth, jumped_this_frame):
        nonlocal state
        if jumped_this_frame:
            v = JUMP_IMPULSE
        v += GRAVITY
        y += v

        if is_dead(y, v, state.next_pipe, state.bird_x):
            return -float('inf')
        if depth == 0:
            return score(y, v, state.next_pipe)

        return max(
            search(y, v, depth - 1, False),
            search(y, v, depth - 1, True)
        )

    score_jump = search(state.bird_y, state.bird_v, HORIZON, True)
    score_noop = search(state.bird_y, state.bird_v, HORIZON, False)
    return score_jump > score_noop
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
