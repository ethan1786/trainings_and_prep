# NVIDIA — Senior Cloud Software Engineer (NGC Team)

> **Interview prep doc.** Position: Senior Cloud Software Engineer, NGC.
> Team: NGC (NVIDIA GPU Cloud) — catalog/registry platform for GPU-optimized containers and models.
> Salary range: L4 (Senior) and L5 (Staff).
> Last updated: May 27, 2026

---

## Interview Status

- **First round done** (May 14) — 2 technical rounds with ICs, went well
- **Final round scheduled:** Thu May 29 + Fri May 30, 12:00-3:00 PM each day
- **Platform:** Microsoft Teams
- **No outside tools (ChatGPT etc.)** — explicitly stated
- **Format:** No standard structure. Conversational, project deep-dive, possible coding (easy/medium), system design discussion.

---

## Role Context

- **Java-first role**: Core Java (Collections, Streams, Concurrency, I/O) explicitly required
- **Team: NGC** — catalog/registry platform (Docker Hub for GPU software), NOT fleet management
- Key skills: large-scale distributed systems, REST API/gRPC design, RDBMS + NoSQL, cloud technologies, streaming
- **NOT a GPU/CUDA/hardware role** — cloud services platform layer
- Salary range spans L4 (Senior) and L5 (Staff) — leveling TBD

**Your fit (near-perfect match):**
- ✅ Core Java 13 years
- ✅ Large-scale distributed systems (API Mod: 8K rpm, circuit breakers, orchestration)
- ✅ REST API design (RFC standards, API contracts for 10+ consuming teams)
- ✅ RDBMS + NoSQL (MySQL, Redis, Mongo)
- ✅ Cloud (AWS: ECS/EKS, SQS/SNS, S3, RDS, Terraform)
- ✅ Streaming (Kafka event pipelines)
- ✅ Operational experience (SLOs, Datadog, on-call)

**Interview approach (learned from first round + HashiCorp):**
- Lead with TECHNICAL DEPTH, not leadership stories
- "Here's what I built, here's the technical decision, here's why it works at scale"
- Let interviewer discover leadership through follow-ups
- If unfamiliar tech comes up: "Let me reason through this from first principles"

---

## Coding Prep

No need for hard LC. Focus on clean, bug-free implementation of medium problems.

#### HashMap from Scratch (classic "no library" question)

```java
class MyHashMap<K, V> {
    private static final int DEFAULT_CAPACITY = 16;
    private Node<K, V>[] buckets;
    private int size;

    MyHashMap() {
        buckets = new Node[DEFAULT_CAPACITY];
    }

    void put(K key, V value) {
        int index = hash(key);
        Node<K, V> current = buckets[index];
        // Check if key exists — update
        while (current != null) {
            if (current.key.equals(key)) {
                current.value = value;
                return;
            }
            current = current.next;
        }
        // Key not found — insert at head
        Node<K, V> newNode = new Node<>(key, value);
        newNode.next = buckets[index];
        buckets[index] = newNode;
        size++;
        // Optional: resize if load factor > 0.75
    }

    V get(K key) {
        int index = hash(key);
        Node<K, V> current = buckets[index];
        while (current != null) {
            if (current.key.equals(key)) return current.value;
            current = current.next;
        }
        return null;
    }

    V remove(K key) {
        int index = hash(key);
        Node<K, V> current = buckets[index];
        Node<K, V> prev = null;
        while (current != null) {
            if (current.key.equals(key)) {
                if (prev == null) buckets[index] = current.next;
                else prev.next = current.next;
                size--;
                return current.value;
            }
            prev = current;
            current = current.next;
        }
        return null;
    }

    private int hash(K key) {
        return Math.abs(key.hashCode() % buckets.length);
    }

    static class Node<K, V> {
        K key;
        V value;
        Node<K, V> next;
        Node(K key, V value) { this.key = key; this.value = value; }
    }
}
```

**Key points if asked follow-ups:**
- **Hash collision:** chaining with linked list (simple). Java 8+ uses tree (red-black) when bucket exceeds 8 nodes.
- **Load factor:** resize (double capacity, rehash all entries) when size/capacity > 0.75
- **Why Math.abs?** hashCode() can be negative. Modulo of negative = negative index.
- **Equals + hashCode contract:** if `a.equals(b)` then `a.hashCode() == b.hashCode()`. Broken contract = lost entries.
- **Thread safety:** this isn't thread-safe. ConcurrentHashMap uses lock striping (segment-level locks) for concurrency.

**Priority list (do 3-4/day Sat-Tue, 15-20 min each):**

| # | LC # | Problem | Pattern | Why |
|---|---|---|---|---|
| 1 | 71 | Simplify Path | String + stack | File path processing — very cloud-infra |
| 2 | 56 | Merge Intervals | Sort + merge | Scheduling / resource allocation |
| 3 | 253 | Meeting Rooms II | Min-heap | Resource allocation (GPU slots!) |
| 4 | 207 | Course Schedule | Topological sort | Job dependency graphs |
| 5 | 394 | Decode String | Stack + string | String processing + stack |
| 6 | 49 | Group Anagrams | HashMap + sorting | HashMap grouping |
| 7 | 3 | Longest Substring Without Repeating | Sliding window + set | Classic window |
| 8 | 146 | LRU Cache | HashMap + DLL | Design question |
| 9 | 347 | Top K Frequent Elements | HashMap + heap/bucket | Counting + ranking |
| 10 | 468 | Validate IP Address | String parsing | Parsing + validation |
| 11 | 1166 | Design File System | Trie / HashMap | Cloud storage relevant |
| 12 | 227 | Basic Calculator II | Stack + parsing | Expression evaluation |

**Full reference by category:**

**String Processing (most likely per forum intel):**

