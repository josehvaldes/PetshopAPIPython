CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,              -- 'human' or 'ai'
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questionnaire (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    breed TEXT,
    age INTEGER,
    name TEXT,
    temperament TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
