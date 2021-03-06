DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tasks;
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone CHARACTER(20) NULL
);
CREATE TABLE tasks(
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);