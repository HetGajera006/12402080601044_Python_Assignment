
import csv
import mysql.connector
from mysql.connector import Error


def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            student_id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            SPI DECIMAL(3,1) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CourseRegistration (
            student_id INT,
            course_id VARCHAR(20),
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id)
        )
    """)

    connection.commit()
    cursor.close()


def import_students(connection, file_path):
    cursor = connection.cursor()

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT INTO Student (student_id, name, SPI)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    SPI = VALUES(SPI)
            """, (
                int(row["student_id"]),
                row["name"],
                float(row["SPI"])
            ))

    connection.commit()
    cursor.close()


def import_registrations(connection, file_path):
    cursor = connection.cursor()

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT IGNORE INTO CourseRegistration
                (student_id, course_id)
                VALUES (%s, %s)
            """, (
                int(row["student_id"]),
                row["course_id"]
            ))

    connection.commit()
    cursor.close()


def display_students(connection, course_id, threshold):
    cursor = connection.cursor()

    query = """
        SELECT s.student_id, s.name, s.SPI, cr.course_id
        FROM Student s
        JOIN CourseRegistration cr
            ON s.student_id = cr.student_id
        WHERE cr.course_id = %s AND s.SPI > %s
        ORDER BY s.SPI DESC, s.student_id ASC
    """

    cursor.execute(query, (course_id, threshold))

    for student_id, name, spi, course in cursor.fetchall():
        print(student_id, name, spi, course)

    cursor.close()


def main():
    connection = None

    try:
        host = input("MySQL host (default localhost): ").strip() or "localhost"
        user = input("MySQL username: ").strip()
        password = input("MySQL password: ")
        database = input("Existing database name: ").strip()

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Connected to MySQL successfully.")

            create_tables(connection)

            student_file = input("Student CSV file path: ").strip()
            registration_file = input(
                "Registration CSV file path: "
            ).strip()

            import_students(connection, student_file)
            import_registrations(connection, registration_file)

            course_id = input("Enter course ID: ").strip()
            threshold = float(input("Enter SPI threshold: "))

            if not 0 <= threshold <= 10:
                print("Error: SPI threshold must be between 0 and 10.")
                return

            display_students(connection, course_id, threshold)

    except Error as error:
        print("MySQL error:", error)
    except (OSError, ValueError, KeyError) as error:
        print("Input or file error:", error)
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")


if __name__ == "__main__":
    main()
