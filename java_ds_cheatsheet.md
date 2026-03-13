# Java Data Structures Cheat Sheet (Interview Quick Reference)

---

## TreeMap<K, V>

Sorted map backed by a Red-Black tree. All operations **O(log n)**.

### Core

| Method | Description |
|---|---|
| `put(k, v)` | Insert / update |
| `get(k)` | Get value |
| `remove(k)` | Remove by key |
| `containsKey(k)` | Check existence |
| `size()` | Number of entries (O(1)) |

### Min / Max

| Method | Description |
|---|---|
| `firstKey()` / `firstEntry()` | Smallest key / entry |
| `lastKey()` / `lastEntry()` | Largest key / entry |
| `pollFirstEntry()` | Remove + return smallest |
| `pollLastEntry()` | Remove + return largest |

### Neighbor Lookups

| Method | Description |
|---|---|
| `floorKey(k)` | Largest key **≤ k** |
| `ceilingKey(k)` | Smallest key **≥ k** |
| `lowerKey(k)` | Largest key **< k** |
| `higherKey(k)` | Smallest key **> k** |

All have `Entry` variants: `floorEntry(k)`, `ceilingEntry(k)`, etc. Returns `null` if no match.

### Range Views (live — changes reflect in original)

| Method | Description |
|---|---|
| `subMap(from, to)` | Keys in `[from, to)` |
| `subMap(from, incl, to, incl)` | Configurable bounds |
| `headMap(to)` | All keys `< to` |
| `tailMap(from)` | All keys `≥ from` |

### When to Use

- Sliding window needing sorted access (min/max + arbitrary removal)
- Nearest neighbor queries (`floor`/`ceiling`)
- Interval problems (find overlapping intervals)
- Prefer over `PriorityQueue` when you need **O(log n) removal by key**

---

## ArrayDeque<E>

Resizable array-backed double-ended queue. All operations **O(1) amortized**. Faster than `LinkedList` for both stack and queue use. **Does not allow `null` elements.**

### As a Stack (LIFO)

| Method | Description |
|---|---|
| `push(e)` | Push onto top (head) |
| `pop()` | Remove + return top (throws if empty) |
| `peek()` | View top without removing (returns `null` if empty) |

### As a Queue (FIFO)

| Method | Description |
|---|---|
| `offer(e)` / `add(e)` | Enqueue at tail |
| `poll()` | Dequeue from head (returns `null` if empty) |
| `peek()` | View head without removing |

### As a Deque (double-ended)

| Method | Description |
|---|---|
| `offerFirst(e)` / `addFirst(e)` | Add to head |
| `offerLast(e)` / `addLast(e)` | Add to tail |
| `pollFirst()` | Remove from head |
| `pollLast()` | Remove from tail |
| `peekFirst()` | View head |
| `peekLast()` | View tail |

### Throwing vs Returning null

| Operation | Throws on empty | Returns null on empty |
|---|---|---|
| Add | `addFirst` / `addLast` | `offerFirst` / `offerLast` |
| Remove | `removeFirst` / `removeLast` | `pollFirst` / `pollLast` |
| Examine | `getFirst` / `getLast` | `peekFirst` / `peekLast` |

For interviews, the `poll`/`peek`/`offer` family is generally safer (no exceptions).

### When to Use

- **Stack**: monotonic stack (LC 739, 42), DFS iteration, parentheses matching
- **Queue**: BFS (LC 200, 127), sliding window with deque (LC 239, 1438)
- **Deque**: monotonic deque for sliding window max/min

### Common Interview Patterns

**Monotonic stack** (decreasing, for "next greater element"):
```java
Deque<Integer> stack = new ArrayDeque<>();
for (int i = 0; i < nums.length; i++) {
    while (!stack.isEmpty() && nums[stack.peek()] < nums[i]) {
        int idx = stack.pop();
        result[idx] = nums[i];
    }
    stack.push(i);
}
```

