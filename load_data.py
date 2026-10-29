"""Create the tables from schema.sql and load class_dataset.csv into them.

Run:  python load_data.py
Reads DATABASE_URL from .env (use Railway's PUBLIC url locally).
"""
import csv
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL not set - add it to your .env")
if "railway.internal" in DATABASE_URL:
    raise SystemExit("That's Railway's PRIVATE url. Locally you need DATABASE_PUBLIC_URL (host ends in proxy.rlwy.net).")

CSV_PATH = "class_dataset.csv"
TABLES = ["students", "tools", "student_tools", "availability_slots", "student_availability"]


def split_multi(cell):
    """'SQL; Python; Excel' -> ['SQL', 'Python', 'Excel']"""
    return [v.strip() for v in (cell or "").split(";") if v.strip()]


def get_or_create(cur, table, name, cache):
    if name not in cache:
        cur.execute(
            f"INSERT INTO {table} (name) VALUES (%s) "
            f"ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id",
            (name,),
        )
        cache[name] = cur.fetchone()[0]
    return cache[name]


def main():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn, conn.cursor() as cur:
            # 1) structure first
            with open("schema.sql", encoding="utf-8") as f:
                cur.execute(f.read())
            print("Tables created.")

            # 2) then the data
            tool_ids, slot_ids = {}, {}
            # utf-8-sig strips a BOM if Excel added one; csv handles multi-line quoted cells
            with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    cur.execute(
                        """
                        INSERT INTO students (netid, name, school_year, intro_programming,
                            skill_programming, skill_data_stats, skill_frontend_design,
                            skill_business_pitch, working_style, interests, semester_goal,
                            submitted_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING student_id
                        """,
                        (
                            row["netid"].strip(), row["name"].strip(), row["school_year"].strip(),
                            row["intro_programming"].strip(),
                            int(row["skill_programming"]), int(row["skill_data_stats"]),
                            int(row["skill_frontend_design"]), int(row["skill_business_pitch"]),
                            row["working_style"], row["interests"], row["semester_goal"],
                            row["submitted_at"],
                        ),
                    )
                    sid = cur.fetchone()[0]

                    for tool in split_multi(row["tools"]):
                        tid = get_or_create(cur, "tools", tool, tool_ids)
                        cur.execute(
                            "INSERT INTO student_tools VALUES (%s,%s) ON CONFLICT DO NOTHING",
                            (sid, tid),
                        )
                    for slot in split_multi(row["availability"]):
                        aid = get_or_create(cur, "availability_slots", slot, slot_ids)
                        cur.execute(
                            "INSERT INTO student_availability VALUES (%s,%s) ON CONFLICT DO NOTHING",
                            (sid, aid),
                        )

            # 3) row counts
            print("\nRow counts:")
            for t in TABLES:
                cur.execute(f"SELECT count(*) FROM {t}")
                print(f"  {t:<22} {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
