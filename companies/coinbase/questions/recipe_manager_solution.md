## Summary

Recipe CRUD with case-insensitive name uniqueness, search/sort, user auth, and version history with rollback. 4 levels: basic CRUD → search/sort with mixed ID types → user system → versioned edits + rollback.

## Design

**Data model:** `VersionedRecipe` list per recipeId (append-only history). Separate `activeRecipeNames` map tracks ONLY the current name for uniqueness — old version names don't participate.

**Maps:**
- `recipes`: recipeId → List<VersionedRecipe> (history, latest = getLast())
- `activeRecipeNames`: name.toLowerCase() → recipeId (current name registry)
- `users`: userId → username

**Key pattern:** Name uniqueness is case-insensitive — ALL name map keys are lowercased. Every name comparison uses `equalsIgnoreCase`, every map lookup uses `name.toLowerCase()`.

**Gotchas under pressure:**
- Same-name update: "reject if name taken BY A DIFFERENT recipe" — not just "name exists." Read condition aloud before writing: `nameExists && !belongsToThisRecipe`
- This check appears in `updateRecipe`, `editRecipe`, AND `rollbackRecipe` — same logic, easy to get wrong on copy-paste
- `updateRecipe` (Level 1) clears history and resets to version 1; `editRecipe` (Level 3+) appends new version — different semantics
- `addUser` rejects existing users (`containsKey` → false), opposite of the `!containsKey` pattern used in edit/rollback for missing users — don't copy-paste the condition
- Sort: ingredient count ASC, then recipeId ASC with numeric IDs sorted numerically

---

