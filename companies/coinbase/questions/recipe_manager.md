# Recipe Manager

**Category:** Coding
**Difficulty:** Medium-Hard
**Time Estimate:** 60 min
**Key Topics:** HashMap, CRUD Design, Case-Insensitive Uniqueness, Version History, User Auth

---

## Problem Statement

Build an in-memory recipe management system with progressive complexity: basic CRUD, search and sort, user authentication, and version-controlled edits with rollback.

Each recipe has:
- `recipe_id: str` — unique identifier
- `name: str` — unique (case-insensitive)
- `ingredients: list[str]`

## Requirements

### Level 1: Basic CRUD
```python
class RecipeManager:
    def add_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool
    # False if recipe_id already exists OR name is taken (case-insensitive)

    def get_recipe(self, recipe_id: str) -> dict | None
    # Returns {id, name, ingredients} or None

    def update_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool
    # False if recipe_id not found OR new name is taken by a different recipe

    def delete_recipe(self, recipe_id: str) -> bool
    # False if not found
```

### Level 2: Search and Sort
```python
def search_recipes(self, query: str) -> list[dict]
# Case-insensitive substring match on name

def get_all_recipes(self) -> list[dict]
# Both return list sorted by: (ingredient_count ASC, recipe_id ASC)
# recipe_id: numeric sort if all digits, else lexicographic
```

### Level 3: User System
```python
def add_user(self, user_id: str, username: str) -> bool

def edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool
# Fails if user_id not found; otherwise behaves like update_recipe
# (In Level 4, this appends to history instead of overwriting)
```

### Level 4: Version History
```python
def edit_recipe(...)  # Now appends a new version; version numbers start at 1

def get_recipe_history(self, recipe_id: str) -> list[dict] | None
# Returns [{version, name, ingredients}, ...] or None if recipe not found

def rollback_recipe(self, user_id: str, recipe_id: str, version: int) -> bool
# Copies old version's data as a new (latest) version — does not delete newer versions
# Fails if version out of range, user invalid, or rolled-back name conflicts with another recipe
```

---

## Solution Approach

### Level 1
**Core Idea:** Two dicts: `recipes` (id -> data) and `name_to_id` (lowercase name -> id). The second dict makes name-uniqueness checks O(1) instead of O(R).

```python
class RecipeManager:
    def __init__(self):
        self.recipes = {}      # recipe_id -> {id, history: [{name, ingredients}]}
        self.name_to_id = {}   # name.lower() -> recipe_id

    def add_recipe(self, recipe_id, name, ingredients):
        if recipe_id in self.recipes or name.lower() in self.name_to_id:
            return False
        self.recipes[recipe_id] = {
            'id': recipe_id,
            'history': [{'name': name, 'ingredients': ingredients.copy()}]
        }
        self.name_to_id[name.lower()] = recipe_id
        return True

    def get_recipe(self, recipe_id):
        if recipe_id not in self.recipes:
            return None
        current = self.recipes[recipe_id]['history'][-1]
        return {'id': recipe_id, 'name': current['name'],
                'ingredients': current['ingredients'].copy()}

    def update_recipe(self, recipe_id, name, ingredients):
        if recipe_id not in self.recipes:
            return False
        existing_id = self.name_to_id.get(name.lower())
        if existing_id is not None and existing_id != recipe_id:
            return False
        old_name = self.recipes[recipe_id]['history'][-1]['name']
        del self.name_to_id[old_name.lower()]
        self.recipes[recipe_id]['history'] = [{'name': name, 'ingredients': ingredients.copy()}]
        self.name_to_id[name.lower()] = recipe_id
        return True

    def delete_recipe(self, recipe_id):
        if recipe_id not in self.recipes:
            return False
        current_name = self.recipes[recipe_id]['history'][-1]['name']
        del self.name_to_id[current_name.lower()]
        del self.recipes[recipe_id]
        return True
```

**Complexity:** O(1) per method

### Level 2
**Core Idea:** Linear scan for search (substring match), then sort with a custom key that handles numeric vs. string IDs.

```python
def _sort_key(self, r):
    rid = r['id']
    return (len(r['ingredients']), 0, int(rid), '') if rid.isdigit() \
           else (len(r['ingredients']), 1, 0, rid)

def _to_dict(self, recipe_id):
    current = self.recipes[recipe_id]['history'][-1]
    return {'id': recipe_id, 'name': current['name'],
            'ingredients': current['ingredients'].copy()}

def search_recipes(self, query):
    q = query.lower()
    matches = [self._to_dict(rid) for rid, r in self.recipes.items()
               if q in r['history'][-1]['name'].lower()]
    return sorted(matches, key=self._sort_key)

def get_all_recipes(self):
    return sorted([self._to_dict(rid) for rid in self.recipes], key=self._sort_key)
```

**Complexity:** O(R log R) — R = total recipes

### Level 3
**Core Idea:** Add a `users` dict. `edit_recipe` is a user-gated `update_recipe`. At Level 4 it will append to history instead of overwriting.

