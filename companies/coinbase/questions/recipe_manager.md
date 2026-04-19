# Recipe Manager

**Category:** Coding
**Difficulty:** Medium-Hard
**Time Estimate:** 60 min
**Key Topics:** HashMap, CRUD Design, Case-Insensitive Uniqueness, Version History, User Auth

---

## Problem Statement

Build an in-memory recipe management system with progressive complexity: basic CRUD, search and sort, user authentication, and version-controlled edits with rollback.

Each recipe has:
- `recipeId: String` — unique identifier
- `name: String` — unique (case-insensitive)
- `ingredients: List<String>`

## Requirements

### Level 1: Basic CRUD
```java
class RecipeManager {
    boolean addRecipe(String recipeId, String name, List<String> ingredients)
    // false if recipeId already exists OR name is taken (case-insensitive)

    Map<String, Object> getRecipe(String recipeId)
    // Returns {id, name, ingredients} or null

    boolean updateRecipe(String recipeId, String name, List<String> ingredients)
    // false if recipeId not found OR new name is taken by a different recipe

    boolean deleteRecipe(String recipeId)
    // false if not found
}
```

### Level 2: Search and Sort
```java
List<Map<String, Object>> searchRecipes(String query)
// Case-insensitive substring match on name

List<Map<String, Object>> getAllRecipes()
// Both return list sorted by: (ingredient_count ASC, recipe_id ASC)
// recipeId: numeric sort if all digits, else lexicographic
```

### Level 3: User System
```java
boolean addUser(String userId, String username)

boolean editRecipe(String userId, String recipeId, String name, List<String> ingredients)
// Fails if userId not found; otherwise behaves like updateRecipe
// (In Level 4, this appends to history instead of overwriting)
```

### Level 4: Version History
```java
boolean editRecipe(...)  // Now appends a new version; version numbers start at 1

List<Map<String, Object>> getRecipeHistory(String recipeId)
// Returns [{version, name, ingredients}, ...] or null if recipe not found

boolean rollbackRecipe(String userId, String recipeId, int version)
// Copies old version's data as a new (latest) version — does not delete newer versions
// Fails if version out of range, user invalid, or rolled-back name conflicts with another recipe
```

---

## Solution Approach

### Level 1
**Core Idea:** Two maps: `recipes` (id -> data) and `nameToId` (lowercase name -> id). The second map makes name-uniqueness checks O(1) instead of O(R).

```java
import java.util.*;

class RecipeManager {
    // recipeId -> {id, history: List<{name, ingredients}>}
    private final Map<String, Map<String, Object>> recipes = new HashMap<>();
    private final Map<String, String> nameToId = new HashMap<>(); // name.lower() -> recipeId

    boolean addRecipe(String recipeId, String name, List<String> ingredients) {
        if (recipes.containsKey(recipeId) || nameToId.containsKey(name.toLowerCase()))
            return false;
        List<Map<String, Object>> history = new ArrayList<>();
        history.add(Map.of("name", name, "ingredients", new ArrayList<>(ingredients)));
        recipes.put(recipeId, new HashMap<>(Map.of("id", recipeId, "history", history)));
        nameToId.put(name.toLowerCase(), recipeId);
        return true;
    }

    Map<String, Object> getRecipe(String recipeId) {
        if (!recipes.containsKey(recipeId)) return null;
        List<Map<String, Object>> history = getHistory(recipeId);
        Map<String, Object> current = history.get(history.size() - 1);
        return Map.of("id", recipeId, "name", current.get("name"),
                      "ingredients", new ArrayList<>((List<?>) current.get("ingredients")));
    }

    boolean updateRecipe(String recipeId, String name, List<String> ingredients) {
        if (!recipes.containsKey(recipeId)) return false;
        String existingId = nameToId.get(name.toLowerCase());
        if (existingId != null && !existingId.equals(recipeId)) return false;
        List<Map<String, Object>> history = getHistory(recipeId);
        String oldName = (String) history.get(history.size() - 1).get("name");
        nameToId.remove(oldName.toLowerCase());
        history.clear();
        history.add(Map.of("name", name, "ingredients", new ArrayList<>(ingredients)));
        nameToId.put(name.toLowerCase(), recipeId);
        return true;
    }

    boolean deleteRecipe(String recipeId) {
        if (!recipes.containsKey(recipeId)) return false;
        List<Map<String, Object>> history = getHistory(recipeId);
        String currentName = (String) history.get(history.size() - 1).get("name");
        nameToId.remove(currentName.toLowerCase());
        recipes.remove(recipeId);
        return true;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> getHistory(String recipeId) {
        return (List<Map<String, Object>>) recipes.get(recipeId).get("history");
    }
}
```