| LC # | Problem | Difficulty | Pattern |
|---|---|---|---|
| 3 | Longest Substring Without Repeating Characters | Medium | Sliding window + set |
| 49 | Group Anagrams | Medium | HashMap + sorting |
| 5 | Longest Palindromic Substring | Medium | Expand from center |
| 14 | Longest Common Prefix | Easy | String comparison |
| 394 | Decode String | Medium | Stack + string building |
| 71 | Simplify Path | Medium | Stack + split (file path!) |
| 227 | Basic Calculator II | Medium | Stack + parsing |
| 468 | Validate IP Address | Medium | String parsing + validation |
| 8 | String to Integer (atoi) | Medium | Parsing edge cases |
| 722 | Remove Comments | Medium | State machine + string |

**HashMap / Counting:**

| LC # | Problem | Difficulty | Pattern |
|---|---|---|---|
| 1 | Two Sum | Easy | HashMap lookup |
| 560 | Subarray Sum Equals K | Medium | Prefix sum + HashMap |
| 347 | Top K Frequent Elements | Medium | HashMap + heap or bucket sort |
| 380 | Insert Delete GetRandom O(1) | Medium | HashMap + array |
| 146 | LRU Cache | Medium | HashMap + DLL |
| 128 | Longest Consecutive Sequence | Medium | HashSet |

**Array / Sliding Window / Two Pointers:**

| LC # | Problem | Difficulty | Pattern |
|---|---|---|---|
| 15 | 3Sum | Medium | Sort + two pointers |
| 56 | Merge Intervals | Medium | Sort + merge (scheduling!) |
| 253 | Meeting Rooms II | Medium | Min-heap (resource allocation!) |
| 238 | Product of Array Except Self | Medium | Prefix/suffix |
| 11 | Container With Most Water | Medium | Two pointers |
| 53 | Maximum Subarray | Medium | Kadane's |

**Graph / BFS / DFS (dependencies, scheduling):**

| LC # | Problem | Difficulty | Pattern |
|---|---|---|---|
| 207 | Course Schedule | Medium | Topological sort (job deps!) |
| 210 | Course Schedule II | Medium | Topo sort — return the order |
| 200 | Number of Islands | Medium | BFS/DFS on grid |
| 994 | Rotting Oranges | Medium | Multi-source BFS |
| 133 | Clone Graph | Medium | BFS + HashMap |

**Design / OOD:**

| LC # | Problem | Difficulty | Pattern |
|---|---|---|---|
| 355 | Design Twitter | Medium | HashMap + merge k sorted |
| 362 | Design Hit Counter | Medium | Queue / circular buffer |
| 1166 | Design File System | Medium | Trie / HashMap (cloud storage!) |
| 981 | Time Based Key-Value Store | Medium | HashMap + binary search |

### Technical Deep-Dive Prep — Resume Bullet by Bullet

They'll pick something from your resume and drill. For each technology/concept below, be ready to explain HOW it works, not just that you used it.

**Kubernetes / EKS:**

- **Pod lifecycle: Pending → Running → Succeeded/Failed. What triggers each transition?**
  - Pending: pod accepted by the cluster but not yet scheduled (waiting for node resources, image pull, or volume mount)
  - Running: at least one container is running. Kubelet on the assigned node pulled the image and started the process.
  - Succeeded: all containers exited with code 0 (for Jobs/batch). For long-running pods, they stay Running until killed.
  - Failed: at least one container exited non-zero or was killed by the system (OOMKilled, evicted).
  - Key point: the scheduler assigns pods to nodes based on resource requests, affinity rules, and taints/tolerations.

- **Deployments vs StatefulSets — when to use each?**
  - Deployment: stateless services. Pods are interchangeable, can be killed/replaced freely. Horizontal scaling is trivial.
  - StatefulSet: stateful workloads (databases, Kafka brokers, ZooKeeper). Pods get stable network identity (pod-0, pod-1), persistent volume claims that survive restarts, and ordered startup/shutdown.
  - Rule of thumb: if the pod needs stable storage or identity, use StatefulSet. Everything else is Deployment.

- **Rolling update strategy: maxSurge, maxUnavailable — how to do zero-downtime deploys?**
  - maxSurge: how many extra pods can exist above desired count during rollout (e.g., 1 means create 1 new pod before killing an old one)
  - maxUnavailable: how many pods can be unavailable during rollout (0 = never drop below desired count)
  - Zero-downtime: set maxUnavailable=0, maxSurge=1. New pod starts, passes readiness probe, gets traffic. Only then old pod terminates.
  - Also need proper readiness probes — if the new pod fails readiness, rollout pauses automatically.

- **Readiness vs Liveness probes?**
  - Readiness: "Can this pod serve traffic?" Fails → pod removed from Service endpoints, no traffic routed to it. Pod stays alive.
  - Liveness: "Is this pod stuck/deadlocked?" Fails → kubelet kills and restarts the container.
  - Common mistake: using liveness for slow startup — pod gets killed in a restart loop. Use startup probe or generous initialDelaySeconds instead.
  - My JVM warmup example: readiness probe calls a `/health/ready` endpoint that returns 200 only after the warmup routine (synthetic GraphQL queries) completes. Traffic doesn't flow until JIT has compiled hot paths.

- **HPA (Horizontal Pod Autoscaler) — what metrics to scale on?**
  - Default: CPU utilization (e.g., scale up when avg CPU > 70%)
  - Better for services: custom metrics — request latency p99, queue depth, error rate
  - For our orchestration service: scaled on request latency p99. When latency rose, we added pods before CPU was maxed — latency is a leading indicator, CPU is lagging.
  - For Kafka consumers: scale on consumer lag (messages behind). Lag growing → add consumers.
  - HPA checks metrics every 15s by default. Cooldown prevents thrashing (scale-down stabilization window).

