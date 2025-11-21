import sqlite3
import os
from ingest import get_organization_id
import bcrypt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "events.db")

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def create_organization(title, description, academic_fields):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO organizations (title, organization_description) VALUES (?, ?)
        """,
        (title, description)
    )

    organization_id = get_organization_id(title)

    for academic_field in academic_fields:
        cursor.execute(
            """
            INSERT OR IGNORE INTO organization_academic_fields (organization_id, academic_fields) VALUES (?, ?)
            """,
            (organization_id, academic_field)
        )
    
    connection.commit()
    connection.close()

def create_event(title, description, start_time, end_time, location, free_food, organization_name):
    organization_id = get_organization_id(organization_name)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO events (title, event_description, start_time, end_time, event_location, free_food, organization_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (title, description, start_time, end_time, location, free_food, organization_id)
    )

    connection.commit()
    connection.close()

def hash_password(password: str) -> str:
    password_bytes = password.encode("UTF-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return hashed.decode("UTF-8")

def email_exists(email: str) -> bool:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,))
    database_row = cursor.fetchone()

    connection.close()

    return database_row is not None

def netID_exists(netID: str) -> bool:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT 1 FROM users WHERE netID = ? LIMIT 1", (netID,))
    database_row = cursor.fetchone()

    connection.close()

    return database_row is not None

def sign_up(first_name, last_name, netID, email, password, phone_number, degree_ids = None):
    if netID_exists(netID):
        return False, "There Is Already A User With This NetID"

    if email_exists(email):
        return False, "There Is Already A User With This Email"

    connection = get_connection()
    cursor = connection.cursor()

    encrypted_password = hash_password(password)

    cursor.execute(
        """
        INSERT INTO users (first_name, last_name, netID, email, user_password, phone_number)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (first_name, last_name, netID, email, encrypted_password, phone_number),
    )

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    if degree_ids:
        degree_ids = [int(degree) for degree in degree_ids if str(degree).isdigit()]
        set_user_degrees(user_id, degree_ids)

    return True, "Account Created Successfully."

def fetch_expected_password(email: str) -> str | None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_password FROM users WHERE email = ?", (email,)
    )

    expected_password = cursor.fetchone()
    connection.close()
    
    if expected_password is None:
        return None
    return expected_password[0]

def verify_password(password: str, encrypted_password: str | None) -> bool:
    if encrypted_password is None:
        return False

    return bcrypt.checkpw(
        password.encode("utf-8"), encrypted_password.encode("utf-8")
    )

# Once the user has logged in, make sure to keep track of a pointer towards the specific user.
# This way, it is easy to keep track of who is logged in and fetch the user_id easier.
def fetch_user_id(email):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    )

    user_id = cursor.fetchone()
    connection.close()
    
    if user_id is None:
        return None
    return user_id[0]

def sign_in(email: str, password: str):
    expected_password = fetch_expected_password(email)

    if expected_password is None:
        return False, None

    if verify_password(password, expected_password):
        user_id = fetch_user_id(email)
        return True, user_id
    
    return False, None

def follow_organization(user_id, organization_name):
    connection = get_connection()
    cursor = connection.cursor()

    organization_id = get_organization_id(organization_name)

    cursor.execute(
        """
        INSERT OR IGNORE INTO organization_interests (user_id, organization_id) VALUES (?, ?)
        """,
        (user_id, organization_id)
    )

    connection.commit()
    connection.close()

def unfollow_organization(user_id, organization_name):
    connection = get_connection()
    cursor = connection.cursor()

    organization_id = get_organization_id(organization_name)

    cursor.execute(
        """
        DELETE FROM organization_interests WHERE user_id = ? AND organization_id = ?
        """,
        (user_id, organization_id),
    )
    
    connection.commit()
    connection.close()

def get_followed_organizations(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT organization.id, organization.title, organization.organization_description
        FROM organizations organization
        JOIN organization_interests organization_interest
            ON organization.id = organization_interest.organization_id
        WHERE organization_interest.user_id = ?
        ORDER BY organization.title ASC
        """,
        (user_id,),
    )

    rows = [dict[row] for row in cursor.fetchall()]
    connection.close()
    return rows

def get_academic_fields():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, degree_name FROM academic_fields ORDER BY degree_name")
    rows = cursor.fetchall()
    connection.close()

    return [{"id": row[0], "name": row[1]} for row in rows]

def set_user_degrees(user_id: int, degree_ids: list[int]):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM user_academic_fields WHERE user_id = ?", (user_id,))

    for degree_id in degree_ids:
        cursor.execute(
            "INSERT OR IGNORE INTO user_academic_fields (user_id, academic_field_id) VALUES (?, ?)",
            (user_id, degree_id),
        )
    
    connection.commit()
    connection.close()

def get_user_degrees(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        """
        SELECT academic_field.id, academic_field.degree_name
        FROM academic_fields academic_field
        JOIN user_academic_fields user_academic_field 
            ON academic_field.id = user_academic_field.academic_field_id
        WHERE user_academic_field.user_id = ?
        ORDER BY academic_field.degree_name
        """,
        (user_id,),
    )

    rows = cursor.fetchall()
    connection.close()
    return [{"id": row[0], "name": row[1]} for row in rows]