**Monotonic deque** (for sliding window maximum):
```java
Deque<Integer> deque = new ArrayDeque<>();
for (int i = 0; i < nums.length; i++) {
    while (!deque.isEmpty() && nums[deque.peekLast()] <= nums[i]) {
        deque.pollLast();
    }
    deque.offerLast(i);
    if (deque.peekFirst() <= i - k) deque.pollFirst();  // evict out-of-window
    if (i >= k - 1) result[i - k + 1] = nums[deque.peekFirst()];
}
```

**BFS template**:
```java
Deque<Node> queue = new ArrayDeque<>();
queue.offer(start);
while (!queue.isEmpty()) {
    Node curr = queue.poll();
    for (Node neighbor : curr.neighbors) {
        if (!visited.contains(neighbor)) {
            visited.add(neighbor);
            queue.offer(neighbor);
        }
    }
}
```

---

## PriorityQueue<E>

Min-heap backed by a **resizable array**. Default ordering is natural (min on top). Use `new PriorityQueue<>(Comparator.reverseOrder())` for max-heap.

### Core Operations

| Method | Description | Time |
|---|---|---|
| `offer(e)` / `add(e)` | Insert element | **O(log n)** — sift up |
| `peek()` | View min (top) without removing | **O(1)** |
| `poll()` | Remove + return min | **O(log n)** — sift down |
| `remove(obj)` | Remove arbitrary element | **O(n)** — linear scan + O(log n) sift |
| `contains(obj)` | Check if element exists | **O(n)** — linear scan |
| `size()` | Number of elements | **O(1)** |

### Bulk / Construction

| Operation | Time |
|---|---|
| `new PriorityQueue<>(collection)` | **O(n)** — heapify (not n log n) |
| `toArray()` | **O(n)** |

### Key Gotchas

- **`remove(obj)` is O(n)** — this is the big one. No index from value → position, so it must scan the backing array. This is why `TreeMap` is preferred when you need arbitrary removal.
- **No random access** — you can only efficiently access the min element. The rest of the heap is unordered.
- **Iterator is NOT sorted** — `for (int x : pq)` does NOT iterate in sorted order. The heap property only guarantees the root is min.
- **Duplicates allowed** — unlike `TreeMap`, PQ happily stores duplicate values.

### Common Interview Patterns

**Top K elements** (use max-heap of size k):
```java
PriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.reverseOrder());
// or for top-k smallest, use min-heap and evict when size > k:
PriorityQueue<Integer> pq = new PriorityQueue<>();
for (int num : nums) {
    pq.offer(num);
    if (pq.size() > k) pq.poll();  // O(n log k) total
}
```

**Merge K sorted lists**:
```java
PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> a.val - b.val);
// add first node of each list, then poll min + offer its next
```

---

## Trie (Prefix Tree)

Tree where each node represents a character. Paths from root to nodes represent prefixes; paths to nodes marked `isEnd` represent complete words.

### Node Structure

```java
class TrieNode {
    TrieNode[] children = new TrieNode[26];  // or Map<Character, TrieNode> for unicode
    boolean isEnd;
}
```

Use `TrieNode[26]` for lowercase English letters (interview default). Use `Map<Character, TrieNode>` when the character set is large or unknown (e.g., file paths, arbitrary strings).

### Core Operations

```java
class Trie {
    TrieNode root = new TrieNode();

    // INSERT — O(L) where L = word length
    void insert(String word) {
        TrieNode curr = root;
        for (char c : word.toCharArray()) {
            if (curr.children[c - 'a'] == null)
                curr.children[c - 'a'] = new TrieNode();
            curr = curr.children[c - 'a'];
        }
        curr.isEnd = true;
    }

    // SEARCH exact word — O(L)
    boolean search(String word) {
        TrieNode node = find(word);
        return node != null && node.isEnd;
    }

    // STARTS WITH prefix — O(L)
    boolean startsWith(String prefix) {
        return find(prefix) != null;
    }

    // Helper: traverse to end of prefix, return node or null
    private TrieNode find(String s) {
        TrieNode curr = root;
        for (char c : s.toCharArray()) {
            if (curr.children[c - 'a'] == null) return null;
            curr = curr.children[c - 'a'];
        }
        return curr;
    }
}
```

