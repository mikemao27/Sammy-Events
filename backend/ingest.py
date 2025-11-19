# Getting event data from events.rice.edu and OwlNest.
import sqlite3
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import feedparser

DATABASE_PATH = "database/events.db"
EVENTS_RSS_URL = "https://events.rice.edu/live/rss/events/header/All%20Events"
OWL_NEST_RSS_URL = "https://owlnest.rice.edu/events.rss"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def insert_academic_fields():
    connection = get_connection()
    cursor = connection.cursor()

    academic_fields = [
        "Rice University", "Architecture", "Business", "STEM", "Humanities and Arts", 
        "Social Sciences", "Career and Professional", "Sports", 
        "Community, Culture, and Identity", "Environmental and Sustainability",
    ]

    for academic_field in academic_fields:
        cursor.execute(
            "INSERT OR IGNORE INTO academic_fields (degree_name) VALUES (?)",
            (academic_field,)
        )
    
    connection.commit()
    connection.close()

# Organizations -> Academic Fields.
# Rice University: 1
# Architecture: 2
# Business: 3
# STEM: 4
# Humanities and Arts: 5
# Social Sciences: 6
# Career and Professional: 7
# Sports: 8
# Community, Culture, and Identity: 9
# Environmental and Sustainability: 10

# Read the large .csv file storing all of the organizations and their academic fields.
def read_organizations():
    organizations = []
    organizations_map = {}
    with open("database/organizations.csv", "r", encoding = "utf-8") as file:
        for line in file:
            line = line.strip()
        
            if not line:
                continue

            parts = line.rsplit(":", 1)
            organization_name = parts[0].strip()
            organizations.append(organization_name)
            right = parts[1].strip()

            # Remember, the academic fields are a sequence of integers as a string.
            right_split = right.split(", ")
            academic_fields = []
            for index in range(0, len(right_split)):
                degree = right_split[index].strip()
                if degree.isdigit():
                    academic_fields.append(int(degree))
            
            organizations_map[organization_name] = academic_fields
    
    return organizations, organizations_map

def parse_organizations(organizations_list):
    organizations = []
    for organization in organizations_list:
        title = organization

        organizations.append({
            "title": title,
        })
    
    return organizations

# Insert organization names into the organization database.
def insert_organizations(organizations):
    connection = get_connection()
    cursor = connection.cursor()

    for organization in organizations:
        cursor.execute(
            """
            INSERT OR IGNORE INTO organizations
                (title)
            VALUES
                (:title)
            """,
            organization,
        )

    connection.commit()
    connection.close()

def get_organization_id(name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM organizations WHERE title = ?", (name,)
    )

    result = cursor.fetchone()
    connection.close()

    if result is None:
        return None
    return result[0]

def map_organizations(organizations_map):
    connection = get_connection()
    cursor = connection.cursor()

    for organization in organizations_map.keys():
        title = organization
        academic_field_ids = organizations_map[organization]

        organization_id = get_organization_id(title)
        
        if organization_id is None:
            continue

        for academic_field_id in academic_field_ids:
            cursor.execute(
                """
                INSERT OR IGNORE INTO organization_academic_fields(organization_id, academic_field_id)
                VALUES (?, ?)
                """,
                (organization_id, academic_field_id)
            )
        
    connection.commit()
    connection.close() 

# Rice Events Page Helper Methods.
def parse_events_description(html: str) -> str | None:
    if not html:
        return None
    parser = BeautifulSoup(html, "html.parser")
    text = parser.get_text(separator = " ", strip = True)
    return text or None

def get_events_times(entry):
    published = getattr(entry, "published_parsed", None)
    if not published:
        return None, None
    
    date = datetime(*published[:6], tzinfo = timezone.utc)
    start_time = date.isoformat()
    end_time = None
    return start_time, end_time

def get_event_location(entry):
    return getattr(entry, "georss_featurename", None)

# OwlNest Events Page Helper Methods.
def parse_owlnest_description(html):
    parser = BeautifulSoup(html, "html.parser")

    description_block = parser.select_one(".p-description.description")
    description = None
    if description_block:
        description = description_block.get_text(separator = " ", strip = True)

    start_tag = parser.select_one(".dt-start")
    end_tag = parser.select_one(".dt-end")

    start_time = None
    if start_tag and start_tag.has_attr("datetime"):
        start_time = start_tag["datetime"]
    end_time = None
    if end_tag and end_tag.has_attr("datetime"):
        end_time = end_tag["datetime"]

    location_tag = parser.select_one(".p-location.location")
    location = None
    if location_tag:
        location = location_tag.get_text(strip = True)

    return description, start_time, end_time, location

# Parse both feeds.
def parse_rss():
    events_feed = feedparser.parse(EVENTS_RSS_URL)
    owl_nest_feed = feedparser.parse(OWL_NEST_RSS_URL)
    events = []

    # Rice Events Page.
    for entry in events_feed.entries:
        title = entry.title
        link = entry.link

        raw_html = getattr(entry, "description", "")
        description = parse_events_description(raw_html)
        start_time, end_time = get_events_times(entry)
        location = get_event_location(entry)

        events.append({
            "source": "events.rice.edu",
            "source_id": link,
            "title": title,
            "event_description": description,
            "source_url": link,
            "start_time": start_time,
            "end_time": end_time,
            "event_location": location,
            "free_food": False,
            "organization_id": 1
        })
    
    # OwlNest Events Page.
    for entry in owl_nest_feed.entries:
        title = entry.title
        link = entry.link

        raw_html = getattr(entry, "description", "")
        description, start_time, end_time, location = parse_owlnest_description(raw_html)

        events.append({
            "source": "owlnest.rice.edu",
            "source_id": link,
            "title": title,
            "event_description": description,
            "source_url": link,
            "start_time": start_time,
            "end_time": end_time,
            "event_location": location,
        })
    
    return events

# Insert events into the database.
def insert_events(events):
    connection = get_connection()
    cursor = connection.cursor()

    for event in events:
        cursor.execute(
            """
            INSERT INTO events
                (source, source_id, title, event_description, source_url,
                start_time, end_time, event_location)
            VALUES
                (:source, :source_id, :title, :event_description, :source_url,
                :start_time, :end_time, :event_location)
            ON CONFLICT(source, source_id) DO UPDATE SET
                title = excluded.title,
                event_description = excluded.event_description,
                source_url = excluded.source_url,
                start_time = excluded.start_time,
                end_time = excluded.end_time,
                event_location = excluded.event_location;
            """,
            event,
        )

    connection.commit()
    connection.close()

if __name__ == "__main__":
    events = parse_rss()
    print(f"Fetched {len(events)} events from RSS!")

    insert_events(events)
    print("Events inserted into the database!")

    insert_academic_fields()
    print("Degrees inserted into the database!")

    organizations_list, organizations_map = read_organizations()
    organizations = parse_organizations(organizations_list)
    insert_organizations(organizations)
    print("Organizations inserted into the database!")

    map_organizations(organizations_map)
    print("Organizations have been mapped to their academic fields!")
    