import sqlite3

DATABASE_PATH = "database/events.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

with open("database/schema.sql") as file:
    cursor.executescript(file.read())

connection.commit()
connection.close()

print("Databases Initialized!")