import sqlite3
import os

DATABASE_PATH = "database/events.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def clear_user_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM organization_interests;")

    cursor.execute("DELETE FROM users;")

    connection.commit()
    connection.close()

    print("User Data Cleared!")

if __name__ == "__main__":
    clear_user_data()