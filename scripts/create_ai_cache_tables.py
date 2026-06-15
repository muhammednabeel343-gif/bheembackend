import sqlite3
p='backend/ai_cache_test.db'
conn=sqlite3.connect(p)
c=conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS explanation_cache (
    id INTEGER PRIMARY KEY,
    cache_key VARCHAR(128) NOT NULL UNIQUE,
    request TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS upgrade_recommendations_cache (
    id INTEGER PRIMARY KEY,
    cache_key VARCHAR(128) NOT NULL UNIQUE,
    request TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

conn.commit()
print('created tables in', p)
conn.close()
