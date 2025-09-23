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

# Enforce foreign keys in SQLite
cursor.execute("PRAGMA foreign_keys = ON;")

# --- Table Creation (Movies Domain, Normalized) ---

# Movies master table
cursor.execute(
    """
CREATE TABLE MOVIES (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TITLE TEXT NOT NULL,
    RELEASE_YEAR INTEGER NOT NULL,
    GENRE TEXT NOT NULL,
    RUNTIME_MINUTES INTEGER NOT NULL,
    RATING REAL
);
"""
)
print("Created 'MOVIES' table.")

# Actors master table
cursor.execute(
    """
CREATE TABLE ACTORS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    BIRTH_YEAR INTEGER,
    NATIONALITY TEXT
);
"""
)
print("Created 'ACTORS' table.")

# Many-to-many join table between movies and actors
cursor.execute(
    """
CREATE TABLE MOVIE_ACTORS (
    MOVIE_ID INTEGER NOT NULL,
    ACTOR_ID INTEGER NOT NULL,
    ROLE TEXT,
    PRIMARY KEY (MOVIE_ID, ACTOR_ID),
    FOREIGN KEY (MOVIE_ID) REFERENCES MOVIES(ID) ON DELETE CASCADE,
    FOREIGN KEY (ACTOR_ID) REFERENCES ACTORS(ID) ON DELETE CASCADE
);
"""
)
print("Created 'MOVIE_ACTORS' table.")

# Revenues table, one row per movie
cursor.execute(
    """
CREATE TABLE REVENUES (
    MOVIE_ID INTEGER PRIMARY KEY,
    BUDGET REAL NOT NULL,
    BOX_OFFICE_DOMESTIC REAL NOT NULL,
    BOX_OFFICE_INTERNATIONAL REAL NOT NULL,
    OPENING_WEEKEND REAL,
    FOREIGN KEY (MOVIE_ID) REFERENCES MOVIES(ID) ON DELETE CASCADE
);
"""
)
print("Created 'REVENUES' table.")

# --- Data Generation ---

genres = [
    'Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance',
    'Thriller', 'Animation', 'Fantasy'
]
nationalities = [
    'American', 'British', 'Canadian', 'Australian', 'Indian', 'French',
    'German', 'Japanese', 'Korean', 'Spanish'
]

num_movies = 60
num_actors = 200

print(f"Generating {num_movies} movies and {num_actors} actors with relations and revenues...")

# Insert actors
actor_ids = []
for _ in range(num_actors):
    actor_name = fake.name()
    birth_year = random.randint(1950, 2005)
    nationality = random.choice(nationalities)
    cursor.execute(
        """
        INSERT INTO ACTORS (NAME, BIRTH_YEAR, NATIONALITY)
        VALUES (?, ?, ?)
        """,
        (actor_name, birth_year, nationality),
    )
    actor_ids.append(cursor.lastrowid)

# Insert movies and revenues
movie_ids = []
for _ in range(num_movies):
    title = f"{fake.color_name()} {fake.word().title()}"
    release_year = random.randint(1980, 2025)
    genre = random.choice(genres)
    runtime = random.randint(80, 180)
    rating = round(random.uniform(4.0, 9.8), 1)

    cursor.execute(
        """
        INSERT INTO MOVIES (TITLE, RELEASE_YEAR, GENRE, RUNTIME_MINUTES, RATING)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, release_year, genre, runtime, rating),
    )
    movie_id = cursor.lastrowid
    movie_ids.append(movie_id)

    # Assign 2-6 random actors to each movie
    num_cast = random.randint(2, 6)
    cast_actor_ids = random.sample(actor_ids, k=num_cast)
    for aid in cast_actor_ids:
        role = random.choice(['Lead', 'Supporting', 'Cameo'])
        cursor.execute(
            """
            INSERT INTO MOVIE_ACTORS (MOVIE_ID, ACTOR_ID, ROLE)
            VALUES (?, ?, ?)
            """,
            (movie_id, aid, role),
        )

    # Create plausible revenue numbers
    budget = round(random.uniform(5_000_000, 200_000_000), 0)
    opening_weekend = round(random.uniform(0.05, 0.5) * budget, 0)
    domestic = round(random.uniform(0.5, 3.0) * budget, 0)
    international = round(random.uniform(0.5, 3.5) * budget, 0)

    cursor.execute(
        """
        INSERT INTO REVENUES (MOVIE_ID, BUDGET, BOX_OFFICE_DOMESTIC, BOX_OFFICE_INTERNATIONAL, OPENING_WEEKEND)
        VALUES (?, ?, ?, ?, ?)
        """,
        (movie_id, budget, domestic, international, opening_weekend),
    )

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"\n\033[92mSuccessfully created and populated the '{db_path}' database with MOVIES/ACTORS schema.\033[0m")
print("You can now run the main application.")
