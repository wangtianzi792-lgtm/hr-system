import sqlite3
conn = sqlite3.connect('attendance.db')
cur = conn.cursor()
cur.execute("SELECT id, name FROM departments")
for row in cur.fetchall():
    print(f"ID={row[0]}, raw={row[1]!r}")
conn.close()
