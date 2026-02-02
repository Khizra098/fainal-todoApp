#!/usr/bin/env python3
"""
Script to fix existing user records in the database that have invalid password hashes
"""

import sqlite3
import os
import sys
sys.path.append('.')

from src.auth.auth_handler import get_password_hash, verify_password

def fix_invalid_password_hashes():
    # Connect to the database
    db_path = 'todo_chatbot.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all users
        cursor.execute("SELECT id, email, password_hash FROM users")
        users = cursor.fetchall()

        for user_id, email, password_hash in users:
            # Try to verify a dummy password against the hash to see if it's valid
            try:
                # Just try to verify with a dummy password to see if the hash is valid
                verify_password("dummy", password_hash)
                print(f"User {email}: Password hash is valid")
            except Exception as e:
                print(f"User {email}: Invalid password hash detected: {str(e)}")

                # Reset the password hash to a default value or remove the user
                # For safety, let's update with a known good hash for a default password
                default_hash = get_password_hash("default123")  # Use the fixed function

                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (default_hash, user_id)
                )
                print(f"User {email}: Password hash reset to default")

        # Commit changes
        conn.commit()
        print("\nDatabase cleanup completed successfully!")

    except Exception as e:
        print(f"Error during database cleanup: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    fix_invalid_password_hashes()