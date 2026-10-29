"""Part 1d: run a few queries against the database. Run: python queries.py"""
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])

QUERIES = {
    "Student count (should match CSV rows = 23)":
        "SELECT count(*) FROM students",
    "First 5 students":
        "SELECT name, school_year FROM students LIMIT 5",
    "Tools by number of students":
        """SELECT t.name, COUNT(*) AS n_students
           FROM student_tools st
           JOIN tools t ON st.tool_id = t.id
           GROUP BY t.name
           ORDER BY n_students DESC""",
    "Availability by number of students":
        """SELECT a.name, COUNT(*) AS n_students
           FROM student_availability sa
           JOIN availability_slots a ON sa.slot_id = a.id
           GROUP BY a.name
           ORDER BY n_students DESC""",
}

with conn, conn.cursor() as cur:
    for title, sql in QUERIES.items():
        cur.execute(sql)
        print(f"\n-- {title}")
        for row in cur.fetchall():
            print("  ", *row)
conn.close()