### Big O

| Operation | Time | Space |
|---|---|---|
| Insert | O(L) | O(L) worst case (new branch) |
| Search | O(L) | O(1) |
| Prefix check | O(L) | O(1) |
| Total space | — | O(N × L × 26) worst case |

Where L = word length, N = number of words.

### When to Use

- **Prefix matching**: autocomplete, type-ahead search
- **Word-by-word validation**: word search in grids (LC 212)
- **Directory/path structures**: file system design (LC 588, 1166)
- **Shared prefix optimization**: when many strings share prefixes, trie deduplicates storage

### Key Gotchas

- **Array vs Map children**: `TrieNode[26]` is faster but wastes space if the tree is sparse. For interviews, array is fine for lowercase English.
- **`isEnd` is critical**: without it, `search("app")` would return true if `"apple"` was inserted (the path exists, but "app" was never added).
- **Delete is rarely asked**: it requires decrementing reference counts or recursive cleanup. Skip unless the problem explicitly needs it.

### Common Interview Patterns

**Basic trie** (LC 208):
```java
// Just implement insert, search, startsWith as above
```

**Trie + DFS backtracking** (LC 212 — Word Search II):
```java
// Build trie from word list, then DFS from each grid cell
// At each cell, follow trie children instead of checking all words
// This prunes search: if no trie child for current char, stop early
void dfs(char[][] board, int i, int j, TrieNode node, List<String> result) {
    char c = board[i][j];
    if (c == '#' || node.children[c - 'a'] == null) return;
    node = node.children[c - 'a'];
    if (node.isEnd) {
        result.add(node.word);  // store word at end node for easy retrieval
        node.isEnd = false;     // de-duplicate
    }
    board[i][j] = '#';  // mark visited
    for (int[] d : DIRS) dfs(board, i+d[0], j+d[1], node, result);
    board[i][j] = c;    // restore
}
```

**Trie as directory tree** (LC 588 — File System):
```java
class TrieNode {
    Map<String, TrieNode> children = new TreeMap<>();  // sorted listing
    String content = "";  // file content if this is a file
    boolean isFile;
}
// Navigate path segments like trie characters: split("/foo/bar") → ["foo", "bar"]
```

---

## Graph Algorithms Cheat Sheet

### Algorithm Overview

