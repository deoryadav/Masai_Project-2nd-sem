# Library Management System

A simple command-line Library Management System implemented in Python using CSV files as a lightweight database. It supports two user roles (Librarian and Member) and provides basic CRUD operations, due-date logic, overdue reporting, and password hashing for secure member authentication.

## Features

* **Librarian**

  * Add, Remove, Issue, and Return books
  * Register new members with bcrypt-hashed passwords
  * View overdue loans in a formatted table

* **Member**

  * Search book catalog by title or author
  * Borrow available books
  * View personal loan history (due dates and returned status)

* **Data Storage**

  * CSV-backed "mini-database" (`data/*.csv`)
  * `Book`, `Member`, and `Loan` dataclasses for in-memory models
  * `CSVStorage` for loading/saving CSVs with error handling

* **Authentication**

  * `AuthService` for `register_member` and `login` flows
  * Bcrypt password hashing

* **Overdue Report**

  * Tabulated console output via [tabulate](https://pypi.org/project/tabulate/)
  * Detects corrupt date ranges and warns before listing overdue items

* **Testing**

  * Pytest suite covers issue/return logic, invalid input, and overdue detection

## Getting Started

### Prerequisites

* Python 3.8+
* `pip` for dependency management

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/LibrarySystem.git
   cd LibrarySystem
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .\.venv\Scripts\activate   # Windows PowerShell
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI from the project root directory:

```bash
python -m library.main [--data-dir path/to/data]
```

* **Librarian role**: enter `librarian` and the default password `libpass`.
* **Member role**: enter `member`, then your Member ID and password.

Once logged in, follow the on-screen menus to perform operations.

## Running Tests

Execute the pytest suite:

```bash
pytest -q
```

## Project Structure

```
LibrarySystem/
├── data/                 # CSV files (books, members, loans)
├── library/              # Core application code
│   ├── auth.py           # Authentication service
│   ├── storage.py        # CSV load/save helpers
│   ├── models.py         # Data classes
│   └── main.py           # CLI entrypoint
├── tests/                # Pytest test cases
├── requirements.txt      # pip dependencies
└── README.md             # Project documentation
```

## Notes

* By default, the app uses the `data/` folder in the project root. Use `--data-dir` to override.
* All passwords are hashed with bcrypt for security.
* The Librarian password is hard-coded as `libpass` for demo purposes.

---

Made by Ramesh D Yadav
