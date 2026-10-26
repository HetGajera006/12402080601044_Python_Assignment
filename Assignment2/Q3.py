import csv
import getpass
import re
import sys

import mysql.connector
from mysql.connector import Error

BATCH = 5000

CREATE_STUDENT = """
CREATE TABLE IF NOT EXISTS Student (
    student_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    spi DECIMAL(4,2) NOT NULL,
    INDEX idx_spi (spi)
)"""

CREATE_REG = """
CREATE TABLE IF NOT EXISTS CourseRegistration (
    student_id INT NOT NULL,
    course_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (course_id, student_id),
    INDEX idx_student (student_id)
)"""

INSERT_STUDENT = "INSERT IGNORE INTO Student (student_id, name, spi) VALUES (%s, %s, %s)"
INSERT_REG = "INSERT IGNORE INTO CourseRegistration (student_id, course_id) VALUES (%s, %s)"

QUERY = """
SELECT s.student_id, s.name, s.spi, r.course_id
FROM Student s
JOIN CourseRegistration r ON r.student_id = s.student_id
WHERE r.course_id = %s AND s.spi > %s
ORDER BY s.spi DESC, s.student_id ASC
"""


def parse_student(row):
    sid, name, spi = int(row[0]), row[1].strip(), float(row[2])
    if not name or not (0.0 <= spi <= 10.0):
        raise ValueError("bad student row")
    return sid, name, spi


def parse_registration(row):
    sid, cid = int(row[0]), row[1].strip()
    if not cid or len(cid) > 20:
        raise ValueError("bad registration row")
    return sid, cid


def read_batches(path, parser):
    batch, bad = [], 0
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.reader(f)):
            if not row:
                continue
            try:
                batch.append(parser(row))
            except (ValueError, IndexError):
                if i > 0:
                    bad += 1
                continue
            if len(batch) >= BATCH:
                yield batch, bad
                batch, bad = [], 0
    if batch or bad:
        yield batch, bad


def load_csv(conn, path, sql, parser):
    total, bad = 0, 0
    cur = conn.cursor()
    for batch, b in read_batches(path, parser):
        if batch:
            cur.executemany(sql, batch)
        total += len(batch)
        bad += b
    conn.commit()
    cur.close()
    return total, bad


def main():
    host = input("Host [localhost]: ").strip() or "localhost"
    user = input("User: ").strip()
    password = getpass.getpass("Password: ")
    db = input("Database name: ").strip()
    if not re.fullmatch(r"\w+", db):
        print("Invalid database name.")
        sys.exit(1)
    student_csv = input("Path to student.csv: ").strip()
    reg_csv = input("Path to registration.csv: ").strip()
    course_id = input("Course id: ").strip()
    try:
        threshold = float(input("SPI threshold: ").strip())
    except ValueError:
        print("Invalid SPI threshold.")
        sys.exit(1)
    if not course_id or not (0.0 <= threshold <= 10.0):
        print("Invalid course id or threshold.")
        sys.exit(1)

    conn = None
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`")
        conn.database = db
        cur.execute(CREATE_STUDENT)
        cur.execute(CREATE_REG)
        conn.commit()
        cur.close()

        n, bad = load_csv(conn, student_csv, INSERT_STUDENT, parse_student)
        print(f"Students processed: {n}, skipped: {bad}")
        n, bad = load_csv(conn, reg_csv, INSERT_REG, parse_registration)
        print(f"Registrations processed: {n}, skipped: {bad}")

        cur = conn.cursor()
        cur.execute(QUERY, (course_id, threshold))
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            for sid, name, spi, cid in rows:
                print(sid, name, f"{float(spi):g}", cid)
        cur.close()
    except FileNotFoundError as e:
        print("File error:", e)
    except Error as e:
        print("Database error:", e)
        if conn is not None and conn.is_connected():
            conn.rollback()
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()
