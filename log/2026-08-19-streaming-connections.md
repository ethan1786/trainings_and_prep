# Streaming: SSE vs WebSocket, and three kinds of "connection"

**Date:** 2026-08-19
**Question that started it:** We only use SSE for the AI chatbot. Why not WebSockets? And why not a thin, cheaply-scaled layer just for streaming connections?

---

## The path

## Why SSE won

The decisive fact is that the flow is **turn-based** and only needs server→client push. Bidirectionality is the one meaningful architectural difference, and with a turn-based flow it "adds complexity without benefit."

The advantages that actually tipped it:
- **Stateless / horizontally scalable** — SSE is a plain HTTP response, so any node handles a reconnect as long as history is in a shared store. WebSocket is stateful and wants sticky sessions or a broker to survive deploys.
- **Passes through existing infra** — any HTTP proxy/CDN/firewall (buffering off). WebSocket needs WS-aware config and can be silently dropped.
- **Standard auth, free reconnect, built-in event typing.** WebSocket needs custom auth/CSRF, manual reconnect, and a hand-rolled envelope.

Revisit only for **binary** (voice/audio) or **true bidirectional control** (interrupt mid-generation) — and even then, add a small WS side-channel rather than migrate.

## My objection: the client does send messages

Right, but the resolution is that direction and *simultaneity* are different questions. One turn is: **POST the message (client→server, short) → SSE stream the answer (server→client, long)**. Two separate HTTP interactions, each unidirectional, in sequence. WebSocket's real value is *both directions at once on one connection* — which turn-based chat never uses.

Even the interactive-feeling case decomposes: when the agent asks a clarifying question, that question **is** a normal streamed response; the stream closes and the user's answer is a fresh POST. Full history is replayed each time, so the agent "remembers."

## My bigger objection: why stream at all?

The payload is a few KB. Couldn't it be one plain HTTP response?

**The trigger isn't size, it's production time.** The reply is generated token-by-token over 5–30s, and time-to-first-token is gated by classifier + tool calls. A plain response means a blank spinner for the entire generation, then a dump — with an explicit product concern that users abandon at 30s. Streaming paints first tokens in ~1–4s.

Two secondary reasons a single long response is *worse*: a 30s silent request risks proxy **idle timeouts** (SSE chunks/heartbeats prove liveness), and streaming enables **progressive typed events** and mid-stream intervention.

The test that proves the rule: the welcome/initialize path returns **plain JSON, no streaming**, because it's hydrating existing history — same size, nothing being produced over time.

## The two-hop pipeline

```
Browser ──POST /chat (SSE)──> SSR BFF ──POST /stream (SSE)──> agent server ──> LLM
```

The BFF is a **transforming proxy**: it reads the upstream SSE stream, **hydrates rich elements** (fills real data via the composition layer), and writes `data: {json}\n\n` to the browser. Not a dumb tunnel — but also not a decision-maker.

Consequence: each active chat pins **two** long-lived connections for the full 5–30s. That's the doubling behind the connection-limit pressure.

## The guardrail (the subtle part)

Framework hooks are provided by the agent library (an output-processor hook per chunk, an `abort()` primitive surfacing as a tripwire). The **actual scanner is custom** — regex, no LLM, ~1–5ms per chunk, seven categories. Notably the library's own LLM-based guardrails are **disabled** (they broke streaming in the dev studio), so the custom regex scanner is the only one running.

Mechanism: accumulate text → scan buffer → on match call `abort()` with a safe replacement → middleware emits a `guardrail-replace` event → client overwrites the message it was watching build.

**Severity-gated abort** is the clever bit: only high-severity categories abort mid-stream. Two lower-severity ones defer to finish-time because they **false-positive on partial text** — a half-streamed refusal reads like a violation. The tradeoff: abort earlier and leak less, or wait and avoid killing a good response.

And this only works *because* of streaming — text is inspectable during generation. A blocking response could only scan post-generation, after the unsafe content is fully formed.

## Two layer misattributions I made

1. **I thought the scanner was in the BFF.** No — abort and replacement both happen **on the agent server**. The BFF forwards `guardrail-replace` like any other event. Safety stays next to generation so *any* client inherits it; putting it in one BFF would protect only the web path.
2. **"The guardrail aborts the SSE stream."** It aborts the **LLM generation**, one layer beneath. The SSE connection stays open and healthy — what changes is *which event type the next message carries*. Abort the generation, not the connection.

