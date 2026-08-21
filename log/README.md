# Study Log

Append-only, chronological. Each entry records **the reasoning path** of one study session — including wrong turns, pushback, and what got corrected — not just conclusions. Conclusions live in `../design_knowledge_base.md`.

Never revise an entry. If understanding changes later, write a new entry and add a line to `../corrections.md`.

## Entries

| Date | Topic | Starting question |
|---|---|---|
| 2026-08-11 | [Kafka partitioning and consumer scaling](2026-08-11-kafka-partitions.md) | Can I pin a topic's publishes to one partition for ordering? |
| 2026-08-12 | [Search platform: ingestion and index lifecycle](2026-08-12-opensearch-cgsp.md) | Search engines are expensive to write — how is the index kept current? |
| 2026-08-18 | [MongoDB: fit, choice, tuning](2026-08-18-mongodb-usage.md) | Is it just a persistent caching store? |
| 2026-08-19 | [Streaming: SSE vs WebSocket, three kinds of connection](2026-08-19-streaming-connections.md) | Why SSE and not WebSockets? Why not a thin streaming layer? |
| 2026-08-19 | [GraphQL Federation, gRPC, and where logic belongs](2026-08-19-graphql-grpc-composition.md) | We don't have gRPC — should we? |
| 2026-08-19 | [S3 / object storage](2026-08-19-s3-object-storage.md) | What are the actual use cases? |
| 2026-08-19 | [Coordination stores and stream processing](2026-08-19-coordination-flink.md) | What are ZooKeeper and etcd? When would we need Flink? |
| 2026-08-19 | [Caching: layers, strategies, when it's needed](2026-08-19-caching-strategies.md) | Are the DB's own caches usually disabled? |
| 2026-08-19 | [Latency investigation decision tree](2026-08-19-latency-investigation.md) | How do you find the bottleneck when many layers are involved? |
| 2026-08-19 | [Throughput and capacity planning](2026-08-19-capacity-planning.md) | Will it hold at 10x? |
| 2026-08-19 | [Part 3 decision layer](2026-08-19-part3-decision-layer.md) | Tool entries are descriptive — bring them to the Part 1 standard |
| 2026-08-21 | [Caching: compact design principles](2026-08-21-caching-design-principles.md) | What are the design principles before moving on? |
| 2026-08-21 | [Caching: design-time estimation](2026-08-21-caching-design-time-estimation.md) | Should caching be included before production metrics exist? |

## Entry template

```markdown
# Topic

**Date:** YYYY-MM-DD
**Question that started it:** ...

---

## The path
What I believed going in, what I found, in the order I found it.

## The wrong turn worth keeping
What I got wrong and why it was tempting.

## Pressure I applied
Objections I raised and how they resolved.

---

## What changed in the reference
- Section touched — what was added or corrected
- `corrections.md` — entries added
- `open-questions.md` — items added
```
