import sqlite3
import os
from flask import Flask, jsonify, request, session, render_template, send_from_directory
from db_operations import (
    get_academic_fields, 
    get_user_degrees, 
    set_user_degrees, 
    verify_password,
    create_event,
    create_organization,
)

app = Flask(__name__, static_folder = "../frontend", template_folder = "../frontend/display")

@app.route("/")
def index():
    return send_from_directory("../frontend/display", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("../frontend/display", path)

from db_operations import (
    sign_up, sign_in,
    follow_organization, unfollow_organization, get_followed_organizations,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "events.db")

app = Flask(
    __name__,
    static_folder = "../frontend/static",
    static_url_path = "/static",
    template_folder = "../frontend/display"
)

app.secret_key = "cd4e3be0753bcf403d7a260497d28f0e"

def get_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

@app.route("/api/signup", methods = ["POST"])
def api_signup():
    data = request.get_json() or {}
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    netId = data.get("netID")
    email = data.get("email")
    password = data.get("password")
    phone_number = data.get("phone_number")
    degree_ids = data.get("degree_ids", [])

    ok, msg = sign_up(first_name, last_name, netId, email, password, phone_number, degree_ids)

    if not ok:
        return jsonify({"ok": False, "error": msg}), 400
    
    return jsonify({"ok": True, "message": msg})

@app.route("/api/login", methods = ["POST"])
def api_login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    connection = get_database()
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    connection.close()

    if not row or not verify_password(password, row["user_password"]):
        return jsonify({"ok": False, "error": "Invalid Email or Password"}), 401
    
    session["user_id"] = row["id"]
    return jsonify({"ok": True})

@app.route("/api/logout", methods = ["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/user")
def api_user():
    user_id = session.get("user_id")
    email = session.get("email")

    if not user_id:
        return jsonify({"authenticated": False})
    
    connection = get_database()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, first_name, last_name, email, netID, phone_number FROM users WHERE id = ?",
        (user_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if not row:
        session.clear()
        return jsonify({"authenticated": False})
    
    return jsonify({"authenticated": True, "user": dict(row),})

@app.route("/api/events")
def api_events():
    connection = get_database()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    user_id = session.get("user_id")
    user_id_param = user_id if user_id is not None else -1

    field_id = request.args.get("field_id", type = int)
    free_food_only = request.args.get("free_food") == "1"

    params = [user_id_param]
    conditions = []

    if field_id is not None:
        conditions.append("academic_fields.id = ?")
        params.append(field_id)

    if free_food_only:
        conditions.append("events.free_food = 1")

    conditions.append("(events.start_time IS NULL OR events.start_time >= datetime('now'))")

    base_query = ""
    if conditions:
        base_query = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT
            events.id,
            events.title,
            events.event_description,
            events.source_url,
            events.start_time,
            events.end_time,
            events.event_location,
            events.source,
            events.free_food,
            organizations.title AS organization_name,
            GROUP_CONCAT(academic_fields.degree_name, ', ') AS academic_fields,
            CASE WHEN 
                organization_interests.user_id IS NULL THEN 0 
                ELSE 1 
            END AS followed
        FROM events
        LEFT JOIN organizations
            ON events.organization_id = organizations.id
        LEFT JOIN organization_academic_fields
            ON organizations.id = organization_academic_fields.organization_id
        LEFT JOIN academic_fields
            ON organization_academic_fields.academic_field_id = academic_fields.id
        LEFT JOIN organization_interests
            ON organization_interests.organization_id = organizations.id
            AND organization_interests.user_id = ?
        {base_query}
        GROUP BY events.id
        ORDER BY events.start_time IS NUll, events.start_time;
    """

    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return jsonify(rows)


@app.route("/api/events/followed")
def api_events_followed():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 401
    
    connection = get_database()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            event.id,
            event.title,
            event.event_description,
            event.start_time,
            event.end_time,
            event.event_location,
            event.source,
            event.source_url,
            organization.title AS organization_name
        FROM events event
        JOIN organizations organization
            ON event.organization_id = organization.id
        JOIN organization_interests organization_interest
            ON organization_interest.organization_id = organization.id
            AND organization_interest.user_id = ?
        WHERE (event.start_time IS NULL OR event.start_time >= datetime('now'))
        ORDER BY event.start_time IS NULL, event.start_time ASC
        LIMIT 5
        """,
        (user_id,),
    )

    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return jsonify({"authenticated": True, "events": rows})

@app.route("/api/organizations")
def api_organizations():
    connection = get_database()
    cursor = connection.cursor()

    user_id = session.get("user_id")
    user_id_param = user_id if user_id is not None else -1

    field_filter = request.args.get("field")

    params = [user_id_param]
    conditions = []

    base_query = """
        SELECT
            organization.id,
            organization.title,
            organization.organization_description,
            GROUP_CONCAT(academic_field.degree_name, ', ') AS academic_fields,
            CASE WHEN 
                organization_interest.user_id IS NULL THEN 0 
                ELSE 1 
            END AS followed
        FROM organizations AS organization
        LEFT JOIN organization_academic_fields AS organization_academic_field
            ON organization.id = organization_academic_field.organization_id
        LEFT JOIN academic_fields AS academic_field
            ON organization_academic_field.academic_field_id = academic_field.id
        LEFT JOIN organization_interests AS organization_interest
            ON organization_interest.organization_id = organization.id
            AND organization_interest.user_id = ?
    """
    if field_filter:
        conditions.append("academic_field.degree_name = ?")
        params.append(field_filter)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += """
        GROUP BY organization.id
        ORDER BY followed DESC, organization.title ASC
    """

    cursor.execute(base_query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return jsonify(rows)

@app.route("/api/organizations/follow", methods = ["POST"])
def api_follow_organization():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Not Authenticated"}), 401
    
    data = request.get_json() or {}
    organization_name = data.get("organization_name")

    if not organization_name:
        return jsonify({"ok": False, "error": "Organization Name Required"}), 400
    
    try:
        follow_organization(user_id, organization_name)
        return jsonify({"ok": True})
    except Exception as exception:
        return jsonify({"ok": False, "error": "Failed to Follow Organization"})

@app.route("/api/organizations/unfollow", methods = ["POST"])
def api_unfollow_organization():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Not Authenticated"}), 401
    
    data = request.get_json() or {}
    organization_name = data.get("organization_name")

    if not organization_name:
        return jsonify({"ok": False, "error": "Organization Name Required"}), 400
    
    try:
        unfollow_organization(user_id, organization_name)
        return jsonify({"ok": True})
    except Exception as exception:
        return jsonify({"ok": False, "error": "Failed to Unfollow Organization"})

@app.route("/api/organizations/followed")
def api_followed_organizations():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not Authenticated"}), 401
    
    connection = get_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            organization.id,
            organization.title,
            organization.organization_description
        FROM organizations AS organization
        JOIN organization_interests AS organization_interest
            ON organization_interest.organization_id = organization.id
        WHERE organization_interest.user_id = ?
        ORDER BY organization.title ASC
    """, (user_id,))

    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return jsonify({"organizations": rows})

@app.route("/api/academic-fields")
def api_academic_fields():
    fields = get_academic_fields()
    return jsonify(fields)

@app.route("/api/user/degrees", methods = ["GET", "POST"])
def api_user_degrees():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"authenticated": False}), 401
    
    if request.method == "GET":
        return jsonify({"authenticated": True, "degrees": get_user_degrees(user_id)})
    
    data = request.get_json() or {}
    degree_ids = data.get("degree_ids", [])

    degree_ids = [int(degree) for degree in degree_ids if str(degree).isdigit()]
    set_user_degrees(user_id, degree_ids)
    return jsonify({"ok": True})

@app.route("/api/organizations/create", methods=["POST"])
def api_create_organization():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Authentication Eequired"}), 401

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    academic_field_ids = data.get("academic_field_ids") or []

    if not title:
        return jsonify({"ok": False, "error": "Organization Name is Required"}), 400

    academic_field_ids = [
        int(x) for x in academic_field_ids if str(x).isdigit()
    ]

    create_organization(title, description, academic_field_ids)
    return jsonify({"ok": True})

@app.route("/api/events/create", methods=["POST"])
def api_create_event():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Authentication Required"}), 401

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    start_time = (data.get("start_time") or "").strip() or None
    end_time = (data.get("end_time") or "").strip() or None
    location = (data.get("location") or "").strip()
    org_name = (data.get("organization_name") or "").strip()
    free_food = bool(data.get("free_food"))

    if not title:
        return jsonify({"ok": False, "error": "Event Name is Required"}), 400

    # Uses existing helper in db_operations.py
    create_event(
        title,
        description,
        start_time,
        end_time,
        location,
        1 if free_food else 0,
        org_name,
    )
    return jsonify({"ok": True})


@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/index.html")
def index_html_redirect():
    return render_template("index.html")

@app.route("/events.html")
def events_page():
    return render_template("events.html")

@app.route("/about.html")
def about_page():
    return render_template("about.html")

@app.route("/login.html")
def login_page():
    return render_template("login.html")

@app.route("/organizations.html")
def organizations_page():
    return render_template("organizations.html")

@app.route("/profile.html")
def profile_page():
    return render_template("profile.html")

@app.route("/signup.html")
def signup_page():
    return render_template("signup.html")

@app.route("/create_event.html")
def create_event_page():
    return render_template("create_event.html")

@app.route("/create_organization.html")
def create_org_page():
    return render_template("create_organization.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug = False)