**Complexity:** O(1) per method

### Level 2
**Core Idea:** Linear scan for search (substring match), then sort with a custom comparator that handles numeric vs. string IDs.

```java
private Comparator<Map<String, Object>> sortKey() {
    return (a, b) -> {
        List<?> ai = (List<?>) a.get("ingredients");
        List<?> bi = (List<?>) b.get("ingredients");
        if (ai.size() != bi.size()) return Integer.compare(ai.size(), bi.size());
        String aid = (String) a.get("id"), bid = (String) b.get("id");
        boolean aNum = aid.chars().allMatch(Character::isDigit);
        boolean bNum = bid.chars().allMatch(Character::isDigit);
        if (aNum && bNum) return Long.compare(Long.parseLong(aid), Long.parseLong(bid));
        if (aNum) return -1;
        if (bNum) return 1;
        return aid.compareTo(bid);
    };
}

private Map<String, Object> toDict(String recipeId) {
    List<Map<String, Object>> history = getHistory(recipeId);
    Map<String, Object> current = history.get(history.size() - 1);
    return Map.of("id", recipeId, "name", current.get("name"),
                  "ingredients", new ArrayList<>((List<?>) current.get("ingredients")));
}

List<Map<String, Object>> searchRecipes(String query) {
    String q = query.toLowerCase();
    List<Map<String, Object>> matches = new ArrayList<>();
    for (Map.Entry<String, Map<String, Object>> entry : recipes.entrySet()) {
        List<Map<String, Object>> history = getHistory(entry.getKey());
        String name = (String) history.get(history.size() - 1).get("name");
        if (name.toLowerCase().contains(q)) matches.add(toDict(entry.getKey()));
    }
    matches.sort(sortKey());
    return matches;
}

List<Map<String, Object>> getAllRecipes() {
    List<Map<String, Object>> result = new ArrayList<>();
    for (String rid : recipes.keySet()) result.add(toDict(rid));
    result.sort(sortKey());
    return result;
}
```

**Complexity:** O(R log R) — R = total recipes

### Level 3
**Core Idea:** Add a `users` map. `editRecipe` is a user-gated `updateRecipe`. At Level 4 it will append to history instead of overwriting.

```java
private final Map<String, Map<String, String>> users = new HashMap<>();

boolean addUser(String userId, String username) {
    if (users.containsKey(userId)) return false;
    users.put(userId, Map.of("id", userId, "username", username));
    return true;
}

boolean editRecipe(String userId, String recipeId, String name, List<String> ingredients) {
    if (!users.containsKey(userId) || !recipes.containsKey(recipeId)) return false;
    String existingId = nameToId.get(name.toLowerCase());
    if (existingId != null && !existingId.equals(recipeId)) return false;
    List<Map<String, Object>> history = getHistory(recipeId);
    String oldName = (String) history.get(history.size() - 1).get("name");
    nameToId.remove(oldName.toLowerCase());
    history.add(Map.of("name", name, "ingredients", new ArrayList<>(ingredients)));
    nameToId.put(name.toLowerCase(), recipeId);
    return true;
}
```

**Complexity:** O(1)

### Level 4
**Core Idea:** `editRecipe` already appends (Level 3 implementation above). Add `getRecipeHistory` and `rollbackRecipe`. Rollback appends a copy of the target version as the new head — does not truncate.