- **Resource requests vs limits?**
  - Requests: guaranteed minimum. Scheduler uses this to place pods. Pod won't be scheduled unless a node has this much free.
  - Limits: hard ceiling. If pod exceeds memory limit → OOMKilled. If exceeds CPU limit → throttled (not killed).
  - Best practice: set requests = typical usage, limits = peak burst. Don't set limits too low or you get unnecessary OOMKills under load spikes.
  - No limits set at all → pod can consume entire node's resources, starving neighbors. Always set at least memory limits.

- **Service discovery?**
  - ClusterIP Service: gets a virtual IP + DNS entry (my-service.my-namespace.svc.cluster.local). kube-proxy routes traffic to healthy pod endpoints.
  - Headless Service (clusterIP: None): no virtual IP. DNS returns all pod IPs directly. Used for StatefulSets where clients need to address specific pods.
  - External: LoadBalancer type provisions cloud LB. Ingress controller for HTTP routing rules.

- **Your story:** "We deployed on EKS. Each microservice is a Deployment with readiness probes that validate JVM warmup — I built a warmup routine that sends synthetic queries through the full pipeline before the readiness endpoint returns 200. We use HPA scaling on request latency p99 as a custom metric. Rolling updates with maxUnavailable=0 for zero-downtime. Each service has CPU requests matching steady-state usage, memory limits set to 2x typical heap to absorb GC spikes without OOMKill."

**Terraform / Infrastructure as Code:**

- **State file — what is it, where do you store it, what if two people apply simultaneously?**
  - State file: JSON that maps your Terraform config to real-world resources. Tracks resource IDs, metadata, dependencies.
  - Remote state: stored in S3 bucket with DynamoDB table for locking. Never commit state to git (contains secrets, gets stale).
  - Concurrent apply: DynamoDB lock prevents two `terraform apply` from running simultaneously. Second person gets "state locked" error and must wait.
  - If lock gets stuck (crashed apply): `terraform force-unlock <lock-id>` — but dangerous, verify no apply is actually running.

- **Modules — how to structure reusable infra?**
  - Module = reusable Terraform package with inputs (variables) and outputs.
  - Structure: shared modules for common patterns (e.g., `modules/ecs-service`, `modules/rds-postgres`, `modules/sqs-with-dlq`). Each team composes these into their service config.
  - Root module per service/environment: `services/lead-service/prod/main.tf` calls shared modules with service-specific variables.
  - Versioning: modules stored in separate repo or registry, pinned to version. Breaking changes require version bump.

- **Plan → Apply workflow?**
  - `terraform plan`: reads current state, compares to config, generates an execution plan showing what will be created/modified/destroyed. No changes made.
  - `terraform apply`: executes the plan. Makes actual API calls to AWS/GCP/etc.
  - In CI/CD: plan runs on PR (visible in PR comment), apply runs on merge to main. Human reviews plan before merge.
  - `terraform plan -out=plan.bin`: saves plan to file, `terraform apply plan.bin` ensures exactly that plan is applied (no drift between plan and apply).

- **Drift detection?**
  - Drift: someone manually changes infrastructure via AWS console, CLI, or another tool. State no longer matches reality.
  - Detection: `terraform plan` shows diff — "this resource was changed outside Terraform, will be reverted."
  - Options: (1) let Terraform revert it (enforce IaC as source of truth), (2) `terraform import` to adopt the manual change into state, (3) `terraform refresh` to update state without changing infra.
  - Prevention: restrict AWS console write access via IAM. All changes go through Terraform in CI.

- **Your story:** "We use Terraform for all AWS provisioning — VPCs, EKS clusters, RDS instances, SQS queues. State stored in S3 with DynamoDB locking. Each service team owns their Terraform module, shared networking and security groups are managed centrally by the platform team. Plan runs in CI on every PR — reviewers see exactly what infra changes a code change requires."

**AWS Services (know these at depth):**

- **ECS vs EKS — when to pick each?**
  - ECS: AWS-native, simpler. No K8s complexity. Good for teams that just want containers running without managing cluster control plane. Fargate mode = fully serverless (no EC2 instances to manage).
  - EKS: managed Kubernetes. Portable (can migrate to GKE or on-prem K8s). Full K8s ecosystem (Helm, Istio, ArgoCD). More control, more operational overhead.
  - Decision: if you're already invested in K8s tooling or need multi-cloud portability → EKS. If you want simplicity and are AWS-only → ECS/Fargate.

- **SQS — standard vs FIFO, visibility timeout, DLQ?**
  - Standard: unlimited throughput, at-least-once delivery, best-effort ordering. Messages can be delivered more than once → need idempotent consumers.
  - FIFO: exactly-once processing, strict ordering within a message group. 300 msg/sec (3000 with batching). Use when order matters (financial transactions).
  - Visibility timeout: after a consumer receives a message, it becomes invisible for X seconds. If consumer doesn't delete it before timeout, message reappears for another consumer. Set timeout > max processing time.
  - Dead letter queue (DLQ): after N failed receive attempts (maxReceiveCount), message moves to DLQ. Alert on DLQ depth. Manually replay after fixing the bug.
  - Long polling: consumer waits up to 20s for a message (reduces empty responses and cost vs short polling).
  - Handling duplicates: store processed message IDs in a set (Redis or DB). Check before processing. Or design idempotent operations.

- **SNS — pub/sub fan-out?**
  - Publish one message, deliver to many subscribers (SQS queues, Lambda, HTTP endpoints, email).
  - SNS → SQS pattern: decouple publishers from consumers. Publisher sends to SNS topic, each consumer team has their own SQS queue subscribed to that topic. Teams can consume at their own pace.
  - Filter policies: subscriber can filter which messages it receives based on message attributes (e.g., only receive events where `eventType = "lead.submitted"`). Reduces noise per consumer.
  - Fanout example: "When a lead is captured, SNS publishes once. Three SQS queues subscribe: notification service, analytics service, CRM sync service. Each processes independently."