```java
class RecipeManager {
    private Map<String, List<VersionedRecipe>> recipes = new HashMap<>(); // recipeId to latest version
    private Map<String, String> activeRecipeNames = new HashMap<>();
    private Map<String, String> users = new HashMap<>();

    boolean addRecipe(String recipeId, String name, List<String> ingredients) {
        if (recipes.containsKey(recipeId) || activeRecipeNames.containsKey(name.toLowerCase())) {
            return false;
        }
        VersionedRecipe vr = new VersionedRecipe(1, name, ingredients);
        recipes.computeIfAbsent(recipeId, k -> new ArrayList<>()).add(vr);
        activeRecipeNames.put(name.toLowerCase(), recipeId);
        return true;
    }
    // false if recipeId already exists OR name is taken (case-insensitive)

    Map<String, Object> getRecipe(String recipeId) {
        if (!recipes.containsKey(recipeId)) {
            return null;
        }
        VersionedRecipe vr = recipes.get(recipeId).getLast();
        return Map.of("id", recipeId, "name", vr.name, "ingredients", vr.ingredients);
    }
    // Returns {id, name, ingredients} or null

    boolean updateRecipe(String recipeId, String name, List<String> ingredients) {
        if (!recipes.containsKey(recipeId)) {
            return false;
        }
        if (activeRecipeNames.containsKey(name.toLowerCase()) && !activeRecipeNames.get(name.toLowerCase()).equals(recipeId)) {
            return false;
        }
        VersionedRecipe vr = recipes.get(recipeId).getLast();
        activeRecipeNames.remove(vr.name.toLowerCase());
        recipes.get(recipeId).clear();
        recipes.get(recipeId).add(new VersionedRecipe(1, name, ingredients));
        activeRecipeNames.put(name.toLowerCase(), recipeId);
        return true;
    }
    // false if recipeId not found OR new name is taken by a different recipe

    boolean deleteRecipe(String recipeId) {
        if (!recipes.containsKey(recipeId)) {
            return false;
        }
        VersionedRecipe vr = recipes.get(recipeId).getLast();
        activeRecipeNames.remove(vr.name.toLowerCase());
        recipes.remove(recipeId);
        return true;
    }
    // false if not found

    List<Map<String, Object>> searchRecipes(String query) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Map.Entry<String, String> entry: activeRecipeNames.entrySet()) {
            if (entry.getKey().contains(query.toLowerCase())) {
                result.add(getRecipe(entry.getValue()));
            }
        }
        sortRecipes(result);
        return result;
    }
    // Case-insensitive substring match on name

    List<Map<String, Object>> getAllRecipes() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (String id: recipes.keySet()) {
            result.add(getRecipe(id));
        }
        sortRecipes(result);
        return result;
    }

    void sortRecipes(List<Map<String, Object>> result) {
        result.sort((a, b) -> {
            List<String> ingredientsA = (List<String>) a.get("ingredients");
            List<String> ingredientsB = (List<String>) b.get("ingredients");
            if (ingredientsA.size() != ingredientsB.size()) {
                return ingredientsA.size() - ingredientsB.size();
            }
            String idA = (String) a.get("id");
            String idB = (String) b.get("id");
            Integer numIdA = convertGracefully(idA);
            Integer numIdB = convertGracefully(idB);
            if (numIdA != null && numIdB != null) {
                return numIdA.compareTo(numIdB);
            }
            return idA.compareTo(idB);
        });
    }
    // Both return list sorted by: (ingredient_count ASC, recipe_id ASC)
    // recipeId: numeric sort if all digits, else lexicographic
    Integer convertGracefully(String s) {
        try {
            return Integer.valueOf(s);
        } catch(NumberFormatException e) {
            return null;
        }
    }

    boolean addUser(String userId, String username) {
        if (users.containsKey(userId)) {
            return false;
        }
        users.put(userId, username);
        return true;
    }

    boolean editRecipe(String userId, String recipeId, String name, List<String> ingredients) {
        if (!users.containsKey(userId)) {
            return false;
        }
        if (!recipes.containsKey(recipeId) ) {
            return false;
        }
        if (activeRecipeNames.containsKey(name.toLowerCase()) && !activeRecipeNames.get(name.toLowerCase()).equals(recipeId)) {
            return false;
        }

        VersionedRecipe vr = recipes.get(recipeId).getLast();
        activeRecipeNames.remove(vr.name.toLowerCase());
        recipes.get(recipeId).add(new VersionedRecipe(vr.version + 1, name, ingredients));
        activeRecipeNames.put(name.toLowerCase(), recipeId);
        return true;
    }
    // Fails if userId not found; otherwise behaves like updateRecipe
    // (In Level 4, this appends to history instead of overwriting)
    // Now appends a new version; version numbers start at 1

    List<Map<String, Object>> getRecipeHistory(String recipeId) {
        if (!recipes.containsKey(recipeId)) {
            return null;
        }
        List<VersionedRecipe> versionedRecipes = recipes.get(recipeId);
        return versionedRecipes.stream()
        .map(vr -> Map.of("version", vr.version, "name", vr.name, "ingredients", vr.ingredients))
        .toList();
    }
    // Returns [{version, name, ingredients}, ...] or null if recipe not found

    boolean rollbackRecipe(String userId, String recipeId, int version) {
        if (!users.containsKey(userId) || !recipes.containsKey(recipeId)) {
            return false;
        }
        List<VersionedRecipe> versionedRecipes = recipes.get(recipeId);
        VersionedRecipe old = null;
        for (VersionedRecipe vr: versionedRecipes) {
            if (vr.version == version) {
                old = vr;
                break;
            }
        }
        if (old == null) {
            return false;
        }
        if (activeRecipeNames.containsKey(old.name.toLowerCase()) && !activeRecipeNames.get(old.name.toLowerCase()).equals(recipeId)) {
            return false;
        }

        activeRecipeNames.remove(versionedRecipes.getLast().name.toLowerCase());
        VersionedRecipe copy = new VersionedRecipe(versionedRecipes.getLast().version + 1, old.name, old.ingredients);
        activeRecipeNames.put(old.name.toLowerCase(), recipeId);
        versionedRecipes.add(copy);
        return true;
    }
    // Copies old version's data as a new (latest) version — does not delete newer versions
    // Fails if version out of range, user invalid, or rolled-back name conflicts with another recipe

    private static class VersionedRecipe {
        int version;
        String name;
        List<String> ingredients;
        VersionedRecipe(int v, String n, List<String> i) {
            version = v;
            name = n;
            ingredients = i;
        }
    }
}
