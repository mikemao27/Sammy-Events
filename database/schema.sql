/* Create a database table to store events data */
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,

    title TEXT NOT NULL,
    event_description TEXT,
    source_url TEXT NOT NULL,

    start_time DATE,
    end_time DATE,
    event_location TEXT,
    free_food BOOLEAN,

    organization_id INTEGER,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),

    UNIQUE(source, source_id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    netID TEXT NOT NULL,
    email TEXT NOT NULL,
    user_password TEXT NOT NULL,
    phone_number TEXT,

    degrees TEXT,

    UNIQUE(netID),
    UNIQUE(email)
);

CREATE TABLE IF NOT EXISTS organization_interests (
    user_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,

    PRIMARY KEY (user_id, organization_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    organization_description TEXT,

    UNIQUE(title)
);

CREATE TABLE IF NOT EXISTS academic_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree_name TEXT NOT NULL,

    UNIQUE(degree_name)
);

CREATE TABLE IF NOT EXISTS user_academic_fields (
    user_id INTEGER NOT NULL,
    academic_field_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, academic_field_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (academic_field_id) REFERENCES academic_fields(id)
);

CREATE TABLE IF NOT EXISTS organization_academic_fields (
    organization_id INTEGER NOT NULL,
    academic_field_id INTEGER NOT NULL,

    PRIMARY KEY (organization_id, academic_field_id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (academic_field_id) REFERENCES academic_fields(id)
);