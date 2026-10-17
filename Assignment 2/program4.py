
import mysql.connector


# Only allow approved columns in SQL queries.
ALLOWED_COLUMNS = {
    "student.id": "s.student_id",
    "student.name": "s.name",
    "student.spi": "s.SPI",
    "course.id": "c.course_id",
    "course.name": "c.course_name",
    "registration.course_id": "cr.course_id"
}

ALLOWED_FILTERS = {
    "=": "=",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "LIKE": "LIKE"
}


def build_query(columns, filters, order_column, direction, limit):
    if not columns:
        raise ValueError("Select at least one column.")

    for column in columns:
        if column not in ALLOWED_COLUMNS:
            raise ValueError("Invalid column: " + column)

    if order_column not in ALLOWED_COLUMNS:
        raise ValueError("Invalid order column.")

    direction = direction.upper()
    if direction not in ("ASC", "DESC"):
        raise ValueError("Sort direction must be ASC or DESC.")

    if not 1 <= limit <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    selected = ", ".join(ALLOWED_COLUMNS[col] for col in columns)

    query = f"""
        SELECT {selected}
        FROM Student s
        JOIN CourseRegistration cr
            ON s.student_id = cr.student_id
        JOIN Course c
            ON cr.course_id = c.course_id
    """

    conditions = []
    parameters = []

    for column, operator, value in filters:
        if column not in ALLOWED_COLUMNS:
            raise ValueError("Invalid filter column.")

        if operator.upper() not in ALLOWED_FILTERS:
            raise ValueError("Invalid filter operator.")

        sql_column = ALLOWED_COLUMNS[column]
        sql_operator = ALLOWED_FILTERS[operator.upper()]

        conditions.append(f"{sql_column} {sql_operator} %s")
        parameters.append(value)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += (
        f" ORDER BY {ALLOWED_COLUMNS[order_column]} {direction}"
        f" LIMIT {limit}"
    )

    return query, parameters


def main():
    connection = None
    cursor = None

    try:
        # Example query configuration.
        columns = ["student.name", "course.name"]

        filters = [
            ("course.id", "=", "PY101")
        ]

        order_column = "student.spi"
        direction = "DESC"
        limit = 2

        query, parameters = build_query(
            columns, filters, order_column, direction, limit
        )

        print("SQL_OK")
        print("Query:", " ".join(query.split()))
        print("Parameters:", parameters)

        # Configure your existing MySQL database.
        connection = mysql.connector.connect(
            host="localhost",
            user=input("MySQL username: ").strip(),
            password=input("MySQL password: "),
            database=input("Database name: ").strip()
        )

        cursor = connection.cursor()
        cursor.execute(query, parameters)

        for row in cursor.fetchall():
            print(*row)

    except (ValueError, mysql.connector.Error) as error:
        print("Error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
