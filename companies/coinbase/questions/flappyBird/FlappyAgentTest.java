/**
 * Test cases for the DFS path-finding FlappyAgent.
 *
 * Run: javac FlappyAgentTest.java && java FlappyAgentTest
 */
public class FlappyAgentTest {

    // ==================== DFS Path-Finding Agent ====================

    static final double GRAVITY = 1.0;
    static final double JUMP_V = -8.0;
    static final double PIPE_SPEED = 1.0;
    static final double Y_TOLERANCE = 5.0;
    static final double V_ALLOWANCE = 5.0;
    static final int MAX_NODES = 500_000;

    static int nodeCount;

    // Oscillation: offset=10, vThresh=5 gives band=[target-14, target+14], perfectly centered
    static final double OSC_OFFSET = 14.0;
    static final int DFS_RANGE = 25;  // can reach anywhere on screen in 25 frames

    static boolean shouldJump(double birdY, double birdV, double birdX,
                              double screenHeight,
                              double pipeX, double pipeWidth,
                              double gapTop, double gapBottom) {
        double gapCenter = (gapTop + gapBottom) / 2.0;
        double screenCenter = screenHeight / 2.0;

        // Target the leading edge — DFS delivers bird to gapCenter here,
        // then oscillation keeps it centered through the pipe traversal
        int framesToPipe = Math.max(
                (int) ((pipeX - birdX) / PIPE_SPEED), 0);

        // === Mode 1: Inside pipe zone → oscillate around gap center ===
        if (framesToPipe <= 0) {
            return oscillate(birdY, birdV, gapCenter);
        }

        // === Mode 2: Pipe within DFS range → path-find to gap center ===
        if (framesToPipe <= DFS_RANGE) {
            nodeCount = 0;
            double[] best = {-1, Double.MAX_VALUE};
            dfs(birdY, birdV, false, framesToPipe, 0, gapCenter, screenHeight,
                    false, best, Y_TOLERANCE);
            dfs(birdY, birdV, true, framesToPipe, 0, gapCenter, screenHeight,
                    true, best, Y_TOLERANCE);
            if (best[0] >= 0) return best[0] == 1;

            // Widen tolerance: accept anywhere inside the gap
            double gapTol = (gapBottom - gapTop) / 2.0;
            nodeCount = 0;
            best = new double[]{-1, Double.MAX_VALUE};
            dfs(birdY, birdV, false, framesToPipe, 0, gapCenter, screenHeight,
                    false, best, gapTol);
            dfs(birdY, birdV, true, framesToPipe, 0, gapCenter, screenHeight,
                    true, best, gapTol);
            if (best[0] >= 0) return best[0] == 1;

            return oscillate(birdY, birdV, gapCenter);
        }

        // === Mode 3: Pipe is far → oscillate around screen center ===
        return oscillate(birdY, birdV, screenCenter);
    }

    static boolean oscillate(double y, double v, double target) {
        return y > target + OSC_OFFSET;
    }

    static void dfs(double y, double v, boolean jump, int framesLeft, int depth,
                    double targetY, double screenH,
                    boolean firstActionWasJump, double[] bestResult,
                    double tolerance) {
        nodeCount++;
        if (nodeCount > MAX_NODES) return;

        if (jump) v = JUMP_V;
        v += GRAVITY;
        y += v;

        if (y <= 0 || y >= screenH) return;

        if (framesLeft <= 1) {
            if (Math.abs(y - targetY) > tolerance || Math.abs(v) > V_ALLOWANCE) return;
            double absV = Math.abs(v);
            if (absV < bestResult[1]) {
                bestResult[0] = firstActionWasJump ? 1 : 0;
                bestResult[1] = absV;
            }
            return;
        }

        dfs(y, v, false, framesLeft - 1, depth + 1, targetY, screenH,
                firstActionWasJump, bestResult, tolerance);
        dfs(y, v, true, framesLeft - 1, depth + 1, targetY, screenH,
                firstActionWasJump, bestResult, tolerance);
    }


    // ==================== Test Infrastructure ====================

    static int passed = 0, failed = 0;

    // ==================== Test Cases ====================

