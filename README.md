# Library Management System - SPPU DBMS Mini Project

This is a simple, functional web-based Library Management System created using Python (Flask) as the backend framework. It is designed to fulfill the requirements for the Savitribai Phule Pune University (SPPU) – Database Management Systems Laboratory (TE Computer 2019 course).

The primary focus is on demonstrating database connectivity, CRUD operations, and the integration of both SQL (MySQL) and NoSQL (MongoDB) databases. The user interface is intentionally kept minimal.

## Technical Stack

-   **Frontend:** HTML with minimal inline CSS
-   **Backend:** Python (Flask)
-   **Databases:**
    1.  **MySQL:** Stores structured data (students, books, issues, fines).
    2.  **MongoDB:** Stores logs and audit information for book updates/deletions.

## Features

-   **Home Page:** Basic project info and navigation.
-   **Add New Book:** A simple form to add new books.
-   **View All Books:** Displays all book records from MySQL with options to edit or delete.
-   **Issue/Return Books:** Forms to manage book borrowing and returns.
-   **Fine Calculation:** Automatically calculates and records fines for late returns (₹5/day after 15 days).
-   **MongoDB Audit Trail:** Every time a book record is updated or deleted from MySQL, the old record is saved in a MongoDB collection named `book_audit`.

## How to Set Up and Run the Project

### 1. Prerequisites

-   Python 3.x
-   MySQL Server
-   MongoDB Server

### 2. Installation

Clone the repository and install the required Python packages using pip:

```bash
pip install flask mysql-connector-python pymongo
```

### 3. Database Setup

**a) MySQL:**

1.  Make sure your MySQL server is running.
2.  You need to create a database named `library` and a user with privileges to access it. The application is configured to use the following credentials by default (you can change these in `db_mysql.py`):
    -   **Host:** `localhost`
    -   **Database:** `library`
    -   **User:** `user`
    -   **Password:** `password`
3.  Create the required tables by executing the `schema.sql` file. You can do this using a MySQL client:
    ```bash
    mysql -u user -p library < schema.sql
    ```

**b) MongoDB:**

1.  Make sure your MongoDB server is running on its default port (`27017`).
2.  No special setup is required. The application will automatically create the `library` database and the `book_audit` collection when the first audit record is created.

### 4. Run the Application

Once the setup is complete, you can run the Flask application with the following command:

```bash
python app.py
```

The application will be accessible at `http://localhost:5000` in your web browser.