```python
def add_user(self, user_id, username):
    if user_id in self.users:
        return False
    self.users[user_id] = {'id': user_id, 'username': username}
    return True

def edit_recipe(self, user_id, recipe_id, name, ingredients):
    if user_id not in self.users or recipe_id not in self.recipes:
        return False
    existing_id = self.name_to_id.get(name.lower())
    if existing_id is not None and existing_id != recipe_id:
        return False
    old_name = self.recipes[recipe_id]['history'][-1]['name']
    del self.name_to_id[old_name.lower()]
    self.recipes[recipe_id]['history'].append({'name': name, 'ingredients': ingredients.copy()})
    self.name_to_id[name.lower()] = recipe_id
    return True
```

**Complexity:** O(1)

### Level 4
**Core Idea:** `edit_recipe` already appends (Level 3 implementation above). Add `get_recipe_history` and `rollback_recipe`. Rollback appends a copy of the target version as the new head — does not truncate.

```python
def get_recipe_history(self, recipe_id):
    if recipe_id not in self.recipes:
        return None
    return [{'version': i + 1, 'name': v['name'], 'ingredients': v['ingredients'].copy()}
            for i, v in enumerate(self.recipes[recipe_id]['history'])]

def rollback_recipe(self, user_id, recipe_id, version):
    if user_id not in self.users or recipe_id not in self.recipes:
        return False
    history = self.recipes[recipe_id]['history']
    if version < 1 or version > len(history):
        return False
    target = history[version - 1]
    current_name = history[-1]['name']
    if target['name'].lower() != current_name.lower():
        conflict = self.name_to_id.get(target['name'].lower())
        if conflict is not None and conflict != recipe_id:
            return False
    del self.name_to_id[current_name.lower()]
    history.append({'name': target['name'], 'ingredients': target['ingredients'].copy()})
    self.name_to_id[target['name'].lower()] = recipe_id
    return True
```

**Complexity:** O(V) for `get_recipe_history`, O(1) for `rollback_recipe` — V = versions

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Concurrency:** `edit_recipe` is a multi-step read-modify-write on `recipes` and `name_to_id`. Concurrent edits to the same recipe will corrupt both structures. Use a per-recipe lock or optimistic concurrency (version counter + CAS).
- **name_to_id consistency:** Every mutating operation must maintain `name_to_id` in sync. If any code path raises mid-operation (e.g., after `del name_to_id[old]` but before inserting the new name), the index is corrupted. Wrap in a try/except with rollback, or restructure to be crash-safe.
- **Memory for version history:** Storing full snapshots per version is O(V * size_of_recipe). For large ingredient lists, store diffs (deltas) instead. Tradeoff: cheaper storage, more expensive reconstruction.
- **Persistence:** In-memory state is lost on restart. Production would back this with a DB. Version history maps naturally to an append-only log or event-sourced model.
- **Search at scale:** Linear scan is O(R) per query. For large recipe sets, index names in a trie or full-text search engine (Elasticsearch, Postgres tsvector). The case-insensitive substring match is essentially `ILIKE '%query%'` in SQL.

### Common Interview Traps
- **Same-recipe name update:** `update_recipe("1", "Pasta", [...])` when recipe 1's current name IS "Pasta" (just different capitalization) must succeed. The check `existing_id != recipe_id` handles this — verify you include it.
- **`name_to_id` not cleaned up on delete:** Forgetting to remove the name entry on delete means the name is permanently reserved even after the recipe is gone.
- **`update_recipe` vs. `edit_recipe` history behavior:** Level 1's `update_recipe` overwrites (resets history to one entry). Level 3's `edit_recipe` appends. This distinction is subtle and easy to conflate.
- **Rollback name conflict:** Rolling back to version 1 ("Pasta") when another recipe has since taken that name must return False. Don't skip this check because "it's my own recipe" — the name could now belong to a different recipe_id.
- **Version numbers are 1-indexed:** Off-by-one on `history[version - 1]` is an easy mistake under pressure.

### How to Push Forward as Staff+
- **Flag the dual-dict invariant immediately:** "I'm maintaining two data structures that must stay in sync — `recipes` and `name_to_id`. Every mutating method is essentially a transaction. In production, I'd either use a DB transaction or design the mutation order so partial failure is recoverable."
- **Propose event sourcing:** "Version history is a natural fit for an event-sourced model — `add_recipe` and `edit_recipe` are events, current state is a projection. This also gives us an audit log, which is critical in a financial context."
- **Connect to Coinbase domain:** User-owned assets with version-controlled state is directly analogous to Coinbase's wallet configuration, API key management, or any user-facing resource that needs an audit trail and rollback capability. Regulatory requirements (SOX, BSA) demand exactly this kind of audit history for financial systems.
- **Sorting edge case — mixed IDs:** The sort key handles numeric IDs and string IDs separately. Proactively clarify: "I'm assuming IDs are either all-numeric or all-alphabetic. If they can mix (e.g., 'r1', '2'), I need a different sort key." Show you anticipate ambiguity.
- **Search improvement:** "The current search is O(R) substring scan. If search is frequent, I'd add a trie on recipe names — O(Q) lookup where Q = query length. Trade memory for query speed."
