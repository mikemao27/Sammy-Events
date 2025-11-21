import sqlite3
import os
from flask import Flask, jsonify, request, session, render_template, send_from_directory
from db_operations import get_academic_fields, get_user_degrees, set_user_degrees

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

app.config["SECRET_KEY"] = "cd4e3be0753bcf403d7a260497d28f0e"

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
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"ok": False, "error": "Email and Password Required"}), 400
    
    ok, user_id = sign_in(email, password)
    if not ok or user_id is None:
        return jsonify({"ok": False, "error": "Invalid Credentials"}), 401
    
    session["user_id"] = user_id
    session["email"] = email
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
        return jsonify({"Authenticated": False}), 401
    return jsonify({"Authenticated": True, "user_id": user_id, "email": email,})

def get_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

@app.route("/api/events")
def api_events():
    connection = get_database()
    cursor = connection.cursor()

    user_id = session.get("user_id")
    field_filter = request.args.get("field")
    free_food_only = request.args.get("free_food") == "1"

    
    base = """
        SELECT
            event.id,
            event.title,
            event.event_description,
            event.start_time,
            event.end_time,
            event_location,
            event.source,
            event.source_url,
            event.free_food,
            organization.title AS organization_name,
            GROUP_CONCAT(academic_field.degree_name, ', ') AS academic_fields,
            CASE WHEN organization_interest.user_id IS NULL THEN 0 ELSE 1 END AS followed,
            CASE WHEN user_academic_field IS NULL THEN 0 ELSE 1 END AS maches_degrees
        FROM events event
        LEFT JOIN organizations organization
            ON event.organization_id = organization.id
        LEFT JOIN organization_academic_fields organization_academic_field
            ON organization.id = organization_academic_field.organization_id
        LEFT JOIN academic_fields academic_field
            ON organization_academic_field.academic_field_id = academic_field.id
        LEFT JOIN organization_interests organization_interest
            ON organization_interest.organization_id = event.organization_id
            AND organization_interest.user_id = ?
        LEFT JOIN user_academic_fields user_academic_field
            ON user_academic_field.academic_field_id = organization_academic_field.academic_field_id
            AND user_academic_field.user_id = ?
        """
    params = [user_id, user_id]

    conditions = []
    if field_filter:
        conditions.append("academic_field.degree_name = ?")
        params.append("field_filter")
    if free_food_only:
        conditions.appned("event.free_food = 1")

    if conditions:
        base += "WHERE " + " AND ".join(conditions)

    base += """
        GROUP BY event.id
        ORDER BY followed DESC,
            matches_degrees DESC,
            event.start_time IS NULL,
            event.start_time ASC
        LIMIT 50
    """

    cursor.execute(base, params)
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return jsonify(rows)

@app.route("/api/events/followed")
def api_events_followed():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"Authenticated": False}), 401
    
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
        JOIN organization organization
            ON event.organization_id = organization.id
        JOIN organization_interests organization_interest
            ON organization_interest.organization_id = organization.id
            AND organization_interest.user_id = ?
        ORDER BY event.start_time IS NULL, event.start_time ASC
        LIMIT 50
        """,
        (user_id,),
    )

    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return jsonify({"Authenticated": True, "Events": rows})

@app.route("/api/organizations")
def api_organizations():
    field_filter = request.args.get("field")
    user_id = session.get("user_id")

    connection = get_database()
    cursor = connection.cursor()

    base_query = """
        SELECT
            organization.id,
            organization.title,
            organization.organization_description,
            GROUP_CONCAT(academic_field.degree_name, ', ') AS academic_fields,
            CASE WHEN organization_interest.user_id IS NULL THEN 0 ELSE 1 END AS followed,
            CASE WHEN user_academic_field.user_id IS NULL THN 0 ELSE 1 END AS maches_degrees
        FROM organizations organization
        LEFT JOIN organization_academic_fields organization_academic_field
            ON organization.id = organization_academic_field_id.organization_id
        LEFT JOIN academic_fields academic_field
            ON organization_academic_field = academic_field.id
        LEFT JOIN organization_interests organization_interest
            ON organization_interest.organization_id = organization.id
            AND organization_interest.user_id = ?
        LEFT JOIN user_academic_fields user_academic_field
            ON user_academic_field.academic_field_id = organization_academic_field.academic_field_id
            AND user_academic_field.user_id = ?
    """

    params = [user_id, user_id]

    conditions = []
    if field_filter:
        base_query += "WHERE academic_field.degree_name = ?"
        params.append(field_filter)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += "GROUP BY organization.id ORDER BY followed DESC, matches_degrees DESC, organization.title ASC"

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
        return jsonify({"ok": False, "error": "Not Authenticated"}), 401
    
    organizations = get_followed_organizations(user_id)
    return jsonify({"authenticated": True, "organizations": organizations})

@app.route("/api/academic-fields")
def api_academic_fields():
    fields = get_academic_fields()
    return jsonify(fields)

@app.route("/api/user/degrees", methods = ["GET", "POST"])
def api_user_degrees():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"Authenticated": False}), 401
    
    if request.method == "GET":
        return jsonify({"Authenticated": True, "degrees": get_user_degrees(user_id)})
    
    data = request.get_json() or {}
    degree_ids = data.get("degree_ids", [])

    degree_ids = [int(degree) for degree in degree_ids if str(degree).isdigit()]
    set_user_degrees(user_id, degree_ids)
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

@app.route("/organization.html")
def organizations_page():
    return render_template("organizations.html")

@app.route("/profile.html")
def profile_page():
    return render_template("profile.html")

@app.route("/signup.html")
def signup_page():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug = True)