| Algorithm | Problem | Time | Data Structure |
|---|---|---|---|
| **BFS** | Shortest path (unweighted) | O(V + E) | Queue |
| **Dijkstra's** | Shortest path (non-negative weights) | O(E log V) | PriorityQueue |
| **Bellman-Ford** | Shortest path (negative weights ok) | O(V × E) | Array |
| **Kruskal's** | Minimum Spanning Tree | O(E log E) | Union-Find |
| **Prim's** | Minimum Spanning Tree | O(E log V) | PriorityQueue |
| **Topological Sort (Kahn's)** | Dependency ordering (DAG) | O(V + E) | Queue + in-degree array |

### When to Use Which

```
Shortest path?
├── Unweighted → BFS
├── Non-negative weights → Dijkstra's
├── Negative weights → Bellman-Ford
└── All pairs → Floyd-Warshall (rare in interviews)

Minimum Spanning Tree?
├── Sparse graph / edge list → Kruskal's (sort edges + Union-Find)
└── Dense graph / adjacency list → Prim's (greedy + PriorityQueue)

Dependency order?
└── Topological Sort (Kahn's BFS or DFS post-order)
```

---

### Dijkstra's Algorithm

**Problem**: Shortest path from source to all nodes in a weighted graph (non-negative weights).

**Mental model**: BFS but with a PriorityQueue instead of a Queue. Always process the closest unvisited node.

```java
// Returns shortest distance from src to all nodes
int[] dijkstra(Map<Integer, List<int[]>> graph, int src, int n) {
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;

    // {distance, node}
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
    pq.offer(new int[]{0, src});

    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int d = curr[0], u = curr[1];

        if (d > dist[u]) continue;  // stale entry, skip

        for (int[] edge : graph.getOrDefault(u, List.of())) {
            int v = edge[0], w = edge[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.offer(new int[]{dist[v], v});
            }
        }
    }
    return dist;
}
```

**Key points**:
- `if (d > dist[u]) continue` — lazy deletion instead of decreaseKey. The PQ may have stale entries; skip them.
- **Cannot handle negative weights** — a "settled" node might later find a shorter path via a negative edge.
- LC 743 (Network Delay Time): run Dijkstra, return max of all distances.
- LC 787 (Cheapest Flights Within K Stops): modified Dijkstra/BFS with stop count limit.

---

### Bellman-Ford Algorithm

**Problem**: Shortest path with **negative weights** allowed. Also detects negative cycles.

**Mental model**: Relax all edges V-1 times. Each round propagates shortest paths one hop further.

```java
int[] bellmanFord(int[][] edges, int src, int n) {
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;

    for (int i = 0; i < n - 1; i++) {          // V-1 rounds
        for (int[] e : edges) {                  // relax all edges
            int u = e[0], v = e[1], w = e[2];
            if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }

    // Optional: detect negative cycle (one more round)
    for (int[] e : edges) {
        if (dist[e[0]] != Integer.MAX_VALUE && dist[e[0]] + e[2] < dist[e[1]]) {
            // negative cycle exists
        }
    }
    return dist;
}
```

**Key points**:
- Slower than Dijkstra's but handles negatives.
- LC 787 (Cheapest Flights Within K Stops): limit relaxation rounds to K+1 instead of V-1.
- Rarely asked to implement from scratch in interviews, but knowing when to use it matters.

---

### Kruskal's Algorithm (MST)

**Problem**: Find minimum spanning tree — connect all nodes with minimum total edge weight.

**Mental model**: Sort all edges by weight, greedily add the cheapest edge that doesn't form a cycle. Use Union-Find for cycle detection.

```java
int kruskal(int n, int[][] edges) {
    // Sort edges by weight
    Arrays.sort(edges, (a, b) -> a[2] - b[2]);

    int[] parent = new int[n];
    int[] rank = new int[n];
    for (int i = 0; i < n; i++) parent[i] = i;

    int totalWeight = 0, edgesUsed = 0;
    for (int[] e : edges) {
        int u = e[0], v = e[1], w = e[2];
        if (find(parent, u) != find(parent, v)) {
            union(parent, rank, u, v);
            totalWeight += w;
            if (++edgesUsed == n - 1) break;  // MST complete
        }
    }
    return edgesUsed == n - 1 ? totalWeight : -1;  // -1 if disconnected
}

int find(int[] parent, int x) {
    if (parent[x] != x) parent[x] = find(parent, parent[x]);  // path compression
    return parent[x];
}

void union(int[] parent, int[] rank, int x, int y) {
    int px = find(parent, x), py = find(parent, y);
    if (rank[px] < rank[py]) parent[px] = py;
    else if (rank[px] > rank[py]) parent[py] = px;
    else { parent[py] = px; rank[px]++; }
}
```

**Key points**:
- Sort edges O(E log E) dominates. Union-Find operations are nearly O(1) amortized.
- MST has exactly V-1 edges. Early termination when `edgesUsed == n - 1`.
- LC 1135 (Connecting Cities With Minimum Cost): direct Kruskal's application.
- LC 1584 (Min Cost to Connect All Points): generate all edges, then Kruskal's.

---

### Prim's Algorithm (MST)

**Problem**: Same as Kruskal's — minimum spanning tree. Different approach.

**Mental model**: Start from any node. Greedily add the cheapest edge connecting the MST to a non-MST node. Like Dijkstra's but for MST.

```java
int prim(Map<Integer, List<int[]>> graph, int n) {
    boolean[] inMST = new boolean[n];
    // {weight, node}
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
    pq.offer(new int[]{0, 0});  // start from node 0

    int totalWeight = 0, nodesAdded = 0;
    while (!pq.isEmpty() && nodesAdded < n) {
        int[] curr = pq.poll();
        int w = curr[0], u = curr[1];
        if (inMST[u]) continue;

        inMST[u] = true;
        totalWeight += w;
        nodesAdded++;

        for (int[] edge : graph.getOrDefault(u, List.of())) {
            if (!inMST[edge[0]]) {
                pq.offer(new int[]{edge[1], edge[0]});
            }
        }
    }
    return nodesAdded == n ? totalWeight : -1;
}
```

**Key points**:
- Very similar to Dijkstra's in structure (PQ + greedy).
- Difference: Dijkstra tracks **distance from source**, Prim's tracks **edge weight to MST**.
- Better for dense graphs (adjacency list/matrix); Kruskal's better for sparse (edge list).

---

### Kruskal's vs Prim's

| | Kruskal's | Prim's |
|---|---|---|
| **Approach** | Sort edges, add cheapest non-cycle | Grow tree, add cheapest connection |
| **Data structure** | Union-Find | PriorityQueue |
| **Input format** | Edge list | Adjacency list |
| **Better for** | Sparse graphs | Dense graphs |
| **Time** | O(E log E) | O(E log V) |
| **Simpler when** | Edges already given as list | Graph already as adjacency list |

---

### Union-Find (Disjoint Set Union)

Not a graph algorithm itself, but the backbone of Kruskal's and many connectivity problems.

```java
class UnionFind {
    int[] parent, rank;
    int components;

    UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        components = n;
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent, parent[x]);
        return parent[x];
    }

    boolean union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;  // already connected
        if (rank[px] < rank[py]) parent[px] = py;
        else if (rank[px] > rank[py]) parent[py] = px;
        else { parent[py] = px; rank[px]++; }
        components--;
        return true;
    }
}
```

**Two optimizations** (always use both):
- **Path compression**: `parent[x] = find(parent[x])` — flattens tree on every find
- **Union by rank**: attach shorter tree under taller — keeps tree balanced

Together they give nearly O(1) amortized per operation (technically O(α(n)), inverse Ackermann).

**Interview problems**:
- LC 323 (Number of Connected Components): union all edges, return `components`
- LC 684 (Redundant Connection): union edges one by one, first edge where `union` returns false is redundant
- LC 721 (Accounts Merge): union accounts sharing the same email

---

### Topological Sort

Produces a linear ordering of vertices in a **directed acyclic graph (DAG)** such that for every edge u→v, u comes before v. If a cycle exists, no valid ordering is possible.

#### When to Use

- **"Prerequisites" / "dependencies"** — LC 207, 210, 269
- **"Order of compilation / build"**
- **"Is it possible to finish all tasks?"** — cycle detection in directed graphs

#### Kahn's Algorithm (BFS) — Preferred for Interviews

**Mental model**: Repeatedly process nodes with no remaining prerequisites (in-degree 0).

```java
// Returns topological order, or empty if cycle exists
List<Integer> topoSort(int n, Map<Integer, List<Integer>> graph) {
    int[] inDegree = new int[n];
    for (var neighbors : graph.values())
        for (int next : neighbors)
            inDegree[next]++;

    Queue<Integer> queue = new ArrayDeque<>();
    for (int i = 0; i < n; i++)
        if (inDegree[i] == 0) queue.offer(i);

    List<Integer> order = new ArrayList<>();
    while (!queue.isEmpty()) {
        int curr = queue.poll();
        order.add(curr);
        for (int next : graph.getOrDefault(curr, List.of()))
            if (--inDegree[next] == 0)  // all prerequisites met
                queue.offer(next);
    }

    return order.size() == n ? order : List.of();  // empty = cycle
}
```

**Core insight**: `if (--inDegree[next] == 0) queue.offer(next)` — a node is ready only when **all** its prerequisites are processed.

#### DFS Post-Order (Alternative)

**Mental model**: DFS to the deepest dependency first, add to result on the way back (post-order), then reverse.

```java
List<Integer> topoSortDFS(int n, Map<Integer, List<Integer>> graph) {
    int[] state = new int[n];  // 0=unvisited, 1=visiting, 2=visited
    List<Integer> order = new ArrayList<>();

    for (int i = 0; i < n; i++)
        if (state[i] == 0 && hasCycle(i, graph, state, order))
            return List.of();  // cycle

    Collections.reverse(order);
    return order;
}

boolean hasCycle(int node, Map<Integer, List<Integer>> graph,
                 int[] state, List<Integer> order) {
    state[node] = 1;  // visiting (in current DFS path)
    for (int next : graph.getOrDefault(node, List.of())) {
        if (state[next] == 1) return true;   // back edge = cycle
        if (state[next] == 0 && hasCycle(next, graph, state, order))
            return true;
    }
    state[node] = 2;  // done
    order.add(node);   // post-order: add AFTER all descendants
    return false;
}
```

#### Kahn's vs DFS

| | Kahn's (BFS) | DFS Post-Order |
|---|---|---|
| **Cycle detection** | `order.size() != n` | Back edge: `state[next] == 1` |
| **Result** | Direct order | Must reverse |
| **Easier to** | Get order + count levels | Detect cycle during traversal |
| **Interview preference** | Preferred — more intuitive | Fine, but trickier to get right |

#### Key Patterns

**Build the graph — watch edge direction**:
```java
// "a must come before b" or "a is prerequisite of b"
// → edge from a to b: graph[a].add(b), inDegree[b]++

// LC 210: prerequisites[i] = [course, prereq]
// prereq → course (prereq must come first)
graph.get(prereq).add(course);  // NOT course → prereq
```

**Alien Dictionary (LC 269) — graph from sorted words**:
```java
// Compare adjacent words, first differing char gives one edge
// "wrt" vs "wrf" → t before f → edge t→f
```

#### Edge Cases

| Case | What Happens |
|---|---|
| **Cycle exists** | Kahn's: `order.size() < n`. DFS: back edge found |
| **Multiple valid orders** | Both methods produce one valid answer |
| **Disconnected graph** | Works fine — multiple starting nodes with in-degree 0 |
| **Single node** | Returns `[0]` |
| **Nodes with no edges** | In-degree 0, processed first in Kahn's |

#### Variant: Lexicographically Smallest Topological Order

When multiple nodes have in-degree 0 at the same time, a regular queue picks arbitrarily. Swap it for a **PriorityQueue** to always pick the smallest first.

**Example**: Nodes `{0,1,2,3}`, edges `2→0, 2→1, 3→0`

```
Regular Kahn's queue:  [2, 3] → could produce [2, 3, 0, 1] or [3, 2, 1, 0]
PriorityQueue Kahn's:  [2, 3] → always picks 2 first → [2, 1, 3, 0]
                        (lexicographically smallest valid order)
```

```java
// Only change: PriorityQueue instead of ArrayDeque
PriorityQueue<Integer> pq = new PriorityQueue<>();
for (int i = 0; i < n; i++)
    if (inDegree[i] == 0) pq.offer(i);

List<Integer> order = new ArrayList<>();
while (!pq.isEmpty()) {
    int curr = pq.poll();  // always picks smallest available
    order.add(curr);
    for (int next : graph.getOrDefault(curr, List.of()))
        if (--inDegree[next] == 0)
            pq.offer(next);
}
```

**Trade-off**: O(V log V) instead of O(V) due to heap operations. Only use when the problem explicitly asks for lexicographic order.

#### Common Mistakes

- **Reversing edge direction** — "prereq → course", not "course → prereq"
- **Forgetting to count all nodes** — some nodes may not appear in any edge (LC 269)
- **Not checking for cycles** — always verify `order.size() == n`

---

## Quick Comparison

| | TreeMap | ArrayDeque | PriorityQueue |
|---|---|---|---|
| **Order** | Sorted by key | Insertion order | Heap order (min by default) |
| **Min access** | O(log n) | O(1) head | O(1) peek |
| **Arbitrary remove** | O(log n) | O(n) | O(n) |
| **Neighbor query** | O(log n) | N/A | N/A |
| **Best for** | Sorted access + removal | Stack / Queue / Deque | Pure min/max stream |
