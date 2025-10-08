-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS library;

-- Use the library database
USE library;

-- Table structure for STUDENT
CREATE TABLE IF NOT EXISTS STUDENT (
    Stud_ID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Dept VARCHAR(255),
    Year INT
);

-- Table structure for BOOK
CREATE TABLE IF NOT EXISTS BOOK (
    Book_ID INT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Author VARCHAR(255),
    Publisher VARCHAR(255),
    Status VARCHAR(50) DEFAULT 'Available'
);

-- Table structure for ISSUE
CREATE TABLE IF NOT EXISTS ISSUE (
    Issue_ID INT PRIMARY KEY AUTO_INCREMENT,
    Stud_ID INT,
    Book_ID INT,
    IssueDate DATE NOT NULL,
    ReturnDate DATE,
    FOREIGN KEY (Stud_ID) REFERENCES STUDENT(Stud_ID),
    FOREIGN KEY (Book_ID) REFERENCES BOOK(Book_ID)
);

-- Table structure for FINE
CREATE TABLE IF NOT EXISTS FINE (
    Fine_ID INT PRIMARY KEY AUTO_INCREMENT,
    Stud_ID INT,
    Amount INT NOT NULL,
    FineDate DATE NOT NULL,
    FOREIGN KEY (Stud_ID) REFERENCES STUDENT(Stud_ID)
);
