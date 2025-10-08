# app.py

from flask import Flask, render_template, request, redirect, url_for
import db_mysql
import db_mongo
from datetime import datetime, timedelta
import mysql.connector # To handle potential errors

# Initialize Flask app
app = Flask(__name__)

# --- Database Connections ---
# Establish connection to MySQL
# This is called once when the app starts.
mysql_conn = db_mysql.create_connection()

# Establish connection to MongoDB
# This is called once when the app starts.
mongo_client = db_mongo.create_connection()
if mongo_client:
    db = mongo_client['library']
    book_audit_collection = db['book_audit']
else:
    # Handle the case where MongoDB connection failed
    db = None
    book_audit_collection = None


# --- Route Definitions ---

# Home Page
@app.route('/')
def index():
    """ Renders the home page with navigation. """
    return render_template('index.html')

# Add New Book
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    """ Handles adding a new book to the MySQL database. """
    if request.method == 'POST':
        book_id = request.form['book_id']
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        status = 'Available'  # New books are available by default

        if mysql_conn and mysql_conn.is_connected():
            cursor = mysql_conn.cursor()
            try:
                cursor.execute("INSERT INTO BOOK (Book_ID, Title, Author, Publisher, Status) VALUES (%s, %s, %s, %s, %s)",
                               (book_id, title, author, publisher, status))
                mysql_conn.commit()
            except mysql.connector.Error as err:
                print(f"Error adding book: {err}")
            finally:
                cursor.close()
        return redirect(url_for('view_books'))
    return render_template('add_book.html')

# View All Books
@app.route('/view')
def view_books():
    """ Displays all book records from the MySQL database. """
    books = []
    if mysql_conn and mysql_conn.is_connected():
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM BOOK")
        books = cursor.fetchall()
        cursor.close()
    return render_template('view_books.html', books=books)

# --- Student Management ---

# Add New Student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """ Handles adding a new student to the MySQL database. """
    if request.method == 'POST':
        stud_id = request.form['stud_id']
        name = request.form['name']
        dept = request.form['dept']
        year = request.form['year']

        if mysql_conn and mysql_conn.is_connected():
            cursor = mysql_conn.cursor()
            try:
                cursor.execute("INSERT INTO STUDENT (Stud_ID, Name, Dept, Year) VALUES (%s, %s, %s, %s)",
                               (stud_id, name, dept, year))
                mysql_conn.commit()
            except mysql.connector.Error as err:
                print(f"Error adding student: {err}")
            finally:
                cursor.close()
        return redirect(url_for('view_students'))
    return render_template('add_student.html')

# View All Students
@app.route('/view_students')
def view_students():
    """ Displays all student records from the MySQL database. """
    students = []
    if mysql_conn and mysql_conn.is_connected():
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM STUDENT")
        students = cursor.fetchall()
        cursor.close()
    return render_template('view_students.html', students=students)


# --- Book Issuing and Returning ---

# Issue a Book
@app.route('/issue', methods=['GET', 'POST'])
def issue_book():
    """ Handles issuing a book to a student. """
    if request.method == 'POST':
        book_id = request.form['book_id']
        stud_id = request.form['stud_id']
        issue_date = datetime.now().date()

        if mysql_conn and mysql_conn.is_connected():
            cursor = mysql_conn.cursor()
            try:
                # Check if book is available and update its status
                cursor.execute("UPDATE BOOK SET Status = 'Issued' WHERE Book_ID = %s AND Status = 'Available'", (book_id,))
                if cursor.rowcount > 0:  # Check if the update was successful
                    # Insert the new issue record
                    cursor.execute("INSERT INTO ISSUE (Book_ID, Stud_ID, IssueDate) VALUES (%s, %s, %s)",
                                   (book_id, stud_id, issue_date))
                    mysql_conn.commit()
                else:
                    print("Book is not available for issue or does not exist.")
            except mysql.connector.Error as err:
                print(f"Error issuing book: {err}")
                mysql_conn.rollback()
            finally:
                cursor.close()
        return redirect(url_for('view_books'))

    # For GET request, populate dropdowns with available books and students
    available_books = []
    students = []
    if mysql_conn and mysql_conn.is_connected():
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT Book_ID, Title FROM BOOK WHERE Status = 'Available'")
        available_books = cursor.fetchall()
        cursor.execute("SELECT Stud_ID, Name FROM STUDENT")
        students = cursor.fetchall()
        cursor.close()
    return render_template('issue_book.html', books=available_books, students=students)

