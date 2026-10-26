import getpass
import json
import re
import sys

TABLES = {
    "student": ("Student", "s", {"id": "student_id", "name": "name", "spi": "spi"}),
    "course": ("Course", "c", {"id": "course_id", "name": "name"}),
    "registration": ("CourseRegistration", "r", {"student_id": "student_id", "course_id": "course_id"}),
}
ALIASES = {"courseregistration": "registration"}
OPS = {"=", "<>", "<", "<=", ">", ">=", "LIKE"}
COND_RE = re.compile(r"^\s*([A-Za-z_]+\.[A-Za-z_]+)\s*(<=|>=|<>|=|<|>|LIKE)\s*(.+?)\s*$", re.I)
FROM_CLAUSE = (
    "FROM Student s "
    "JOIN CourseRegistration r ON s.student_id = r.student_id "
    "JOIN Course c ON c.course_id = r.course_id"
)


def resolve(col):
    if not isinstance(col, str) or col.count(".") != 1:
        raise ValueError(f"Invalid column: {col!r}")
    table, name = col.strip().lower().split(".")
    table = ALIASES.get(table, table)
    if table not in TABLES or name not in TABLES[table][2]:
        raise ValueError(f"Column not allowed: {col!r}")
    return f"{TABLES[table][1]}.{TABLES[table][2][name]}"


def clean_value(v):
    if isinstance(v, bool):
        raise ValueError("Boolean values are not allowed")
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        if len(v) > 100 or "\x00" in v:
            raise ValueError("Unsafe or too long string value")
        return v
    raise ValueError(f"Unsupported value type: {type(v).__name__}")


def parse_condition(cond):
    if isinstance(cond, str):
        m = COND_RE.match(cond)
        if not m:
            raise ValueError(f"Cannot parse condition: {cond!r}")
        col, op, raw = m.group(1), m.group(2).upper(), m.group(3).strip("'\"")
        try:
            val = int(raw)
        except ValueError:
            try:
                val = float(raw)
            except ValueError:
                val = raw
        return col, op, val
    if isinstance(cond, dict) and {"column", "op", "value"} <= set(cond):
        return cond["column"], str(cond["op"]).upper(), cond["value"]
    raise ValueError("Condition must be a string or {column, op, value}")


def build_query(spec):
    cols = spec.get("columns")
    if not isinstance(cols, list) or not (1 <= len(cols) <= 10):
        raise ValueError("columns must be a list of 1 to 10 items")
    select = ", ".join(resolve(c) for c in cols)

    params, where_parts = [], []
    for cond in spec.get("where", []):
        col, op, val = parse_condition(cond)
        sql_col = resolve(col)
        if op == "BETWEEN":
            if not (isinstance(val, list) and len(val) == 2):
                raise ValueError("BETWEEN needs a list of two values")
            where_parts.append(f"{sql_col} BETWEEN %s AND %s")
            params.extend(clean_value(x) for x in val)
        elif op in OPS:
            val = clean_value(val)
            if op == "LIKE" and not isinstance(val, str):
                raise ValueError("LIKE needs a string value")
            where_parts.append(f"{sql_col} {op} %s")
            params.append(val)
        else:
            raise ValueError(f"Operator not allowed: {op}")

    sql = f"SELECT {select} {FROM_CLAUSE}"
    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)

    order = spec.get("order")
    if order:
        if isinstance(order, dict):
            ocol, odir = order.get("column"), str(order.get("direction", "ASC")).upper()
        else:
            parts = str(order).split()
            if not 1 <= len(parts) <= 2:
                raise ValueError("Invalid order clause")
            ocol, odir = parts[0], (parts[1].upper() if len(parts) == 2 else "ASC")
        if odir not in ("ASC", "DESC"):
            raise ValueError("Sort direction must be ASC or DESC")
        sql += f" ORDER BY {resolve(ocol)} {odir}"

    limit = spec.get("limit", 100)
    if isinstance(limit, bool) or not isinstance(limit, int) or not (1 <= limit <= 1000):
        raise ValueError("limit must be an integer between 1 and 1000")
    sql += " LIMIT %s"
    params.append(limit)
    return sql, params


def print_table(headers, rows):
    rows = [[str(x) for x in r] for r in rows]
    widths = [max([len(h)] + [len(r[i]) for r in rows]) for i, h in enumerate(headers)]
    print(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(v.ljust(w) for v, w in zip(r, widths)))


def execute(sql, params, headers):
    import mysql.connector

    host = input("Host [localhost]: ").strip() or "localhost"
    user = input("User: ").strip()
    password = getpass.getpass("Password: ")
    db = input("Database: ").strip()
    conn = None
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=db)
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        print_table(headers, rows)
    except mysql.connector.Error as e:
        print("Database error:", e)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def main():
    raw = input("Enter JSON (single line) or path to a .json file: ").strip()
    try:
        if raw.startswith("{"):
            spec = json.loads(raw)
        else:
            with open(raw, encoding="utf-8") as f:
                spec = json.load(f)
        if not isinstance(spec, dict):
            raise ValueError("Top-level JSON must be an object")
        sql, params = build_query(spec)
    except (ValueError, OSError) as e:
        print("SQL_REJECTED:", e)
        sys.exit(1)
    print("SQL_OK")
    print("SQL:", sql)
    print("PARAMS:", params)
    if input("Execute on MySQL? (y/n): ").strip().lower() == "y":
        execute(sql, params, spec["columns"])


if __name__ == "__main__":
    main()
