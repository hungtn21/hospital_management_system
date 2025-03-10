# Hospital Management System

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Database Configuration](#database-configuration)

## Introduction

The Hospital Management System is a Python-based application that uses the Tkinter library for the user interface and PostgreSQL for database management. This system allows the management of user information, doctors, patients, and medical consultations.

## System Requirements

- Python 3.x
- `tkinter` library
- `psycopg2` library
- PostgreSQL

## Installation

1. **Clone the repository**

2. **Install the required libraries**:

   ```bash
   pip install psycopg2-binary
   ```

3. **Set up the database**:
   - Ensure PostgreSQL is installed and running.
   - Create a new database in PostgreSQL.
   - Run the SQL script to create the necessary tables:
     ```bash
     psql -U yourusername -d yourdatabase -f query.sql
     ```

## Database Configuration

Before running the application, you need to configure the database connection settings in the `main.py` file.

Open `main.py` and update the following section with your PostgreSQL connection details:

```python
connection = psycopg2.connect(
    host="your_host",
    database="your_database",
    user="your_username",
    password="your_password"
)
```

And now run `main.py` to experience.