# Return a Book
@app.route('/return', methods=['GET', 'POST'])
def return_book():
    """ Handles returning a book and calculating fines if applicable. """
    if request.method == 'POST':
        book_id = request.form['book_id']
        return_date = datetime.now().date()

        if mysql_conn and mysql_conn.is_connected():
            cursor = mysql_conn.cursor(dictionary=True)
            try:
                # Find the latest issue record for this book that has not been returned
                cursor.execute("SELECT Issue_ID, Stud_ID, IssueDate FROM ISSUE WHERE Book_ID = %s AND ReturnDate IS NULL ORDER BY IssueDate DESC LIMIT 1", (book_id,))
                issue = cursor.fetchone()

                if issue:
                    # Update return date in ISSUE table
                    cursor.execute("UPDATE ISSUE SET ReturnDate = %s WHERE Issue_ID = %s", (return_date, issue['Issue_ID']))

                    # Update book status to 'Available'
                    cursor.execute("UPDATE BOOK SET Status = 'Available' WHERE Book_ID = %s", (book_id,))

                    # Calculate and record fine if the book is late
                    issue_date = issue['IssueDate']
                    days_issued = (return_date - issue_date).days
                    if days_issued > 15:
                        fine_amount = (days_issued - 15) * 5
                        cursor.execute("INSERT INTO FINE (Stud_ID, Amount, FineDate) VALUES (%s, %s, %s)",
                                       (issue['Stud_ID'], fine_amount, return_date))
                    mysql_conn.commit()
                else:
                    print(f"No active issue record found for Book ID: {book_id}")
            except mysql.connector.Error as err:
                print(f"Error returning book: {err}")
                mysql_conn.rollback()
            finally:
                cursor.close()
        return redirect(url_for('view_books'))

    # For GET request, populate dropdown with issued books
    issued_books = []
    if mysql_conn and mysql_conn.is_connected():
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT Book_ID, Title FROM BOOK WHERE Status = 'Issued'")
        issued_books = cursor.fetchall()
        cursor.close()
    return render_template('return_book.html', books=issued_books)

# View Fine Records
@app.route('/fines')
def fine_records():
    """ Displays all fine records from the MySQL database. """
    fines = []
    if mysql_conn and mysql_conn.is_connected():
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT f.Fine_ID, s.Name, f.Amount, f.FineDate FROM FINE f JOIN STUDENT s ON f.Stud_ID = s.Stud_ID")
        fines = cursor.fetchall()
        cursor.close()
    return render_template('fines.html', fines=fines)

# MongoDB Audit Log for Books
@app.route('/audit')
def audit_log():
    """ Displays the book audit log from the MongoDB collection. """
    records = []
    if book_audit_collection:
        # Sort by timestamp descending to show newest first
        audit_records = book_audit_collection.find().sort('audit_timestamp', -1)
        records = list(audit_records)
    return render_template('audit.html', records=records)

# --- Routes for demonstrating MongoDB audit trail ---

# Edit a Book (triggers 'update' audit)
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    """ Handles editing a book's details and logs the old record to MongoDB before updating. """
    if not (mysql_conn and mysql_conn.is_connected()):
        return "Database connection not available.", 500

    cursor = mysql_conn.cursor(dictionary=True)
    if request.method == 'POST':
        # Get old record for auditing
        cursor.execute("SELECT * FROM BOOK WHERE Book_ID = %s", (book_id,))
        old_book_data = cursor.fetchone()

        # Log to MongoDB before updating
        if old_book_data and book_audit_collection:
            log_entry = old_book_data.copy()
            log_entry['audit_timestamp'] = datetime.utcnow()
            log_entry['operation'] = 'update'
            book_audit_collection.insert_one(log_entry)

        # Get new data from form and update MySQL
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        cursor.execute("UPDATE BOOK SET Title = %s, Author = %s, Publisher = %s WHERE Book_ID = %s",
                       (title, author, publisher, book_id))
        mysql_conn.commit()
        cursor.close()
        return redirect(url_for('view_books'))

    # For GET request, fetch book details to populate the form
    cursor.execute("SELECT * FROM BOOK WHERE Book_ID = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    if book:
        return render_template('edit_book.html', book=book)
    return "Book not found.", 404

# Delete a Book (triggers 'delete' audit)
@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    """ Handles deleting a book and logs the deleted record to MongoDB. """
    if not (mysql_conn and mysql_conn.is_connected()):
        return "Database connection not available.", 500

    cursor = mysql_conn.cursor(dictionary=True)
    try:
        # Get record for auditing before deleting
        cursor.execute("SELECT * FROM BOOK WHERE Book_ID = %s", (book_id,))
        book_to_delete = cursor.fetchone()

        if book_to_delete:
            # Log to MongoDB before deleting
            if book_audit_collection:
                log_entry = book_to_delete.copy()
                log_entry['audit_timestamp'] = datetime.utcnow()
                log_entry['operation'] = 'delete'
                book_audit_collection.insert_one(log_entry)

            # Delete from related tables first to avoid foreign key constraints
            cursor.execute("DELETE FROM ISSUE WHERE Book_ID = %s", (book_id,))
            cursor.execute("DELETE FROM BOOK WHERE Book_ID = %s", (book_id,))
            mysql_conn.commit()
    except mysql.connector.Error as err:
        print(f"Error deleting book: {err}")
        mysql_conn.rollback()
    finally:
        cursor.close()
    return redirect(url_for('view_books'))


# --- Main Execution ---
if __name__ == '__main__':
    # The host='0.0.0.0' makes the server accessible from your network
    app.run(host='0.0.0.0', port=5000, debug=True)
