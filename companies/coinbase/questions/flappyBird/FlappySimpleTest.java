/**
 * Test simple agents under both physics models:
 *   A) v = JUMP_V  (replacement)
 *   B) v += JUMP_V (additive)
 *
 * Run: javac FlappySimpleTest.java && java FlappySimpleTest
 */
public class FlappySimpleTest {

    static final double GRAVITY = 1.0;
    static final double JUMP_V = -8.0;
    static final double PIPE_SPEED = 1.0;
    static final int OFFSET = 14;
    static final int MAX_V = 8;

    // Agent 1: simple offset (no velocity cap)
    static boolean shouldJumpSimple(double birdY, double birdV, double screenH,
                                     double gapTop, double gapBottom) {
        double gapCenter = (gapTop + gapBottom) / 2.0;
        double trigger = Math.max(Math.min(gapCenter + OFFSET, screenH - OFFSET), OFFSET);
        return birdY > trigger;
    }

    // Agent 2: with velocity cap (for additive jump)
    static boolean shouldJumpCapped(double birdY, double birdV, double screenH,
                                     double gapTop, double gapBottom) {
        double gapCenter = (gapTop + gapBottom) / 2.0;
        double trigger = Math.max(Math.min(gapCenter + OFFSET, screenH - OFFSET), OFFSET);
        return birdY > trigger && birdV > -MAX_V;
    }

    // ==================== Test Infrastructure ====================

    static int passed = 0, failed = 0;

    public static void main(String[] args) {
        double H = 200;

        // ===== Replacement physics: v = JUMP_V =====
        System.out.println("========================================");
        System.out.println("  REPLACEMENT PHYSICS (v = JUMP_V)");
        System.out.println("========================================\n");

        System.out.println("--- Simple agent (no cap) ---");
        runAllTests(H, false, false);

        System.out.println("\n--- Capped agent (with MAX_V) ---");
        runAllTests(H, false, true);

        // ===== Additive physics: v += JUMP_V =====
        System.out.println("\n========================================");
        System.out.println("  ADDITIVE PHYSICS (v += JUMP_V)");
        System.out.println("========================================\n");

        System.out.println("--- Simple agent (no cap) ---");
        runAllTests(H, true, false);

        System.out.println("\n--- Capped agent (with MAX_V) ---");
        runAllTests(H, true, true);

        System.out.printf("\n\nTotal: %d passed, %d failed%n", passed, failed);
    }

    static void runAllTests(double H, boolean additive, boolean capped) {
        multiFrameTest("T01: Centered gap from center",
            100, 0, 10, H, 80, 10, 80, 120, 200, additive, capped);
        multiFrameTest("T02: High gap from low position",
            150, 0, 10, H, 60, 10, 10, 50, 200, additive, capped);
        multiFrameTest("T03: Low gap from high position",
            50, 0, 10, H, 80, 10, 140, 180, 200, additive, capped);
        multiFrameTest("T04: Centered gap with high downward velocity",
            100, 10, 10, H, 80, 10, 80, 120, 200, additive, capped);
        multiFrameTest("T05: Gap near ceiling",
            100, 0, 10, H, 80, 10, 15, 55, 200, additive, capped);
        multiFrameTest("T06: Gap near floor",
            100, 0, 10, H, 80, 10, 145, 185, 200, additive, capped);
        multiFrameTest("T07: Back-to-back pipes",
            100, 0, 10, H, 40, 10, 80, 120, 300, additive, capped);
        // Additional stress tests for additive physics
        multiFrameTest("T08: Bird starts with high upward velocity",
            100, -10, 10, H, 80, 10, 80, 120, 200, additive, capped);
        multiFrameTest("T09: Bird starts with high downward velocity",
            100, 15, 10, H, 80, 10, 80, 120, 200, additive, capped);
        multiFrameTest("T10: Narrow gap (30px)",
            100, 0, 10, H, 80, 10, 85, 115, 200, additive, capped);
        multiFrameTest("T11: Very narrow gap (20px)",
            100, 0, 10, H, 80, 10, 90, 110, 200, additive, capped);
        multiFrameTest("T12: Pipe very far away",
            100, 0, 10, H, 200, 10, 80, 120, 400, additive, capped);
    }

    static void multiFrameTest(String name, double startY, double startV,
                                double birdX, double screenH,
                                double pipeX, double pipeW,
                                double gapTop, double gapBot,
                                int targetFrames,
                                boolean additive, boolean capped) {
        double y = startY, v = startV;
        double curPipeX = pipeX;
        double curGapTop = gapTop, curGapBot = gapBot;
        int survived = 0;
        String deathCause = null;

        for (int frame = 0; frame < targetFrames; frame++) {
            boolean jump = capped
                    ? shouldJumpCapped(y, v, screenH, curGapTop, curGapBot)
                    : shouldJumpSimple(y, v, screenH, curGapTop, curGapBot);

            // Physics: replacement vs additive
            if (jump) {
                if (additive) v += JUMP_V;
                else v = JUMP_V;
            }
            v += GRAVITY;
            y += v;

            curPipeX -= PIPE_SPEED;

            if (y <= 0) { deathCause = String.format("ceiling at f=%d y=%.1f v=%.1f", frame, y, v); break; }
            if (y >= screenH) { deathCause = String.format("floor at f=%d y=%.1f v=%.1f", frame, y, v); break; }

            if (curPipeX <= birdX && birdX <= curPipeX + pipeW) {
                if (y < curGapTop || y > curGapBot) {
                    deathCause = String.format("pipe at f=%d y=%.1f v=%.1f gap=%.0f-%.0f", frame, y, v, curGapTop, curGapBot);
                    break;
                }
            }

            if (curPipeX + pipeW < birdX) {
                curPipeX = birdX + 70;
                curGapTop = gapTop;
                curGapBot = gapBot;
            }
            survived++;
        }

        if (survived >= targetFrames) {
            passed++;
            System.out.printf("  PASS  %s%n", name);
        } else {
            failed++;
            System.out.printf("  FAIL  %s — %s (survived %d/%d)%n", name, deathCause, survived, targetFrames);
        }
    }
}
