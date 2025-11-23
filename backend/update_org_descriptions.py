import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "events.db")
DESCRIPTIONS_PATH = os.path.join(BASE_DIR, "database", "descriptions")

def load_descriptions(organization_id: int) -> str | None:
    filename = f"description{organization_id}.txt"
    path = os.path.join(DESCRIPTIONS_PATH, filename)
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding = "utf-8") as file:
        text = file.read()

    cleaned = " ".join(text.split())
    return cleaned

def main():
    if not os.path.exists(DATABASE_PATH):
        raise SystemExit(f"Database Not Found at {DATABASE_PATH}")
    
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT id, title FROM organizations")
    organizations = cursor.fetchall()

    updated = 0
    missing = 0

    for organization_id, title in organizations:
        description = load_descriptions(organization_id)

        if description is None:
            print(f"No Description File for Organization {organization_id} ({title})")
            missing += 1
            continue

        cursor.execute(
            "UPDATE organizations SET organization_description = ? WHERE id = ?",
            (description, organization_id)
        )

        updated += 1
        print(f"Updated Organization {organization_id} ({title} with Description from File)")

    connection.commit()
    connection.close()
    print(f"Done. Updated {updated} Organizations, {missing} Had no Description File")

if __name__ == "__main__":
    main()