- **S3 — consistency, storage classes, access patterns?**
  - Consistency: since Dec 2020, S3 provides strong read-after-write consistency for all operations. (Before that, overwrites/deletes were eventually consistent.)
  - Storage classes: Standard (frequent access), IA (infrequent, cheaper storage, retrieval fee), Glacier (archive, minutes-to-hours retrieval), Deep Archive (cheapest, 12hr retrieval).
  - Lifecycle policies: automatically transition objects between classes based on age (e.g., 90 days → IA, 1 year → Glacier).
  - Pre-signed URLs: generate a time-limited URL that grants temporary access to a private object without requiring IAM credentials. Used for file downloads/uploads from untrusted clients.
  - Multipart upload: for large files (>100MB), upload in parallel chunks, then assemble. Handles network failures gracefully — retry individual parts.

- **RDS — HA, read replicas, failover?**
  - Multi-AZ: synchronous replication to a standby in a different AZ. If primary fails, automatic failover to standby (~60-120s). No data loss (sync replication).
  - Read replicas: asynchronous replication. For read scaling — route read queries to replicas. Can have up to 5 replicas. Lag is typically seconds but can grow under write load.
  - Failover behavior: DNS endpoint (CNAME) automatically points to new primary. Application reconnects using same endpoint. Connection pool must handle brief interruption.
  - Connection pooling: RDS has a max_connections limit. At high concurrency, use a connection pool (HikariCP in Java) or RDS Proxy (managed pooling layer).
  - Backups: automated daily snapshots + transaction logs for point-in-time recovery (PITR) to any second within retention window.

- **IAM — least privilege, roles, cross-account?**
  - Principle of least privilege: grant only permissions needed for the specific task. No wildcards in production policies.
  - Service roles (instance profiles): EC2/ECS tasks assume an IAM role. No long-lived credentials. Temporary credentials rotated automatically via STS.
  - User roles: for humans — assume a role via SSO. MFA required for privileged roles.
  - Cross-account access: Service in Account A assumes a role in Account B via `sts:AssumeRole`. The role in Account B has a trust policy allowing Account A.
  - Policy evaluation: explicit Deny always wins. Then explicit Allow. Default is implicit Deny.

**Circuit Breakers / Resilience:**

- **Three states: Closed → Open → Half-Open?**
  - Closed (normal): requests pass through. Failures counted in a sliding window (e.g., last 10 seconds or last 100 calls).
  - Open (tripped): failure rate exceeded threshold (e.g., >50% failures). All requests immediately fail-fast with fallback response. No calls to downstream. Timer starts (e.g., 30s cooling period).
  - Half-Open (testing): after cooling period, allow a small number of trial requests through. If they succeed → back to Closed. If they fail → back to Open.

