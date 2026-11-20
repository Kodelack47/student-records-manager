# Student Records Manager

A menu-driven command-line program for managing student records in a **SQLite** database, written in **Python**.

## Features

- **Add, view, update, and delete** students (full CRUD)
- **Input validation:** student IDs must be numbers, and emails must contain an `@`
- **Error handling** around everything that can fail: duplicate IDs, missing records, and database errors
- Asks for confirmation before deleting a record
- Small single-purpose functions (`connect_db`, `create_table`, `add_student`, …) so each database operation is easy to read and test on its own

## Run it

```bash
python3 student_db.py
```

It uses only the Python standard library (`sqlite3`). The database file `students.db` is created the first time you run it.

```
1. Add a new student
2. View all students
3. Update a student
4. Delete a student
5. Exit
```

## Author

**Ousmana Tunkara** · [GitHub @Kodelack47](https://github.com/Kodelack47)
