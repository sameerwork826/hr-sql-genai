import sqlite3
from faker import Faker
import random
import os

# Initialize Faker
fake = Faker()

# Database file name
db_path = 'employee_kpi.db'

# Check if the database file already exists and remove it to start fresh
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database file '{db_path}'.")

# Connect to SQLite database (creates a new file)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# --- Table Creation ---
# Create the EMPLOYEE table with a schema that is useful for HR analysis
cursor.execute("""
CREATE TABLE EMPLOYEE (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    AGE INTEGER NOT NULL,
    DEPARTMENT TEXT NOT NULL,
    SALARY REAL NOT NULL,
    PERFORMANCE_SCORE REAL NOT NULL,
    YEARS_OF_EXPERIENCE INTEGER NOT NULL,
    LAST_PROMOTION_YEAR INTEGER,
    LOCATION TEXT NOT NULL
);
""")
print("Created 'EMPLOYEE' table.")

# --- Data Generation ---
departments = ['IT', 'HR', 'Sales', 'Marketing', 'Finance', 'Engineering']
locations = ['New York', 'London', 'Tokyo', 'San Francisco', 'Singapore', 'Berlin']

print("Generating and inserting 100 fake employee records...")

# Generate and insert 100 fake employee records
for i in range(100):
    name = fake.name()
    age = random.randint(22, 60)
    department = random.choice(departments)
    salary = round(random.uniform(45000, 160000), 2)
    performance_score = round(random.uniform(1.0, 5.0), 1)
    years_of_experience = random.randint(1, age - 21)
    # Employees with less than 2 years of experience might not have a promotion
    if years_of_experience < 2:
        last_promotion_year = None
    else:
        last_promotion_year = random.randint(2018, 2024)
    location = random.choice(locations)
    
    cursor.execute("""
    INSERT INTO EMPLOYEE (NAME, AGE, DEPARTMENT, SALARY, PERFORMANCE_SCORE, YEARS_OF_EXPERIENCE, LAST_PROMOTION_YEAR, LOCATION)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, department, salary, performance_score, years_of_experience, last_promotion_year, location))

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"\n\033[92mSuccessfully created and populated the '{db_path}' database with 100 sample records.\033[0m")
print("You can now run the main application.")