## Why the BFF re-fetches instead of the agent injecting data

I proposed the agent attach listing data to the SSE event, saving a fetch and avoiding mismatch if data changes mid-generation. Both arguments are real; the design chose against them for four reasons:

- **Not actually a re-fetch** — grounding data (specs, for reasoning) and display data (images, formatted pricing, badges) are different shapes from different APIs. "Reuse" relocates work rather than saving it.
- **Integrity** — the LLM emits **IDs only**, validated against the tool result. Real data never passes through the model, so it can't be mutated or hallucinated. The model picks *which*; it never authors *their data*.
- **Freshness beats consistency-with-reasoning** — if price changed mid-generation, showing *current* price is correct. Passing the older snapshot makes both stale.
- **Client-agnostic** — IDs-only lets web and mobile hydrate their own display shapes. Baking web payloads in couples generation to one client's presentation.

Failure modes differ too: failed hydration → a visibly missing card; stale snapshot → confidently wrong numbers. Worse for a pricing surface.

## The connection taxonomy (the biggest correction)

I believed WebSocket holds ~5k connections vs SSE's ~50. **Apples-to-oranges.** The 50 is an application throttle (`maxConcurrentStreams`) protecting scarce LLM concurrency — not an SSE limit. At transport level both are one long-lived TCP connection with near-identical cost; capacity is FDs, memory, event-loop headroom. SSE is marginally *lighter* per idle connection.

The only genuine SSE disadvantage is the HTTP/1.1 **~6-connections-per-domain browser** cap — client-side, and removed by HTTP/2 multiplexing.

Then the third kind of connection: I remembered the DB pool was also 50 and asked why it's held open. **Coincidental number, opposite meaning.** A pooled connection is borrowed per **operation** (~5–10ms) and returned; one 20s stream borrows 6–8 times. So 50 pooled connections serve *hundreds* of streams while 50 stream slots fill fast. Pools stay open to amortize TCP+TLS+auth handshake (10–100ms) against a 5–10ms query — standard driver practice, nothing to do with streaming.

## Why not a thin streaming layer? (my proposal)

It's **on the roadmap, deferred not rejected** — route isolation onto dedicated pods/target groups, or a separate streaming BFF. Reasons it hasn't been built: measured volume is low (~1.5 chat RPS, ~15 concurrent cluster-wide), cheaper mitigations covered the risk first (per-pod limiter returning 503 before opening upstream, upstream timeouts, zombie-stream inactivity timeouts, observability gauges), and autoscaling is the intermediate step.

The subtlety worth keeping: naive autoscaling signals (CPU, RPS) are **blind to held-open streams** — the streams are ~99% idle waiting on the LLM, so CPU stays flat and no alarm fires until OOM or refusal. Hence a dedicated `active_streams` gauge feeding a **dual trigger**.

The legitimate justification for isolation isn't current volume — it's that streaming has a **fundamentally different resource profile** (I/O-bound, long-lived, connection-count-scaled) than SSR (CPU-bound, millisecond, RPS-scaled).

## Follow-up: protocol choice for dashboards

Later question about live dashboards resolved to a clean rule: **known refresh interval → polling; server-driven one-way updates → SSE; interactive simultaneous two-way → WebSocket.** HTTP/2 Server Push is deprecated in browsers and is not an alternative.

Live stock dashboards commonly use WebSocket not because "prices" require it, but because those systems *also* need dynamic subscribe/unsubscribe, acks, binary protocols, or very high update rates. Receiving quote updates alone is fine over SSE. And WebSocket isn't lower-latency by nature — it wins on **binary frames** (SSE is UTF-8; binary would need base64) and lightweight post-handshake framing.

---

## What changed in the reference

- `Part 2.1 Streaming and Connection Models` — the whole section
- `WebSocket and SSE` tool entry — corrected the connection-ceiling claim
- `Rate Limiting and Load Shedding` — load-shedding-before-upstream, gauge-based autoscaling
- `corrections.md` — five entries
- `open-questions.md` — pool latency under burst, disconnect-fix effect size
