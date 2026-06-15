import sqlite3
p='backend/ai_cache_test.db'
conn=sqlite3.connect(p)
c=conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print(c.fetchall())
# Check schema for explanation_cache
c.execute("PRAGMA table_info('explanation_cache')")
print('explanation_cache cols:', c.fetchall())
# Check schema for upgrade_recommendations_cache
c.execute("PRAGMA table_info('upgrade_recommendations_cache')")
print('upgrade_recommendations_cache cols:', c.fetchall())
conn.close()
