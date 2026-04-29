// Coin Budget Flappy Bird — Solution
//
// Three modes:
//   1. Decision mode: coin cluster nearby, linear DP to decide take/skip each coin
//   2. Idle mode: no coins nearby, stay near screen center
//   3. Survival mode: low budget, near floor, must jump
//
// Physics: simple +1/-1 per frame (gravity drops 1/frame, jump lifts 1/frame)
// Bird moves right 1 unit per frame. Coins at fixed (x, y) positions.
//
// Score = y + coins (how far the bird can still travel)
//   - Freefall frame: y-1, coins same  → score -1
//   - Jump frame:     y+1, coins-1     → score unchanged (jump preserves score)
//   - Collect coin:   coins+1          → score +1
//
// So the DP per coin is: does collecting this coin gain more score than the
// extra jumps cost in positioning? Pure arithmetic, no simulation needed.

class CoinBirdAgent {
    static final int CLUSTER_GAP = 30;

    // Cache
    Map<Integer, Boolean> cachedDecisions = null;
    int cachedClusterId = -1;
    Coin cachedTarget = null;

    boolean policy(State state) {
        // Survival: near floor and falling
        if (state.height <= 2 && state.velocity <= 0 && state.coins > 0) return true;
        // Ceiling: don't jump into ceiling
        if (state.height >= state.screenHeight - 2) return false;

        List<Coin> visible = state.getVisibleCoins(); // sorted by x
        List<Coin> cluster = getNextCluster(visible, state.birdX);

        if (cluster.isEmpty() || cluster.get(0).x - state.birdX > CLUSTER_GAP) {
            return idleMode(state);
        }

        // Compute or use cached plan
        int clusterId = cluster.get(0).x;
        if (cachedDecisions == null || clusterId != cachedClusterId) {
            cachedDecisions = computePlan(cluster, (int) state.birdX, (int) state.height, state.coins);
            cachedClusterId = clusterId;
            cachedTarget = null;
        }

        return shouldJumpThisFrame(state, cluster, cachedDecisions);
    }

    // Linear DP over sorted coins in cluster
    // At each coin: compare take vs skip by (y + coins) score
    Map<Integer, Boolean> computePlan(List<Coin> cluster, int birdX, int birdY, int budget) {
        Map<Integer, Boolean> decisions = new HashMap<>();

        int prevX = birdX;
        int y = birdY;

        for (Coin coin : cluster) {
            int dx = coin.x - prevX;
            int freefallY = y - dx; // freefall: lose 1 height per frame

            // Skip: just freefall
            // skipScore = freefallY + budget

            // Take: extra jumps needed to reach coin.y from freefall position
            // each jump offsets 1 unit of freefall (score neutral)
            int extraJumps = Math.max(0, coin.y - freefallY);
            boolean reachable = extraJumps <= budget;

            // takeScore = coin.y + (budget - extraJumps + 1)
            // take if: takeScore > skipScore
            //   coin.y + budget - extraJumps + 1 > freefallY + budget
            //   coin.y - extraJumps + 1 > freefallY
            //   simplifies to: 1 > freefallY - coin.y + extraJumps
            //
            // When coin.y >= freefallY: extraJumps = coin.y - freefallY
            //   → 1 > freefallY - coin.y + coin.y - freefallY → 1 > 0 → always true
            //
            // When coin.y < freefallY: extraJumps = 0
            //   → 1 > freefallY - coin.y → only true if freefallY - coin.y < 1
            //   → true when coin is at freefall level, false when coin is far below
            boolean profitable = (coin.y >= freefallY) || (freefallY - coin.y < 1);

            if (reachable && profitable) {
                decisions.put(coin.x, true);
                y = coin.y;
                budget = budget - extraJumps + 1;
            } else {
                decisions.put(coin.x, false);
                y = freefallY;
                // budget unchanged
            }

            prevX = coin.x;
        }

        return decisions;
    }

    // Per-frame: find next coin marked "take", decide if we need to jump now
    boolean shouldJumpThisFrame(State state, List<Coin> cluster, Map<Integer, Boolean> decisions) {
        // Find next target coin
        if (cachedTarget == null || cachedTarget.x <= state.birdX) {
            cachedTarget = null;
            for (Coin c : cluster) {
                if (c.x > state.birdX && decisions.getOrDefault(c.x, false)) {
                    cachedTarget = c;
                    break;
                }
            }
        }

        if (cachedTarget == null) {
            return idleMode(state);
        }

        int framesToCoin = cachedTarget.x - (int) state.birdX;
        int freefallY = (int) state.height - framesToCoin;

        // Coin is at or below freefall path — don't jump, gravity delivers it
        if (cachedTarget.y <= freefallY) {
            return false;
        }

        // Need extra height. Each frame we don't jump, deficit grows by 1.
        // Jump now if remaining frames barely cover the deficit.
        int deficit = cachedTarget.y - freefallY;
        if (deficit >= framesToCoin) {
            return true; // must jump every remaining frame to reach it
        }

        // We have slack — can we wait one more frame?
        // Next frame freefall: height - 1, frames - 1 → freefallY still = height - framesToCoin
        // But jumping now vs later: jumping earlier gives more height
        // Simple rule: start jumping when deficit >= framesToCoin / 2
        // This centers the jumps in the approach window
        if (deficit >= framesToCoin / 2) {
            return true;
        }

        return false;
    }

    boolean idleMode(State state) {
        double center = state.screenHeight / 2.0;
        // Below center and falling — gentle correction
        if (state.height < center && state.velocity <= 0 && state.coins > 0) return true;
        return false;
    }

    List<Coin> getNextCluster(List<Coin> coins, double birdX) {
        List<Coin> cluster = new ArrayList<>();
        for (Coin c : coins) {
            if (c.x < birdX) continue;
            if (cluster.isEmpty() || c.x - cluster.get(cluster.size() - 1).x <= CLUSTER_GAP) {
                cluster.add(c);
            } else {
                break;
            }
        }
        return cluster;
    }

    static class State {
        double height, velocity, birdX, screenHeight;
        int coins;
        List<Coin> getVisibleCoins() { return new ArrayList<>(); }
    }

    static class Coin {
        int x, y;
        Coin(int x, int y) { this.x = x; this.y = y; }
    }
}