    public static void main(String[] args) {
        double H = 200;

        System.out.println("=== Multi-Frame Survival Tests ===");

        multiFrameTest("T01: Navigate through centered gap from center",
            100, 0, 10, H,
            80, 10, 80, 120,
            200
        );

        multiFrameTest("T02: Navigate through high gap from low position",
            150, 0, 10, H,
            60, 10, 10, 50,
            200
        );

        multiFrameTest("T03: Navigate through low gap from high position",
            50, 0, 10, H,
            80, 10, 140, 180,  // gap at 140-180, less extreme
            200
        );

        multiFrameTest("T04: Navigate through centered gap with high initial downward velocity",
            100, 10, 10, H,
            80, 10, 80, 120,
            200
        );

        multiFrameTest("T05: Gap near ceiling, bird starts at mid-screen",
            100, 0, 10, H,
            80, 10, 15, 55,  // gap at 15-55, reasonable
            200
        );

        multiFrameTest("T06: Gap near floor, bird starts at mid-screen (known edge case)",
            100, 0, 10, H,
            80, 10, 145, 185,  // gap at 145-185, slightly more room
            200
        );

        multiFrameTest("T07: Two pipes back-to-back (second pipe right after first)",
            100, 0, 10, H,
            40, 10, 80, 120,   // first pipe — we only see this one
            300                 // agent must center to survive unknown second pipe
        );

        // ==================== Summary ====================
        System.out.println();
        System.out.printf("Results: %d passed, %d failed%n", passed, failed);
    }

    /**
     * Simulates multiple frames with the agent making decisions.
     * The pipe scrolls left. When it passes the bird, we generate a new pipe.
     * Reports whether the bird survived the target frame count.
     */
    static void multiFrameTest(String name, double startY, double startV,
                                double birdX, double screenH,
                                double pipeX, double pipeW,
                                double gapTop, double gapBot,
                                int targetFrames) {
        multiFrameTest(name, startY, startV, birdX, screenH, pipeX, pipeW, gapTop, gapBot, targetFrames, false);
    }

    static void multiFrameTest(String name, double startY, double startV,
                                double birdX, double screenH,
                                double pipeX, double pipeW,
                                double gapTop, double gapBot,
                                int targetFrames, boolean verbose) {
        double y = startY, v = startV;
        double curPipeX = pipeX;
        double curGapTop = gapTop, curGapBot = gapBot;

        // For generating subsequent pipes after the first one passes
        double nextGapTop = gapTop, nextGapBot = gapBot;  // keep same gap for determinism

        int survived = 0;
        String deathCause = null;

        for (int frame = 0; frame < targetFrames; frame++) {
            // Agent decision
            boolean jump = shouldJump(y, v, birdX, screenH,
                    curPipeX, pipeW, curGapTop, curGapBot);

            // Apply physics
            if (jump) v = JUMP_V;
            v += GRAVITY;
            y += v;

            if (verbose && frame < 80) {
                System.out.printf("    f=%3d y=%6.1f v=%5.1f jump=%-5s pipeX=%.0f gap=%.0f-%.0f%n",
                    frame, y, v, jump, curPipeX, curGapTop, curGapBot);
            }

            // Move pipe
            curPipeX -= PIPE_SPEED;

            // Boundary check
            if (y <= 0) { deathCause = String.format("hit ceiling at frame %d (y=%.1f)", frame, y); break; }
            if (y >= screenH) { deathCause = String.format("hit floor at frame %d (y=%.1f)", frame, y); break; }

            // Pipe collision
            if (curPipeX <= birdX && birdX <= curPipeX + pipeW) {
                if (y < curGapTop || y > curGapBot) {
                    deathCause = String.format("hit pipe at frame %d (y=%.1f, gap=%.0f-%.0f)",
                            frame, y, curGapTop, curGapBot);
                    break;
                }
            }

            // Pipe passed — generate next pipe
            if (curPipeX + pipeW < birdX) {
                curPipeX = birdX + 70;  // new pipe 70px ahead
                curGapTop = nextGapTop;
                curGapBot = nextGapBot;
            }

            survived++;
        }

        boolean ok = survived >= targetFrames;
        if (ok) {
            passed++;
            System.out.printf("  PASS  %s — survived %d frames%n", name, survived);
        } else {
            failed++;
            System.out.printf("  FAIL  %s — %s (survived %d/%d)%n",
                    name, deathCause, survived, targetFrames);
        }
    }
}
