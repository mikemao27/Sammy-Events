## Events Nest Mobile and Web App
This is a personal mobile and web application built by Rice University undergrads during moments of peace and quiet. While this project is open-source and anyone may borrow code or inspiration from Events Nest, we would like for credit to be given for the production and launch of Events Nest.

## Goal of Events Nest
Events Nest aims to be an all-in-one hub for Rice University students to find and engage in campus events related to their major, minor, degree, or extra-curricular interests. Currently, campus events are isolated in private mailing lists, 
preventing interested students from being able to engage in these formative activities. Currently, Rice Owls are restricted by one-per-year club fairs and club gatherings which often conflict with existing class schedules. In addition, many clubs just aren't present at these campus events, preventing students from being able to engage in these organizations unless they have existing connections.

Events Nest serves to solve all of these problems through one intuitive, easy-to-use app. By scraping event data from Rice University department websites and campus clubs, we aim to provide a hub for students to view all campus events occuring on any given day. Students can then filter events by degree, club, etc. as well as sign up to be notified when an event they're interested in pops up. 

To make Events Nest more accessible, we've included many language options as well as design tweaks that make the app more intutiive to use based on a student's language preference, location, time-zone, etc. 

## Features
* Browse all campus events in a clean, card-based UI
* Filter events by free food availability
* Follow campus organizations and get recommended events
* Screen-reader for user accessibility

## Tech Stack
Frontend:
* HTML + CSS + JavaScript

Backend:
* Python + Flask
* SQLite database for user, event, and organization data
* Custom ingestion scripts for organization and event data

## Set-up Events Nest for Personal Usage
Please strictly adhere to the following instructions when setting up Events Nest for personal tinkering.

1. Clone the Repository
`git clone https://github.com/mikemao27/Events-Nest.git`
`cd Sammy-Events`

2. Create and Activate a Virtual Environment
On macOS/Linus, run: `python -m venv venv` and `source venv/bin/activate`
On Windows, run: `python -m venv venv` and `venv\Scripts\activate`

3. Install Dependencies
`pip install -r requirements.txt`

4. Database Setup and Features
To initialize the database, run: `python init_db.py`
To clear the database, run: `python clear_database.py`
To clear only user data, run: `python clear_users.py`

To load events and organization data into the database, run: `python backend/ingest.py` and then `python backend/update_org_descriptions.py`

5. Run the Web Application
To start the flask server, run `python backend/app.py`
