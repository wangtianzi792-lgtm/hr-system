# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect('attendance.db')
conn.text_factory = lambda x: x.decode('utf-8', 'replace')
cur = conn.cursor()
cur.execute("SELECT id, name FROM departments")
print("Depts:", cur.fetchall())
cur.execute("SELECT id, name, employee_no FROM employees")
print("Emps:", cur.fetchall())
conn.close()