```java
List<Map<String, Object>> getRecipeHistory(String recipeId) {
    if (!recipes.containsKey(recipeId)) return null;
    List<Map<String, Object>> history = getHistory(recipeId);
    List<Map<String, Object>> result = new ArrayList<>();
    for (int i = 0; i < history.size(); i++) {
        Map<String, Object> v = history.get(i);
        result.add(Map.of("version", i + 1, "name", v.get("name"),
                          "ingredients", new ArrayList<>((List<?>) v.get("ingredients"))));
    }
    return result;
}

boolean rollbackRecipe(String userId, String recipeId, int version) {
    if (!users.containsKey(userId) || !recipes.containsKey(recipeId)) return false;
    List<Map<String, Object>> history = getHistory(recipeId);
    if (version < 1 || version > history.size()) return false;
    Map<String, Object> target = history.get(version - 1);
    String targetName = (String) target.get("name");
    String currentName = (String) history.get(history.size() - 1).get("name");
    if (!targetName.equalsIgnoreCase(currentName)) {
        String conflict = nameToId.get(targetName.toLowerCase());
        if (conflict != null && !conflict.equals(recipeId)) return false;
    }
    nameToId.remove(currentName.toLowerCase());
    history.add(Map.of("name", targetName,
                       "ingredients", new ArrayList<>((List<?>) target.get("ingredients"))));
    nameToId.put(targetName.toLowerCase(), recipeId);
    return true;
}
```

**Complexity:** O(V) for `getRecipeHistory`, O(1) for `rollbackRecipe` — V = versions

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Concurrency:** `editRecipe` is a multi-step read-modify-write on `recipes` and `nameToId`. Concurrent edits to the same recipe will corrupt both structures. Use a per-recipe lock (`ReentrantLock`) or optimistic concurrency (version counter + CAS).
- **nameToId consistency:** Every mutating operation must maintain `nameToId` in sync. If any code path throws mid-operation (e.g., after `nameToId.remove(old)` but before inserting the new name), the index is corrupted. Wrap in a try/finally with rollback, or restructure to be crash-safe.
- **Memory for version history:** Storing full snapshots per version is O(V * size_of_recipe). For large ingredient lists, store diffs (deltas) instead. Tradeoff: cheaper storage, more expensive reconstruction.
- **Persistence:** In-memory state is lost on restart. Production would back this with a DB. Version history maps naturally to an append-only log or event-sourced model.
- **Search at scale:** Linear scan is O(R) per query. For large recipe sets, index names in a trie or full-text search engine (Elasticsearch, Postgres tsvector). The case-insensitive substring match is essentially `ILIKE '%query%'` in SQL.

### Common Interview Traps
- **Same-recipe name update:** `updateRecipe("1", "Pasta", [...])` when recipe 1's current name IS "Pasta" (just different capitalization) must succeed. The check `!existingId.equals(recipeId)` handles this — verify you include it.
- **`nameToId` not cleaned up on delete:** Forgetting to remove the name entry on delete means the name is permanently reserved even after the recipe is gone.
- **`updateRecipe` vs. `editRecipe` history behavior:** Level 1's `updateRecipe` overwrites (resets history to one entry). Level 3's `editRecipe` appends. This distinction is subtle and easy to conflate.
- **Rollback name conflict:** Rolling back to version 1 ("Pasta") when another recipe has since taken that name must return false. Don't skip this check because "it's my own recipe" — the name could now belong to a different recipeId.
- **Version numbers are 1-indexed:** Off-by-one on `history.get(version - 1)` is an easy mistake under pressure.

### How to Push Forward as Staff+
- **Flag the dual-map invariant immediately:** "I'm maintaining two data structures that must stay in sync — `recipes` and `nameToId`. Every mutating method is essentially a transaction. In production, I'd either use a DB transaction or design the mutation order so partial failure is recoverable."
- **Propose event sourcing:** "Version history is a natural fit for an event-sourced model — `addRecipe` and `editRecipe` are events, current state is a projection. This also gives us an audit log, which is critical in a financial context."
- **Connect to Coinbase domain:** User-owned assets with version-controlled state is directly analogous to Coinbase's wallet configuration, API key management, or any user-facing resource that needs an audit trail and rollback capability. Regulatory requirements (SOX, BSA) demand exactly this kind of audit history for financial systems.
- **Sorting edge case — mixed IDs:** The sort key handles numeric IDs and string IDs separately. Proactively clarify: "I'm assuming IDs are either all-numeric or all-alphabetic. If they can mix (e.g., 'r1', '2'), I need a different sort key." Show you anticipate ambiguity.
- **Search improvement:** "The current search is O(R) substring scan. If search is frequent, I'd add a trie on recipe names — O(Q) lookup where Q = query length. Trade memory for query speed."
