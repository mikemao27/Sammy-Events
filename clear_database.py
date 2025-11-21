import sqlite3
import os

DATABASE_PATH = "database/events.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()
cursor.execute("DELETE FROM events;")
connection.commit()
connection.close()