- **When to trip?**
  - Rate-based: >50% failure rate in a 10-second sliding window with minimum 20 calls (don't trip on 1 failure out of 2 calls).
  - Slow-call threshold: if >80% of calls exceed a latency threshold (e.g., 2s), trip the breaker — slow is as bad as failing.
  - Both conditions configurable per downstream dependency (fast service gets tight timeout, slow batch service gets lenient).

- **What happens when open — what does the caller get?**
  - Return a fallback: cached stale data, default value, degraded response, or explicit "service unavailable" for non-critical features.
  - For critical paths: return partial response with available data, omit the failed section.
  - Never block the request waiting for a timeout — the whole point is fast-fail.

- **Difference from retry?**
  - Retry: individual request failed, try again (with backoff). Good for transient failures (network blip).
  - Circuit breaker: pattern of failures detected, STOP trying for a period. Good for sustained failures (downstream is dead, overloaded, or deploying).
  - Use together: retry first (2-3 attempts with exponential backoff), if all retries fail → count as a breaker failure. Breaker trips after threshold of such failures.

- **Resilience4j (Java) specifics:**
  - Annotations: `@CircuitBreaker(name = "pricingService", fallbackMethod = "pricingFallback")`
  - Config: `slidingWindowSize`, `failureRateThreshold`, `waitDurationInOpenState`, `slowCallRateThreshold`
  - Monitoring: exposes metrics (state transitions, failure counts) to Prometheus/Datadog via micrometer.
  - Bulkhead: limits concurrent calls to a dependency (prevents thread pool exhaustion). Separate from circuit breaker but complementary.

- **Your story:** "Each downstream service in the orchestration layer has its own Resilience4j circuit breaker with tuned thresholds. The pricing service has a 50% failure threshold with a 30s cool-down. When it trips, we return the last cached price (acceptable staleness for a display page). The lead submission service has NO fallback — if it trips, we return an error because we can't silently drop a lead. Per-service tuning based on business criticality."

**Distributed Tracing / Observability:**

- **Trace ID propagation — how does it work end-to-end?**
  - Gateway generates a trace ID (128-bit UUID) on first request entry. Injected into HTTP headers (W3C `traceparent` header or Zipkin B3 headers).
  - Every downstream HTTP client reads the trace ID from incoming request and propagates it in outgoing calls. Each service adds its own span.
  - Result: a tree of spans where root = gateway, children = each downstream call. You can see the entire request journey.
  - For async (Kafka/SQS): trace ID goes in message headers/attributes. Consumer creates a linked span.

- **Span = one unit of work. Trace = tree of spans. What data is in a span?**
  - Operation name (e.g., "GET /api/listings"), start time, duration
  - Tags/attributes: HTTP status, service name, error flag, custom business fields
  - Parent span ID: links child to parent, forming the tree
  - Events/logs: timestamped annotations within the span (e.g., "cache miss", "retry attempt 2")

- **Instrumentation approaches?**
  - Auto-instrumentation: agent/library automatically wraps HTTP clients, DB drivers, frameworks. Zero code changes. Captures 80% of value.
  - Manual spans: for business logic that matters (e.g., "inventory enrichment" step within a handler). Wrap with `tracer.startSpan()` / `span.end()`.
  - Libraries: OpenTelemetry (vendor-neutral standard), Datadog APM agent, AWS X-Ray SDK.

- **Datadog APM vs Jaeger vs X-Ray?**
  - Datadog APM: SaaS, auto-instrumentation agents for Java/.NET/Python/Go, correlated with metrics/logs in same platform. Expensive at scale.
  - Jaeger: open-source, self-hosted. Good for K8s environments. Stores in Elasticsearch or Cassandra. More operational overhead.
  - AWS X-Ray: native AWS integration, good if you're all-in on AWS. Limited customization vs Datadog/Jaeger.
  - All support OpenTelemetry — you can instrument once and switch backends.

- **SLO-based observability — how does it work?**
  - Define per-service latency budgets: "inventory service must respond in <30ms at p99"
  - Dashboard shows each service's contribution to total request latency. Sum of parts = total p99.
  - Alert when a single service consumes more than its budget — catch degradation before it impacts the user-facing SLA.
  - Error budgets: "we accept 0.1% errors per month. Once budget is burned, freeze deploys until reliability improves."

- **Your story:** "Every request gets a trace ID at the API gateway. Each downstream call is a child span with Datadog APM auto-instrumentation. I set SLO latency budgets per downstream service — if the inventory service starts using 40ms of our 50ms p99 budget, we see it immediately in the Datadog dashboard and can investigate before the user-facing page degrades. We also correlate traces with structured logs — every log line includes the trace ID so you can jump from a metric spike to the exact trace to the exact log line."

**Event-Driven Architecture (Kafka / SQS/SNS):**

- **Kafka: topics, partitions, consumer groups, offsets?**
  - Topic: logical channel for events (e.g., "lead-events", "inventory-updates")
  - Partition: ordered, append-only log within a topic. Messages in a partition are strictly ordered by offset. A topic has N partitions for parallelism.
  - Consumer group: set of consumers that cooperatively read from a topic. Each partition is assigned to exactly one consumer in the group. More partitions = more parallelism.
  - Offset: position of a message within a partition. Consumer tracks "last committed offset" — on restart, resumes from there.
  - Partition key: determines which partition a message goes to (hash of key mod N partitions). Same key = same partition = ordering guaranteed.

- **At-least-once vs exactly-once?**
  - At-least-once (default): producer retries on failure, message might be written twice. Consumer processes a message, commits offset. If consumer crashes before commit → reprocesses same message.
  - Exactly-once: requires idempotent producers (`enable.idempotence=true`, deduplicates by producer ID + sequence number) AND transactional consumers (read-process-commit in single transaction).
  - In practice: most systems use at-least-once + idempotent consumers (cheaper, simpler). Store processed event IDs, check before processing.

- **Consumer lag — what is it, how to handle?**
  - Lag = latest offset on partition minus consumer's committed offset. Measures "how far behind" a consumer is.
  - Monitor lag in Datadog/Prometheus. Alert if lag exceeds threshold (e.g., >10K messages or >5 minutes of events).
  - Growing lag means: consumer is slower than producer. Fix: add more consumers (up to partition count), optimize processing logic, or scale the consumer instances.
  - Sudden lag spike: often means a consumer crashed or is stuck on a poison message (that's where DLQ helps).

- **Backpressure — what happens when consumers can't keep up?**
  - Kafka: lag grows indefinitely (Kafka retains messages per retention policy, e.g., 7 days). Messages are NOT lost — just delayed. Consumer will eventually catch up or you scale it.
  - SQS: messages pile up in queue. After maxReceiveCount failed attempts → message goes to DLQ. Queue depth is the backpressure metric. Alert when depth exceeds threshold.
  - Handling: scale consumers, increase processing capacity, or shed low-priority work. Never drop messages silently in a financial system.

- **Your story:** "Lead events go through Kafka partitioned by dealer_id — guarantees ordering per dealer so leads for the same dealer are processed sequentially. Inventory updates use SQS (ordering not critical) with a DLQ. If a consumer fails a message 3 times, it moves to DLQ and we alert. We monitor consumer lag in Datadog — any lag above 5 minutes triggers a page."

**In-Memory Caching:**

- **Why in-memory over Redis?**
  - Redis adds: network round-trip (~0.5-1ms) + serialization cost (marshal/unmarshal complex nested objects). At 8K rpm, this adds up.
  - In-memory: direct object reference access, zero serde, sub-microsecond reads. Tradeoff: per-instance (not shared), uses heap space, stale across instances.
  - When Redis IS better: multiple instances need same cached data with consistency guarantees, or cache is too large to fit in each instance's heap.
  - Hybrid: in-memory L1 cache (short TTL, per-instance) + Redis L2 cache (longer TTL, shared). Check L1 first, fall back to L2, fall back to DB.

- **Cache invalidation strategies?**
  - TTL-based: simplest. Set short TTL (e.g., 30s) for dynamic data, long TTL (e.g., 1hr) for static data. Acceptable staleness = TTL duration.
  - Event-based: Kafka event triggers cache eviction. "Inventory changed for listing X" → evict from cache → next read fills fresh data. Near-real-time freshness.
  - Versioned: cache key includes a version. When data changes, bump version → old key expires naturally, new key is filled. No explicit eviction needed.
  - Best for financial data: event-based (can't show stale prices). Best for display data: TTL-based (acceptable staleness, simpler).

- **Cache-aside pattern (most common)?**
  - Read: check cache → hit? return. Miss? → load from DB → put in cache → return.
  - Write: write to DB → invalidate/evict cache entry. (DON'T write-through cache unless you need strong consistency between cache and DB.)
  - Why not write-through: adds latency to writes and complexity. Cache-aside is simpler for read-heavy workloads.

- **Cache stampede — what is it, how to prevent?**
  - Problem: TTL expires on a hot key. 1000 concurrent requests all see cache miss simultaneously. All 1000 hit the database → DB overwhelmed.
  - Solution 1: single-flight / request coalescing. Only one goroutine/thread fetches, others wait for its result. (Guava `LoadingCache` does this automatically in Java.)
  - Solution 2: early expiration with jitter. Refresh cache slightly before TTL expires. Background thread refreshes proactively.
  - Solution 3: lock-based. Acquire a distributed lock before fetching. Others wait or return stale data.

- **Your story:** "At 8K rpm with deeply nested response objects, the network hop to Redis plus JSON serialization cost would eat 2-3ms per request — that's 10% of our latency budget. I chose in-memory Caffeine cache with two tiers: long TTL (1hr) for static dealer metadata, short TTL (30s) for dynamic inventory data. For lead-related data that must be fresh, we use event-based invalidation — Kafka event triggers eviction. Caffeine's `LoadingCache` handles stampede prevention automatically — only one thread fetches on miss, others wait."

---

---

### System Design Prep

**Team context: NGC (NVIDIA GPU Cloud)**

NGC is NVIDIA's catalog/registry platform — users browse, pull, and deploy GPU-optimized containers, pre-trained models, and SDKs. Think "Docker Hub for GPU software." NOT fleet management or DGX hardware.

**What NGC offers:**
- GPU-optimized Docker containers (TensorFlow, PyTorch, RAPIDS pre-configured)
- Pre-trained models (ready to fine-tune or deploy)
- Helm charts for K8s deployment
- SDKs and tools
- Enterprise licensing / entitlements

**Users:** ML engineers, data scientists, enterprises deploying AI at scale.

---

### Most Likely SD Topic: Content Registry / Catalog Platform

> "Design a system where users browse, search, and download GPU-optimized containers and models from a catalog."

**Key components:**
```
User (browser/CLI)
    │
    ▼
API Gateway (auth, rate limiting)
    │
    ├──▶ Catalog Service (Postgres)
    │       - artifact metadata (name, version, description, tags)
    │       - publisher info (org, team)
    │       - licensing/entitlement rules
    │       - download counts, ratings
    │
    ├──▶ Search Service (Elasticsearch)
    │       - full-text search on name, description, tags
    │       - faceted filtering (framework, GPU arch, use case)
    │       - ranking by popularity/relevance
    │
    ├──▶ Artifact Storage (S3 / Container Registry)
    │       - actual binaries (containers = layers, models = files)
    │       - presigned URLs for download (gateway never proxies bytes)
    │       - content-addressable (SHA digest as key)
    │       - CDN in front for popular artifacts
    │
    └──▶ Access Control Service
            - free tier vs enterprise licensing
            - per-org entitlements (team A can access model X)
            - API key / token management
            - usage quota enforcement
```

**Key design points:**

| Area | Details |
|---|---|
| **Publish flow** | Publisher uploads artifact → metadata written to Postgres → binary pushed to S3/registry → indexed in Elasticsearch → becomes searchable |
| **Search/discovery** | Elasticsearch for full-text + facets. Postgres for exact lookups by ID/version. Redis cache for popular items. |
| **Download flow** | Auth check → entitlement check → generate presigned URL → client downloads directly from S3/CDN. Gateway never proxies large files. |
| **Versioning** | Immutable once published. New version = new artifact record. Semantic versioning. "Latest" tag points to newest. |
| **Container specifics** | OCI spec. Layers stored separately (content-addressable by SHA). Pull = download manifest + only missing layers. |
| **Rate limiting** | Per API key, per org. Free tier gets X pulls/day. Enterprise unlimited. Token bucket algorithm. |
| **Deprecation** | Mark deprecated → still downloadable but hidden from search. Eventually archive to cold storage. |

**Data model:**

```java
class Artifact {
    UUID id;
    String name;             // e.g., "nvidia/pytorch"
    String type;             // CONTAINER, MODEL, HELM_CHART, SDK
    String publisher;
    String description;
    List<String> tags;       // ["pytorch", "nlp", "a100-optimized"]
    String license;          // FREE, ENTERPRISE, RESEARCH_ONLY
    LocalDateTime createdAt;
}

class ArtifactVersion {
    UUID id;
    UUID artifactId;         // FK → Artifact
    String version;          // "23.04" or "1.2.0"
    String digest;           // SHA-256 of content
    Long sizeBytes;
    String storageUrl;       // S3 key or registry reference
    Boolean deprecated;
    LocalDateTime publishedAt;
}

class Entitlement {
    UUID id;
    UUID orgId;
    UUID artifactId;         // null = access to all
    String tier;             // FREE, ENTERPRISE
    Integer pullQuotaDaily;
    LocalDateTime expiresAt;
}
```

**APIs:**

```
GET  /v1/artifacts?q=pytorch&framework=pytorch&gpu=a100&page=1
GET  /v1/artifacts/{id}
GET  /v1/artifacts/{id}/versions
GET  /v1/artifacts/{id}/versions/{version}/download → 302 redirect to presigned URL
POST /v1/artifacts                          (create metadata)
PUT  /v1/artifacts/{id}/versions/{version}  (upload binary)
GET  /v1/entitlements/check?org={org}&artifact={id}
```

**Failure modes:**

| Failure | Recovery |
|---|---|
| Elasticsearch down | Fall back to Postgres LIKE queries (slower but functional) |
| S3 unavailable | Return error on download. Metadata/search still works. |
| CDN cache stale | Content-addressable (SHA in URL) — stale = impossible. Cache miss → S3. |
| Publisher uploads corrupt artifact | Verify SHA digest on upload. Reject if mismatch. |
| Rate limit exceeded | Return 429. Client retries with backoff. |

**Scaling:**

| Challenge | Solution |
|---|---|
| Popular artifacts (everyone pulls PyTorch) | CDN in front of S3. Cache at edge. |
| Search at scale (millions of artifacts) | Elasticsearch cluster. Shard by artifact type. |
| Metadata reads | Redis cache for top/trending. Postgres for long-tail. |
| Large uploads (GB+ containers) | Multipart upload to S3. Presigned URLs per part. Resume on failure. |
| Global users | Multi-region CDN. Metadata read replicas. Writes to primary region. |

---

### Backup SD Topics

**Model Registry (you already did this in round 1!):**
- Metadata in Postgres, binaries in S3, presigned URLs, versioning, access control

**Telemetry Pipeline (same pattern as Coinbase Explore):**
- Ingest from agents → aggregate per time window → time-series DB → Grafana + alerting

---

### Java Concurrency Patterns (likely to come up)

**LC 1114 — Three Solutions (Print in Order):**

```java
// Solution 1: Lock + Condition + state variable
class Foo {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition cond = lock.newCondition();
    private int step = 1;

    void first(Runnable r) throws InterruptedException {
        lock.lock();
        try { r.run(); step = 2; cond.signalAll(); }
        finally { lock.unlock(); }
    }
    void second(Runnable r) throws InterruptedException {
        lock.lock();
        try { while (step != 2) cond.await(); r.run(); step = 3; cond.signalAll(); }
        finally { lock.unlock(); }
    }
    void third(Runnable r) throws InterruptedException {
        lock.lock();
        try { while (step != 3) cond.await(); r.run(); }
        finally { lock.unlock(); }
    }
}

// Solution 2: Semaphore (simplest)
class Foo {
    private final Semaphore sem2 = new Semaphore(0);
    private final Semaphore sem3 = new Semaphore(0);

    void first(Runnable r) { r.run(); sem2.release(); }
    void second(Runnable r) throws InterruptedException { sem2.acquire(); r.run(); sem3.release(); }
    void third(Runnable r) throws InterruptedException { sem3.acquire(); r.run(); }
}

// Solution 3: CountDownLatch (one-shot)
class Foo {
    private final CountDownLatch latch1 = new CountDownLatch(1);
    private final CountDownLatch latch2 = new CountDownLatch(1);

    void first(Runnable r) { r.run(); latch1.countDown(); }
    void second(Runnable r) throws InterruptedException { latch1.await(); r.run(); latch2.countDown(); }
    void third(Runnable r) throws InterruptedException { latch2.await(); r.run(); }
}
```

**Why `while` + state in Lock solution:**
- Spurious wakeups: `await()` can return without signal
- Late arrivals: boolean persists so threads arriving after signal skip await
- Thread safety: boolean only accessed under lock

**When to use which:**

| Pattern | Guards | Use when |
|---|---|---|
| Lock + Condition | State ("is step done?") | Data dependency, reusable coordination |
| Semaphore | Count ("how many permits?") | Count-bounded (can't capture more than authorized) |
| CountDownLatch | One-time gate ("did N things finish?") | One-shot initialization |

**Web API examples:**

```java
// Semaphore: can't capture more payments than authorized
class PaymentService {
    private final Semaphore capturePermits = new Semaphore(0);
    void authorize(Request req) { doAuth(req); capturePermits.release(); }
    void capture(Request req) throws InterruptedException {
        capturePermits.acquire(); // blocks if no uncaptured auths
        doCapture(req);
    }
}
```

---

### Back-of-Envelope Numbers

| Thing | Rule of thumb |
|---|---|
| Single Postgres | 10-50K writes/sec |
| Redis | 100K+ ops/sec |
| Kafka | 1M+ messages/sec per cluster |
| Single JVM service | 5-10K concurrent requests |
| WebSocket per node | 50-100K connections |
| REST API p99 target | < 100ms (internal), < 250ms (user-facing) |
| DB connection pool | 10-50 connections per service instance |
| Thread pool | CPU cores × 2 for compute, higher for I/O-bound |

### Behavioral Prep

Since no dedicated BQ round exists, expect behavioral questions woven into technical rounds. Lead with TECHNICAL DEPTH, not leadership/coordination.

**"Tell me about yourself."**
> "Senior/Principal Java backend engineer, 13 years. I build large-scale distributed systems on cloud infrastructure. Most recently: redesigned a high-traffic API platform — 8K rpm, per-service circuit breakers, in-memory caching, SLO-based monitoring. Before that, built event-driven architectures with Kafka, deployed on AWS with Kubernetes, and built auth infrastructure with service mesh. Core Java is my primary language — concurrency, performance tuning, JVM optimization. I'm looking to apply these skills to GPU cloud computing."

**"Tell me about a complex system you designed."** → Story 1 TECHNICAL layer:
> "Orchestration service consolidating 12 downstream integrations into 5 services. Per-service timeouts, connection pools (HikariCP), circuit breakers (Resilience4j), async fan-out with CompletableFuture for parallel calls. In-memory cache (Caffeine) — chose over Redis to avoid network hop + serialization cost at 8K rpm. Per-hop SLO budgets monitored in Datadog. Rolled out with parity testing — zero regressions."

**"Tell me about a disagreement."** → Story 16 (peer conflict):
> "Disagreement about GraphQL federation design — nested entity resolution. I believed IDs-only was correct to avoid a sync hop in the critical path. Built a dev router, measured the latency difference, showed the data. Other lead agreed. Let measurements decide, not philosophy."

**"Tell me about a failure."** → Story 14:
> "Deployed Mongo collection sized for average traffic. Fell over during lunch spike — connection pool starvation. Root cause: peak-to-average ratio was 5x, and connection pools don't degrade linearly. Fix: partitioned to separate cluster, load-tested against peaks. Lesson shaped all my later work — per-service pools, bulkheads, always design for ceiling not average."

### "Why NVIDIA?" Answer

> "This role is a direct match for what I've been doing — large-scale Java backend systems, REST/gRPC API design, distributed services with Kafka and cloud infrastructure. What excites me is applying these skills to GPU cloud computing — it's a domain I haven't worked in, but the engineering patterns are exactly my strength. I want to build the platform layer that makes GPU computing accessible as a service. Plus my academic background in control systems and sensor processing gives me context on the AI/ML workloads this platform serves."

---

## Open Questions (ask AFTER interviews if they go well)

- Is this role hybrid (Westford) or fully remote?
- What's the target level — L4 or L5? The JD listed both ranges.
- What's the team size and structure?
- What does the full interview process look like? (Are these the final rounds, or is there more?)
- What's the timeline for a decision?
- Comp range for the specific level they're targeting?

---

## Prep Strategy — "Explain Your Work" Format

Since this is project-deep-dive style AND the JD is Java/distributed-systems focused:

### Lead Projects (match JD requirements directly)

**Primary: Story 1 (API Modernization) — TECHNICAL LAYER ONLY**
- 8K rpm, per-service circuit breakers, connection pools, bulkheads
- In-memory caching (Caffeine) vs Redis — WHY in-memory (serialization cost at 8K rpm)
- Per-hop SLO latency budgets in Datadog
- Parity testing framework for zero-regression rollout
- **Java specifics to mention:** async thread fan-out (CompletableFuture), connection pool tuning (HikariCP), JVM performance monitoring

**Secondary: Story 4 (Digital Shopping) — TECHNICAL LAYER**
- Kafka event pipeline design (partition key strategy, consumer groups, DLQ)
- Transaction state machine with strong consistency
- In-memory cache with Kafka-driven invalidation (not TTL)
- MySQL schema design: configurational vs transactional data separation

**Tertiary: Story 10 (DGS/GraphQL) — if asked about API design or JVM**
- Netflix DGS subgraph, batch data loaders (N+1 prevention)
- JVM cold-start problem: profiled, found JIT + DGS lazy init, built warmup routine
- Federation schema design, per-consumer authorization

### What to Emphasize (from JD)

| JD Requirement | Your Example | Be Ready to Go Deep |
|---|---|---|
| Core Java (Collections, Streams, Concurrency) | Async fan-out with CompletableFuture, thread pools, connection pooling | How does HikariCP work? ConcurrentHashMap vs synchronized? |
| Large-scale distributed systems | API Mod orchestration (12→5 services, 8K rpm) | Circuit breaker states, bulkhead isolation, retry with backoff |
| REST API / gRPC design | API standards RFCs, pagination (cursor vs offset), versioning | Backward compatibility, idempotency keys |
| RDBMS + NoSQL + Redis | MySQL (transactional), Redis (caching), Mongo (events) | When to use each, caching strategies, connection pool sizing |
| Cloud technologies | AWS (ECS/EKS, SQS/SNS, S3, RDS), Terraform, K8s | ECS vs EKS decision, rolling deploys, readiness probes |
| Streaming (Kafka) | Event-driven pipeline, partition by dealer_id, DLQ | Ordering guarantees, consumer lag, at-least-once + idempotent consumers |
| Troubleshooting complex issues | Story 14 (Mongo connection starvation), DGS cold-start | Root cause analysis methodology, peak vs average |

### Framing (learned from HashiCorp)

**DON'T lead with:** "I led 10 teams, drove alignment, coordinated with product"
**DO lead with:** "Here's what I built, here's the technical decision, here's why it works at scale"

Let the interviewer discover your leadership through follow-up questions. Lead with DEPTH.

### For Each Project, Be Ready to Answer:
- What was the architecture? (Draw it if needed)
- What were the key technical decisions and why?
- What would you do differently?
- How did you handle failures/edge cases?
- What was the scale? How did you monitor it?
- **What Java-specific patterns did you use?** (concurrency, caching, connection management)

### Know About NGC (your team):
- NGC: catalog/registry platform for GPU-optimized containers, models, SDKs
- Think "Docker Hub for GPU software" — browse, search, pull, deploy
- You're building: REST APIs, search/discovery, access control, artifact storage — Java backend
- Users: ML engineers, data scientists, enterprises deploying AI
- NOT writing CUDA or managing GPU hardware

### Questions to Ask Interviewers

**Team & product (show genuine curiosity):**
- What's the team working on right now? What's the biggest technical challenge?
- What does the tech stack look like? (Languages, cloud providers, orchestration, messaging)
- How many services does the team own? What's the ownership model?
- How does this team interact with the hardware platform teams? (firmware, drivers, GPU health)
- How big is the fleet you manage today? What's the growth trajectory?

**Technical challenges (show depth):**
- How do you handle fleet-level failures — a node goes down mid-training job? Is there automatic failover / checkpointing?
- What's the scheduling strategy? FIFO, priority-based, or resource-bin-packing?
- How do you monitor GPU health at scale — memory errors, thermal events, NVLink degradation? Is it proactive or reactive?
- What's the deployment model for your services? How do you roll out changes without disrupting running jobs?
- How do you handle multi-tenancy — is it namespace-level isolation, separate clusters, or something else?

**Role & growth (show you're thinking about fit):**
- What does success look like in the first 6 months for this role?
- Is this role more focused on building new systems (0→1) or scaling/reliability of existing ones?
- How much autonomy does this role have in defining technical direction vs. executing a defined roadmap?
- What's the on-call model? How do GPU fleet incidents differ from typical cloud service incidents?

**Pick 2-3 per interviewer. Don't ask all of them — read the room.**

---

## Pre-Interview Checklist (May 29-30)

- [ ] Skim this doc (focus on: NGC SD topic, concurrency patterns, behavioral answers)
- [ ] Re-read resume_nvidia.html — be ready to go deep on every bullet
- [ ] "Tell me about yourself" — technical angle (90 sec)
- [ ] Project deep-dives ready: Story 1 (API Mod technical layer), Story 10 (DGS/JVM), Story 14 (Failure)
- [ ] Know NGC context (catalog platform, not fleet management)
- [ ] Java concurrency: Lock/Condition, Semaphore, CompletableFuture patterns ready
- [ ] Block calendar 11:30-3:30 both days
- [ ] Test Microsoft Teams
- [ ] 2-3 questions per interviewer ready
