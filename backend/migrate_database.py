#!/usr/bin/env python3
"""
Migration script to add missing columns to the SQLite database
"""

import sqlite3
import os

# Connect to the database
db_path = 'todo_chatbot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if theme column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add theme column if it doesn't exist
    if 'theme' not in columns:
        print("Adding 'theme' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT 'light'")
        print("Added 'theme' column")
    else:
        print("'theme' column already exists")

    # Add language column if it doesn't exist
    if 'language' not in columns:
        print("Adding 'language' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
        print("Added 'language' column")
    else:
        print("'language' column already exists")

    # Commit the changes
    conn.commit()
    print("\nDatabase migration completed successfully!")

except Exception as e:
    print(f"Error during migration: {e}")
    conn.rollback()

finally:
    conn.close()