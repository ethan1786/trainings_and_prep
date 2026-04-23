class CloudFileSystem {
    private Map<String, String> storageByUser = new HashMap<>();
    private Map<String, User> users = new HashMap<>();
    private String adminUserName = "admin";
    private int unlimited = -1;

    CloudFileSystem() {
        User admin = new User(adminUserName, unlimited);
        users.put(adminUserName, admin);
    }

    boolean addFile(String name, int size) {
        return addFileBy(adminUserName, name, size);
    }
    // Returns false if name already exists

    int getFileSize(String name) {
        return getFileSize(adminUserName, name);
    }
    // Returns -1 if file does not exist

    int getFileSize(String userId, String name) {
        if (!users.containsKey(userId)) {
            return -1;
        }
        return users.get(userId).storage.getOrDefault(name, -1);
    }


    boolean deleteFile(String name) {
        return deleteFile(adminUserName, name);
    }
    // Returns false if file does not exist

    boolean deleteFile(String userId, String name) {
        if (!users.containsKey(userId)) {
            return false;
        }
        User u = users.get(userId);
        if (!u.storage.containsKey(name)) {
            return false;
        }
        u.storage.remove(name);
        storageByUser.remove(name);
        return true;
    }


    boolean copyFile(String source, String dest) {
        return copyFile(adminUserName, source, dest);
    }
    boolean copyFile(String userId, String source, String dest) {
        if (!users.containsKey(userId)) {
            return false;
        }
        User u = users.get(userId);
        if (!u.storage.containsKey(source)) {
            return false;
        }
        return addFileBy(userId, dest, u.storage.get(source));
    }
    // Returns false if source missing or dest already exists


    List<String> findFiles(String prefix, int n) {
        return findFiles(adminUserName, prefix, n);
    }
    List<String> findFiles(String userId, String prefix, int n) {
        if (!users.containsKey(userId)) {
            return List.of();
        }
        User u = users.get(userId);
        return u.storage.entrySet().stream()
        .filter(entry -> entry.getKey().startsWith(prefix))
        .sorted((a, b) -> {
            int comp = Integer.compare(b.getValue(), a.getValue());
            return comp != 0 ? comp : a.getKey().compareTo(b.getKey());
        })
        .limit(n)
        .map(entry -> new StringBuilder().append(entry.getKey()).append("(").append(entry.getValue()).append(")").toString())
        .toList();
    }
    // Returns up to N files whose names start with prefix
    // Format: "name(size)", sorted by size DESC, then name ASC on ties


    boolean addUser(String userId, int capacity) {
        if (capacity <= 0 || users.containsKey(userId)) {
            return false;
        }
        users.put(userId, new User(userId, capacity));
        return true;
    }
    // "admin" is reserved; files from addFile() belong to admin (unlimited)

    boolean addFileBy(String userId, String name, int size) {
        if(!users.containsKey(userId) || storageByUser.containsKey(name)) {
            return false;
        }
        User u = users.get(userId);
        if (u.storage.size() != unlimited && u.storage.size() == u.capacity) {
            return false;
        }
        u.storage.put(name, size);
        storageByUser.put(name, userId);
        return true;
    }
    // Fails if user missing, name taken, or would exceed capacity

    boolean mergeUser(String userId1, String userId2) {
        if (!users.containsKey(userId1) || !users.containsKey(userId2) || userId1.equals(userId2)
            || userId1.equals(adminUserName) || userId2.equals(adminUserName)) {
            return false;
        }
        User user1 = users.get(userId1);
        User user2 = users.get(userId2);
        user1.capacity += user2.capacity;
        for (Map.Entry<String, Integer> entry: user2.storage.entrySet()) {
            user1.storage.put(entry.getKey(), entry.getValue());
            storageByUser.put(entry.getKey(), userId1);
        }
        user2.isDeleted = true;
        users.remove(userId2);
        return true;
    }
    // userId2's files and capacity transfer to userId1; userId2 is deleted
    // admin cannot be merged (as source or target)

    int backup(String userId) {
        if (!users.containsKey(userId)) {
            return -1;
        }
        User u = users.get(userId);
        u.backup.clear();
        u.backup.putAll(u.storage);
        return u.backup.size();
    }
    // Snapshot user's files; returns count or -1 if user missing
    // Overwrites any prior backup for this user

    int restore(String userId) {
        if (!users.containsKey(userId)) {
            return -1;
        }
        User u = users.get(userId);
        if (u.backup.isEmpty()) {
            for (String key: u.storage.keySet()) {
                storageByUser.remove(key);
            }
            u.storage.clear();
            return 0;
        }
        AtomicInteger restored = new AtomicInteger(0);
        u.backup.entrySet().stream()
        .sorted((a, b) -> a.getKey().compareTo(b.getKey()))
        .forEach(entry -> {
            if (u.storage.size() < u.capacity && !u.storage.containsKey(entry.getKey())
                && !storageByUser.containsKey(entry.getKey())) {
                u.storage.put(entry.getKey(), entry.getValue());
                storageByUser.put(entry.getKey(), userId);
                restored.incrementAndGet();
            }
        });
        u.backup.clear();
        return restored.get();
    }
    // Restore from backup; returns files restored or -1 if user missing
    // If no backup exists: delete all user's files, return 0
    // Skip files already owned by this user (keep current version)
    // Skip files whose name is taken by another user
    // Restore alphabetically; skip if capacity would be exceeded
    // Clears backup after restore


    private static class User {
        String userId;
        int capacity;
        Map<String, Integer> storage = new HashMap<>();
        Map<String, Integer> backup = new HashMap<>();
        boolean isDeleted;
        User(String id, int c) {
            userId = id;
            capacity = c;
        }
    }
}
