# PG Cohort

PG Cohort is a Flask + SQLite coursework demo for browsing PG accommodation listings, registering a student profile, saving roommate preferences, viewing heuristic roommate matches, and submitting PG visit requests.

## Run locally (Mac/Linux)

1. Open Terminal and move into this folder.
2. Create a virtual environment (only needed once):
   ```bash
   python3 -m venv .venv
   ```
3. Activate it:
   ```bash
   source .venv/bin/activate
   ```
4. Install the requirement:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python3 app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser. Keep the Terminal window running while using the site.

## New account features

- Register with student details and roommate preferences.
- Log in and log out.
- View your saved profile.
- View roommate matches based on the logged-in user's preferences.
- Submit PG visit requests under your own account and see only your own bookings.
- Passwords are stored as hashes, not plain text.

## Existing database safety

The app uses `pg_cohort.db` in this folder. On startup it checks whether `students.password_hash` exists and adds the column only when it is missing. Existing student, PG, preference, and booking rows are not intentionally deleted. Old sample/demo profiles have no password and cannot log in; create a new account to use the account features. **Back up `pg_cohort.db` before replacing project files.**

## Important notes

- Roommate compatibility is a simple educational scoring heuristic, not a guarantee of compatibility.
- Booking requests are stored in the local database only; they do not contact a PG owner or make a real reservation.
- The fallback Flask secret key is for local demos only. Before deployment, set a strong random `FLASK_SECRET_KEY` environment variable and turn off Flask debug mode. Do not commit production secrets to GitHub.
- This is a student project, not a production-ready accommodation service.

## Database

The main tables are `students`, `roommate_preferences`, `pg_accommodations`, and `bookings`. See `database_queries.sql` and the DB Schema page for more information.


## ADA feature: Dijkstra's shortest path

The **Shortest Routes** page demonstrates Dijkstra's algorithm (ADA Unit 4). It models a small sample road network as a weighted graph and calculates the shortest route from a selected campus to each PG location. The implementation uses Python's `heapq` priority queue. With an adjacency list and a binary heap, the expected time complexity is **O((V + E) log V)** and space complexity is **O(V + E)**, where V is the number of vertices and E is the number of edges.

The network and distances are illustrative coursework data only; they are not live road directions or verified distances. Open **Shortest Routes** in the navigation bar and select a starting campus to see the calculated paths.
