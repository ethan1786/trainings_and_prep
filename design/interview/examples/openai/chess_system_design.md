# Online Chess System Design

**Category:** System Design — **#2 Most Frequent SD (7+ occurrences)**
**Difficulty:** Medium
**Time:** 60 min
**Key Topics:** WebSocket, Matchmaking (Elo), Game State Machine, Real-Time Communication, Reconnection

---

## Problem Variants (3 posts, all similar)

### Version 1: Focus on Real-Time + Matchmaking
- Matchmaking by Elo (bucketed queues, widening range)
- Real-time WebSocket channel for moves
- Reconnect handling, duplicate/out-of-order messages
- Deep dive into 1-2 areas

### Version 2: Full Platform
- Auth, create game, matchmaking, friend invite, spectating, chat, replay
- Game lifecycle: move validation, time control (5+0, 3+2), undo/draw/resign
- Anti-cheat, Elo, multi-region

### Version 3: Consistency Focus
- Accept exactly one legal move per turn
- Handle duplicate submissions, out-of-order messages
- Horizontal scaling, hot games, sharding

---

## Solution

### High-Level Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Clients    │────▶│   API Gateway   │────▶│  Auth Service    │
│  (Web/Mobile)│     │  (HTTP + WS)    │     └──────────────────┘
└──────────────┘     └────────┬────────┘
                              │
              ┌───────────────┼───────────────────┐
              ▼               ▼                   ▼
    ┌──────────────┐  ┌──────────────┐  ┌────────────────┐
    │ Matchmaking  │  │ Game Service │  │  WebSocket     │
    │   Service    │  │ (State +     │  │  Manager       │
    │              │  │  Validation) │  │  (Connections) │
    └──────┬───────┘  └──────┬───────┘  └────────┬───────┘
           │                 │                    │
           ▼                 ▼                    │
    ┌──────────────┐  ┌──────────────┐           │
    │ Match Queue  │  │  Game DB     │           │
    │ (Redis)      │  │  (Postgres)  │           │
    └──────────────┘  └──────────────┘           │
                              │                    │
                              ▼                    ▼
                      ┌──────────────┐   ┌──────────────┐
                      │  Move History│   │   Pub/Sub    │
                      │  (append-only│   │  (Redis/Kafka)│
                      └──────────────┘   └──────────────┘
```

### Core Components

| Component | Responsibility |
|---|---|
| **API Gateway** | HTTP for auth/history, WebSocket upgrade for real-time gameplay |
| **Auth Service** | Login, session management, JWT issuance |
| **Matchmaking Service** | Elo-based pairing, queue management |
| **Game Service** | Authoritative game state, move validation, turn management, clock |
| **WebSocket Manager** | Maintains persistent connections, routes messages to/from Game Service |
| **Pub/Sub** | Fan-out game events to players + spectators |
| **Game DB (Postgres)** | Game records, user profiles, Elo ratings |
| **Redis** | Match queue, active game state cache, connection mapping (user → WS server) |

---

### Key APIs

```
# HTTP APIs
POST   /api/games/queue          — join matchmaking queue
DELETE /api/games/queue          — leave queue
GET    /api/games/{id}           — get game state (for reconnect or history)
GET    /api/games/{id}/moves     — get move history (PGN)
POST   /api/games/{id}/resign    — resign game
POST   /api/games/{id}/draw      — offer/accept draw

# WebSocket Messages (bidirectional)
Client → Server:
  { type: "move", game_id, from: "e2", to: "e4", timestamp }
  { type: "resign", game_id }
  { type: "draw_offer", game_id }

Server → Client:
  { type: "move_ack", game_id, move_number, server_timestamp }
  { type: "opponent_move", game_id, from: "e7", to: "e5", clock_remaining }
  { type: "game_over", game_id, result: "white_wins", reason: "checkmate" }
  { type: "clock_update", game_id, white_remaining, black_remaining }
  { type: "error", message: "illegal_move" }
```

---

### Data Model

```sql
-- User
CREATE TABLE users (
    id          UUID PRIMARY KEY,
    username    VARCHAR UNIQUE NOT NULL,
    elo_rating  INT DEFAULT 1200,
    games_played INT DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Game
CREATE TABLE games (
    id          UUID PRIMARY KEY,
    white_id    UUID REFERENCES users(id),
    black_id    UUID REFERENCES users(id),
    status      VARCHAR NOT NULL,  -- WAITING, ACTIVE, COMPLETED, ABANDONED
    result      VARCHAR,           -- WHITE_WIN, BLACK_WIN, DRAW, ABANDONED
    result_reason VARCHAR,         -- CHECKMATE, TIMEOUT, RESIGN, STALEMATE, AGREEMENT
    time_control VARCHAR,          -- "5+0", "3+2", "10+5"
    initial_time_ms BIGINT,       -- initial clock per player
    increment_ms BIGINT,          -- increment per move
    fen         VARCHAR,           -- current board state (FEN notation)
    turn        VARCHAR,           -- WHITE or BLACK
    move_count  INT DEFAULT 0,
    started_at  TIMESTAMP,
    ended_at    TIMESTAMP,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Move History (append-only)
CREATE TABLE moves (
    id          BIGSERIAL PRIMARY KEY,
    game_id     UUID REFERENCES games(id),
    move_number INT NOT NULL,
    player_id   UUID REFERENCES users(id),
    notation    VARCHAR NOT NULL,  -- "e2e4", "Nf3", etc.
    fen_after   VARCHAR,           -- board state after move
    clock_remaining_ms BIGINT,    -- player's remaining time after move
    timestamp   TIMESTAMP NOT NULL,
    UNIQUE(game_id, move_number)   -- exactly one move per turn
);
```

---

### Matchmaking Deep Dive

**Elo-Based Bucketed Queue:**

```
Approach:
1. Player joins queue with their Elo rating (e.g., 1450)
2. Place into bucket: Elo / 100 = bucket 14 (covers 1400-1499)
3. Look for opponent in same bucket first
4. Every 5 seconds waiting: widen search ± 1 bucket
5. After 30 seconds: widen to ± 3 buckets
6. After 60 seconds: match with anyone available

Data structure: Redis sorted set per time control
  Key: "queue:5+0"
  Score: Elo rating
  Value: user_id + queue_join_time

Match logic:
  ZRANGEBYSCORE "queue:5+0" (elo - range) (elo + range)
  If result found → pop both, create game
  Else → widen range, retry on next tick
```

**Why bucketed/range approach:**
- Pure Elo sort (match closest) creates head-of-line blocking
- Widening over time balances fairness (good match) vs speed (fast match)
- Different queues per time control (blitz, rapid, classical)

---

### Game State Machine

```
WAITING → ACTIVE → COMPLETED
                 → ABANDONED (player disconnected, didn't return)

Completion reasons:
- CHECKMATE (one player wins)
- TIMEOUT (clock runs out)
- RESIGN (player resigns)
- STALEMATE (draw)
- DRAW_AGREEMENT (both agree)
- DRAW_REPETITION (threefold repetition)
- DRAW_50_MOVE (50 moves without capture/pawn move)
- INSUFFICIENT_MATERIAL (K vs K, K+B vs K, etc.)
```

---

### Move Validation & Turn Management

**Server is AUTHORITATIVE** — client sends proposed move, server validates:

```java
class GameEngine {
    MoveResult submitMove(Game game, String playerId, String from, String to) {
        // 1. Check it's this player's turn
        if (!game.getCurrentTurn().equals(playerId)) 
            return MoveResult.error("not_your_turn");
        
        // 2. Validate move is legal on current board state
        if (!chessRules.isLegalMove(game.getFen(), from, to))
            return MoveResult.error("illegal_move");
        
        // 3. Check clock hasn't expired
        if (game.getClockRemaining(playerId) <= 0)
            return MoveResult.timeout(getOpponent(playerId));
        
        // 4. Apply move — update FEN, switch turn, adjust clock
        String newFen = chessRules.applyMove(game.getFen(), from, to);
        game.setFen(newFen);
        game.switchTurn();
        game.deductClock(playerId, elapsedSinceLastMove);
        game.addIncrement(playerId);
        
        // 5. Check game-end conditions
        if (chessRules.isCheckmate(newFen)) return MoveResult.gameOver("checkmate");
        if (chessRules.isStalemate(newFen)) return MoveResult.gameOver("stalemate");
        
        // 6. Persist move + broadcast to opponent/spectators
        persistMove(game, from, to, newFen);
        broadcastMove(game, from, to);
        
        return MoveResult.success();
    }
}
```

**Concurrency — exactly one move per turn:**

```sql
-- Optimistic locking: only one move can be inserted per move_number
INSERT INTO moves (game_id, move_number, player_id, notation, ...)
VALUES (?, ?, ?, ?, ...)
-- UNIQUE(game_id, move_number) constraint prevents duplicates
-- If constraint violation → move was already made (duplicate/race), reject
```

---

### Real-Time Communication (WebSocket)

**Connection flow:**
```
1. Client connects via WebSocket: ws://api.chess.com/ws?token=JWT
2. Server validates JWT, maps user_id → WS connection in Redis
3. When game starts: both players' WS connections are linked to game_id
4. Moves flow: Client → WS Manager → Game Service → validate → WS Manager → Opponent
5. Spectators: subscribe to game_id via Pub/Sub, receive move broadcasts
```

**Reconnect handling:**
```
1. Client disconnects (network issue)
2. Server starts "disconnect timer" (e.g., 60 seconds)
3. Client reconnects with same JWT
4. Server: look up user_id → find active game → send current game state (FEN + clock)
5. If timer expires before reconnect → flag as ABANDONED or auto-forfeit
```

**Duplicate/out-of-order messages:**
- Each move has a `move_number` — server rejects if move_number doesn't match expected next move
- Client retries on timeout — server deduplicates via UNIQUE constraint
- At-most-once for game moves (only one legal move per turn position)

---

### Clock Management

```
Server-side clock (authoritative):
- When player makes a move: 
    elapsed = now - last_move_timestamp
    player.clock -= elapsed
    player.clock += increment (if applicable)
- Between moves: server tracks whose turn it is and when the turn started
- Clock runs out → server auto-declares timeout winner

Client-side clock (display only):
- Client receives clock_remaining from server after each move
- Client counts down locally for display
- Client's clock is NOT authoritative — server decides timeout

Why server-authoritative:
- Client can cheat by pausing their local clock
- Network latency causes clock drift — server compensates
```

---

### Scalability

**Horizontal scaling:**
- Game Service is stateless — game state in Redis (hot) + Postgres (persistent)
- Multiple WS Manager instances — Redis Pub/Sub for cross-instance communication
- Matchmaking is a single logical queue but can be sharded by time control

**Hot games (spectating viral games):**
- Pub/Sub fan-out for spectators (not direct WS per spectator from Game Service)
- CDN/cache for board state if spectator count is very high
- Separate "spectator stream" from "player stream"

**Sharding:**
- Shard games by game_id (hash)
- User lookup: Redis mapping user_id → game_id → which server handles it
- No cross-shard transactions needed (one game = one shard)

---

### Key Trade-Offs to Mention

| Decision | Trade-Off |
|---|---|
| Server-authoritative state | More server load, but prevents cheating |
| WebSocket for moves | Real-time, but stateful connections are harder to scale |
| Redis for active game state | Fast, but must persist to Postgres for durability |
| Elo widening over time | Fast matches vs fair matches — user configurable? |
| Clock on server | Fair, but network latency adds ~50-100ms per move to clock |
| Pub/Sub for spectators | Scales better than direct WS, slight latency increase |

---

### Anti-Cheat (Mention if Time)

- **Engine detection:** Statistical analysis — move correlation with engine top choices
- **Time analysis:** Consistent move times (humans vary; engines are steady)
- **Sandboxing:** Don't allow clipboard paste during game
- **Post-game review:** Flag suspicious games for human/ML review
- Not a real-time block — too expensive. Flag and review async.

---

### Connection to Your Experience

- **WebSocket + state management** = similar to your real-time notification/event patterns
- **Game state machine** = similar to your transaction/payment state machine
- **Reconnect handling** = similar to webhook "what if it never arrives" reconciliation
- **Idempotency (one move per turn)** = DB unique constraint, same as idempotency key pattern
- **Matchmaking queue** = similar to job scheduling / priority queue patterns
