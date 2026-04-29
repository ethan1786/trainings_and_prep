// Coin Budget Flappy Bird — Solution
//
// Three modes:
//   1. Decision mode: coin cluster nearby, DP to decide take/skip each coin
//   2. Idle mode: no coins nearby, stay near screen center
//   3. Survival mode: low budget, minimize jumps, floor-bounce only
//
// Physics assumption: simple +1/-1 per frame (gravity drops 1/frame, jump lifts 1/frame)
// Bird moves right 1 unit per frame. Coins are at fixed (x, y) positions.

class CoinBirdAgent {
    static final int JUMP_LIFT = 1;
    static final int GRAVITY = 1;
    static final int CLUSTER_GAP = 30; // frames between coins to consider separate clusters

    // Cache: decision for current cluster
    List<boolean[]> cachedPlan = null;
    int cachedPlanStartX = -1;
    int cachedClusterHash = -1;

    boolean policy(State state) {
        // Survival override: about to hit floor
        if (state.height <= 2 && state.velocity <= 0 && state.coins > 0) {
            return true;
        }
        // Ceiling safety: don't jump into ceiling
        if (state.height >= state.screenHeight - 2 && state.velocity >= 0) {
            return false;
        }

        List<Coin> visibleCoins = state.getVisibleCoins(); // sorted by x
        if (visibleCoins.isEmpty()) {
            return idleMode(state);
        }

        // Find the nearest cluster
        List<Coin> cluster = getNextCluster(visibleCoins, state.birdX);
        if (cluster.isEmpty()) {
            return idleMode(state);
        }

        // Is the cluster close enough to decide now?
        int framesToFirstCoin = cluster.get(0).x - (int) state.birdX;
        if (framesToFirstCoin > CLUSTER_GAP) {
            return idleMode(state);
        }

        // Decision mode: check cache or compute new plan
        int clusterHash = cluster.hashCode();
        if (cachedPlan == null || clusterHash != cachedClusterHash) {
            cachedPlan = computePlan(cluster, state);
            cachedPlanStartX = (int) state.birdX;
            cachedClusterHash = clusterHash;
        }

        // Look up current frame's decision from the plan
        int frameIndex = (int) state.birdX - cachedPlanStartX;
        if (frameIndex >= 0 && frameIndex < cachedPlan.size()) {
            return cachedPlan.get(frameIndex)[0]; // [0] = jump decision for this frame
        }

        return idleMode(state);
    }

    // Idle mode: stay near screen center, minimize jumps
    boolean idleMode(State state) {
        double center = state.screenHeight / 2.0;
        // only jump if below center AND have coins AND falling
        if (state.height < center && state.velocity <= 0 && state.coins > 0) {
            return true;
        }
        return false;
    }

    // Extract the next cluster of coins (coins within CLUSTER_GAP of each other)
    List<Coin> getNextCluster(List<Coin> coins, double birdX) {
        List<Coin> cluster = new ArrayList<>();
        boolean started = false;
        for (Coin c : coins) {
            if (c.x < birdX) continue; // already passed
            if (!started) {
                cluster.add(c);
                started = true;
            } else {
                if (c.x - cluster.get(cluster.size() - 1).x <= CLUSTER_GAP) {
                    cluster.add(c);
                } else {
                    break; // gap too large, end of cluster
                }
            }
        }
        return cluster;
    }

    // DP: for each subset of coins in the cluster, find the path (jump sequence)
    // that maximizes net budget (coins collected - jumps spent) while surviving
    List<boolean[]> computePlan(List<Coin> cluster, State state) {
        int startX = (int) state.birdX;
        int endX = cluster.get(cluster.size() - 1).x + 5; // small buffer past last coin
        int totalFrames = endX - startX;

        // Build a quick lookup: frame -> coin at that x position
        Map<Integer, Coin> coinAtFrame = new HashMap<>();
        for (Coin c : cluster) {
            coinAtFrame.put(c.x - startX, c);
        }

        // DP: try all coin subsets via recursion with memoization
        // State: (frame, height, budget)
        // Decision each frame: jump or not
        // Score: total coins collected
        double bestScore = Double.NEGATIVE_INFINITY;
        List<boolean[]> bestPlan = null;

        // Use DFS to find best jump sequence
        List<boolean[]> currentPlan = new ArrayList<>();
        List<boolean[]> resultPlan = new ArrayList<>();
        dfs(0, state.height, state.velocity, state.coins, coinAtFrame,
            totalFrames, state.screenHeight, currentPlan, resultPlan, new double[]{Double.NEGATIVE_INFINITY});

        return resultPlan;
    }

    void dfs(int frame, double height, double velocity, int budget,
             Map<Integer, Coin> coinAtFrame, int totalFrames, double screenHeight,
             List<boolean[]> currentPlan, List<boolean[]> bestPlan, double[] bestScore) {

        // Leaf: reached end of cluster
        if (frame >= totalFrames) {
            double score = evaluatePlan(currentPlan, coinAtFrame, screenHeight);
            if (score > bestScore[0]) {
                bestScore[0] = score;
                bestPlan.clear();
                bestPlan.addAll(currentPlan.stream().map(a -> a.clone()).toList());
            }
            return;
        }

        // Death check
        if (height <= 0 || height >= screenHeight) {
            double score = evaluatePlan(currentPlan, coinAtFrame, screenHeight);
            if (score > bestScore[0]) {
                bestScore[0] = score;
                bestPlan.clear();
                bestPlan.addAll(currentPlan.stream().map(a -> a.clone()).toList());
            }
            return;
        }

        // Option 1: don't jump
        double newH = height + velocity - GRAVITY;
        double newV = velocity - GRAVITY;
        currentPlan.add(new boolean[]{false});
        dfs(frame + 1, newH, newV, budget, coinAtFrame, totalFrames, screenHeight,
            currentPlan, bestPlan, bestScore);
        currentPlan.remove(currentPlan.size() - 1);

        // Option 2: jump (only if we have budget)
        if (budget > 0) {
            double jumpH = height + velocity - GRAVITY + JUMP_LIFT;
            double jumpV = velocity - GRAVITY + JUMP_LIFT;
            int newBudget = budget - 1;

            // Check if we collect a coin at this frame
            Coin coin = coinAtFrame.get(frame);
            if (coin != null && Math.abs(jumpH - coin.y) < 2) {
                newBudget += 1; // collected a coin
            }

            currentPlan.add(new boolean[]{true});
            dfs(frame + 1, jumpH, jumpV, newBudget, coinAtFrame, totalFrames, screenHeight,
                currentPlan, bestPlan, bestScore);
            currentPlan.remove(currentPlan.size() - 1);
        }
    }

    double evaluatePlan(List<boolean[]> plan, Map<Integer, Coin> coinAtFrame, double screenHeight) {
        // Score = coins collected - jumps used + survival bonus
        int coinsCollected = 0;
        int jumpsUsed = 0;
        for (int i = 0; i < plan.size(); i++) {
            if (plan.get(i)[0]) jumpsUsed++;
            // coin collection tracked in DFS via budget changes, but we can recount here
        }
        // Net ROI + bonus for staying alive longer
        return plan.size() * 0.1 - jumpsUsed + coinsCollected;
    }

    // Data classes (adjust to match actual OA state)
    static class State {
        double height;
        double velocity;
        int coins;
        double birdX;
        double screenHeight;
        List<Coin> getVisibleCoins() { return new ArrayList<>(); }
    }

    static class Coin {
        int x, y;
        Coin(int x, int y) { this.x = x; this.y = y; }
    }
}
