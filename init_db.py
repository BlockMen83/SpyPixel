import sqlite3

conn = sqlite3.connect('pixels.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS pixels (
    id TEXT PRIMARY KEY,
    recipient TEXT,
    access_time TIMESTAMP,
    counter INTEGER,
    notes TEXT  -- Add a new column for notes
)
''')

conn.commit()
conn.close()
