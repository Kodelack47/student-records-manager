"""
student_db.py

Menu-driven command-line program for managing student records in a
SQLite database. Add, view, update, and delete students, with input
validation and error handling around the parts that can actually fail
(bad IDs, missing '@' in an email, database errors, etc).

Everything is split into small functions on purpose - one job per
function - so each database operation can be read (and tested) on its
own instead of as one giant block of code.

References are at the bottom of the file.

- Ousmana Tunkara
"""

import sqlite3

DB_NAME = "students.db"


def connect_db(db_name=DB_NAME):
    """
    Opens a connection to the SQLite database file, creating the file
    itself if it doesn't already exist yet (sqlite3.connect() does this
    automatically - it's not something I have to check for manually).
    """
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Could not connect to the database: {e}")
        return None


def create_table(conn):
    """Creates the students table if it isn't already there."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                email TEXT
            )
            """
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Could not create the students table: {e}")


def is_valid_email(email):
    """Very basic check - just makes sure there's an '@' with something
    on both sides of it. Not trying to fully validate real email syntax,
    just catch obvious typos like leaving it blank or forgetting the @."""
    if "@" not in email:
        return False
    local_part, _, domain_part = email.partition("@")
    return len(local_part) > 0 and len(domain_part) > 0


def get_valid_id(prompt):
    """Keeps asking until the user gives an actual whole number for an ID,
    instead of letting a typo crash the program with a ValueError."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("That's not a valid ID - please enter a whole number.\n")


def add_student(conn):
    print("\n--- Add a New Student ---")

    student_id = get_valid_id("Student ID (whole number): ")

    name = input("Name: ").strip()
    while not name:
        print("Name can't be blank.")
        name = input("Name: ").strip()

    grade = input("Grade: ").strip()

    email = input("Email: ").strip()
    while not is_valid_email(email):
        print("That doesn't look like a valid email (needs an '@' with something on both sides).")
        email = input("Email: ").strip()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (id, name, grade, email) VALUES (?, ?, ?, ?)",
            (student_id, name, grade, email),
        )
        conn.commit()
        print(f"Student {name} (ID {student_id}) added.")
    except sqlite3.IntegrityError:
        print(f"A student with ID {student_id} already exists. Try updating it instead.")
    except sqlite3.Error as e:
        print(f"Something went wrong adding that student: {e}")


def view_students(conn):
    print("\n--- All Students ---")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, grade, email FROM students ORDER BY id")
        rows = cursor.fetchall()

        if not rows:
            print("No students in the database yet.")
            return

        print(f"{'ID':<6}{'Name':<20}{'Grade':<14}{'Email':<25}")
        print("-" * 65)
        for row in rows:
            student_id, name, grade, email = row
            print(f"{student_id:<6}{name:<20}{(grade or ''):<14}{(email or ''):<25}")
    except sqlite3.Error as e:
        print(f"Could not read student records: {e}")


def find_student(conn, student_id):
    """Small helper used by both update_student and delete_student so I'm
    not writing the same SELECT twice."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, grade, email FROM students WHERE id = ?", (student_id,))
    return cursor.fetchone()


def update_student(conn):
    print("\n--- Update a Student ---")
    student_id = get_valid_id("Enter the ID of the student to update: ")

    existing = find_student(conn, student_id)
    if existing is None:
        print(f"No student found with ID {student_id}.")
        return

    print(f"Current record: ID {existing[0]}, {existing[1]}, Grade {existing[2]}, {existing[3]}")
    print("Leave a field blank to keep its current value.\n")

    new_name = input(f"New name [{existing[1]}]: ").strip()
    new_grade = input(f"New grade [{existing[2]}]: ").strip()

    new_email = input(f"New email [{existing[3]}]: ").strip()
    while new_email and not is_valid_email(new_email):
        print("That doesn't look like a valid email (needs an '@' with something on both sides).")
        new_email = input(f"New email [{existing[3]}]: ").strip()

    # fall back to the existing value for anything left blank
    name = new_name if new_name else existing[1]
    grade = new_grade if new_grade else existing[2]
    email = new_email if new_email else existing[3]

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, grade = ?, email = ? WHERE id = ?",
            (name, grade, email, student_id),
        )
        conn.commit()
        print(f"Student ID {student_id} updated.")
    except sqlite3.Error as e:
        print(f"Something went wrong updating that student: {e}")


def delete_student(conn):
    print("\n--- Delete a Student ---")
    student_id = get_valid_id("Enter the ID of the student to delete: ")

    existing = find_student(conn, student_id)
    if existing is None:
        print(f"No student found with ID {student_id}.")
        return

    print(f"About to delete: ID {existing[0]}, {existing[1]}, Grade {existing[2]}, {existing[3]}")
    confirm = input("Are you sure? This can't be undone (y/n): ").strip().lower()

    if confirm != "y":
        print("Delete cancelled.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        print(f"Student ID {student_id} deleted.")
    except sqlite3.Error as e:
        print(f"Something went wrong deleting that student: {e}")


def display_menu():
    print("\n" + "=" * 40)
    print("STUDENT RECORD MANAGER")
    print("=" * 40)
    print("1. Add a new student")
    print("2. View all students")
    print("3. Update a student")
    print("4. Delete a student")
    print("5. Exit")


def main():
    conn = connect_db()
    if conn is None:
        print("Could not open the database. Exiting.")
        return

    create_table(conn)

    try:
        running = True
        while running:
            display_menu()
            choice = input("Choose an option (1-5): ").strip()

            if choice == "1":
                add_student(conn)
            elif choice == "2":
                view_students(conn)
            elif choice == "3":
                update_student(conn)
            elif choice == "4":
                delete_student(conn)
            elif choice == "5":
                running = False
            else:
                print("That's not a valid option - please choose 1 through 5.")
    finally:
        # runs whether the loop exited normally or an unexpected error
        # happened, so the connection never gets left open by accident
        conn.close()
        print("\nDatabase connection closed. Goodbye!")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------
# References
#
# Python Software Foundation. (2026). sqlite3 - DB-API 2.0 interface for
#   SQLite databases. Python 3 documentation.
#   https://docs.python.org/3/library/sqlite3.html
#
# SQLite Consortium. (2026). CREATE TABLE. SQLite documentation.
#   https://www.sqlite.org/lang_createtable.html
#
# SQLite Consortium. (2026). SQLite constraints (primary keys, NOT NULL,
#   and integrity errors). SQLite documentation.
#   https://www.sqlite.org/lang_createtable.html#constraints
#
# Python Software Foundation. (2026). Errors and exceptions. Python 3
#   tutorial. https://docs.python.org/3/tutorial/errors.html
#
# Van Rossum, G., Warsaw, B., & Coghlan, N. (2001). PEP 8 - Style guide
#   for Python code. Python Enhancement Proposals.
#   https://peps.python.org/pep-0008/
# ---------------------------------------------------------------------
