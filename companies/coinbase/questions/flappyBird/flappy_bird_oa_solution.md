class GameState {
    double birdY; // vertical position (0 = top, positive = down)
    double birdV; // vertical velocity (positive = falling)
    double birdX; // horizontal position
    double screenHeight;
    Pipe nextPipe;
}

class Pipe {
    double x; // left edge of pipe
    double width;
    double gapTop; // y of top edge of gap
    double gapBottom; // y of bottom edge of gap
}

//   Stage 1:
//   1. State/Pipe fields — what data do I have?
//   2. Coordinate system — is y=0 top or bottom?
//   3. Collision — point-based or hitbox?
//   4. What are gravity and jump velocity values?

class solution {
    // a. simple physics, no accelaration
    boolean shouldJump(GameState state) {
        double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
        return state.birdY > gapCenter;
    }

    // b. jump replaces velocity
    boolean shouldJump(GameState state) {
        int offset = 14;
        double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
        return state.birdY > gapCenter + offset;
    }

    // c. jump adds to velocity
    boolean shouldJump(GameState state) {
        double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
        double maxDownwardV = 2.0;
        return state.birdY > gapCenter && state.birdV >= maxDownwardV;
    }
    
    // d. improved jump adds to velocity, dist awareness
    boolean shouldJump(GameState state) {
        double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
        double dist = Math.abs(state.birdY - gapCenter);
        double maxDownwardV = (dist > 20) ? 0 : 2;

        return state.birdY > gapCenter && state.birdV >= maxDownwardV;
    }
    
}

//   Stage 2 (ask when you start simulation):
//   1. Jump model — replace or additive?
//   2. Physics order — position or velocity first?
//   3. Pipe speed — constant or variable?
//   4. Boundary death — at or past the edge?    

class solution {
    static final double DEATH_PENALTY = -500;
    static final double PASS_AWARD = 500;
    static final int G = 1;
    static final int JUMP = -8;

    boolean shouldJump(GameState state) {
        if (state.nextPipe.x - state.birdX > 20) {
            double gapCenter = (state.nextPipe.gapTop + state.nextPipe.gapBottom) / 2.0;
            double dist = Math.abs(state.birdY - gapCenter);
            double maxDownwardV = (dist > 20) ? 0 : 2;
            return state.birdY > gapCenter && state.birdV >= maxDownwardV;
        } else {
            double jumpScore = survivalScore(state.birdX, state.nextPipe.x, state.nextPipe.width, state.birdY, state.screenHeight, state.nextPipe.gapTop, state.nextPipe.gapBottom, state.birdV, true);
            double noJumpScore = survivalScore(state.birdX, state.nextPipe.x, state.nextPipe.width, state.birdY, state.screenHeight, state.nextPipe.gapTop, state.nextPipe.gapBottom, state.birdV, false);
            return jumpScore > noJumpScore;
        }
    }

    // assume physics order, position first
    double survivalScore(double birdX, double pipeX, double pipeWidth, double birdY, double screenHeight, double gapTop, double gapBottom, double v, boolean willJump) {
        if (birdX >= pipeX + pipeWidth) {
            return PASS_AWARD;
        }
        if (birdY <= 0 || birdY >= screenHeight || (birdX >= pipeX && (birdY <= gapTop || birdY >= gapBottom))) {
            return DEATH_PENALTY;
        }
        birdY += v;
        v += G;
        if (willJump) {
            v += JUMP;
        }
        double gapCenter = (gapTop + gapBottom) / 2.0;
        double baseScore = (birdX >= pipeX ? 20 : 10) - Math.abs(birdY - gapCenter) * 0.5;
// free fall simulation
        return baseScore + survivalScore(birdX + 1, pipeX, pipeWidth, birdY, screenHeight, gapTop, gapBottom, v, false);

// dfs
        double jumpScore = survivalScore(birdX + 1, pipeX, pipeWidth, birdY, screenHeight, gapTop, gapBottom, v, true);
        double noJumpScore = survivalScore(birdX + 1, pipeX, pipeWidth, birdY, screenHeight, gapTop, gapBottom, v, false);
        return Math.max(jumpScore, noJumpScore) + baseScore;

    }
}
