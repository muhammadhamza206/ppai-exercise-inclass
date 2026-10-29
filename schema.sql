-- Schema for class_dataset.csv
-- Rules: entity -> table, 1:N -> foreign key, M:N -> bridge table.
-- Safe to re-run: drops everything first (bridges before parents).

DROP TABLE IF EXISTS student_availability;
DROP TABLE IF EXISTS student_tools;
DROP TABLE IF EXISTS availability_slots;
DROP TABLE IF EXISTS tools;
DROP TABLE IF EXISTS students;

-- One row per student. Name can't be the PK (two people can share a name),
-- so we generate student_id.
CREATE TABLE students (
    student_id            SERIAL PRIMARY KEY,
    netid                 TEXT NOT NULL UNIQUE,  -- messy in the CSV (some emails / N-numbers), so not used as PK
    name                  TEXT NOT NULL,
    school_year           TEXT NOT NULL
        CHECK (school_year IN ('First-year', 'Sophomore', 'Junior', 'Senior')),
    intro_programming     TEXT NOT NULL
        CHECK (intro_programming IN ('took_it', 'equivalent', 'neither')),
    -- The four skill ratings are single-valued attributes of a student (1-5)
    skill_programming     SMALLINT NOT NULL CHECK (skill_programming BETWEEN 1 AND 5),
    skill_data_stats      SMALLINT NOT NULL CHECK (skill_data_stats BETWEEN 1 AND 5),
    skill_frontend_design SMALLINT NOT NULL CHECK (skill_frontend_design BETWEEN 1 AND 5),
    skill_business_pitch  SMALLINT NOT NULL CHECK (skill_business_pitch BETWEEN 1 AND 5),
    working_style         TEXT,
    interests             TEXT,
    semester_goal         TEXT,
    submitted_at          TIMESTAMPTZ NOT NULL   -- a timestamp, not text
);

-- tools: many-to-many (a student uses many tools; a tool is used by many students)
CREATE TABLE tools (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE student_tools (
    student_id INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    tool_id    INT NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, tool_id)
);

-- availability: same pattern as tools
CREATE TABLE availability_slots (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE          -- e.g. 'Weekend afternoons'
);

CREATE TABLE student_availability (
    student_id INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    slot_id    INT NOT NULL REFERENCES availability_slots(id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, slot_id)
);
