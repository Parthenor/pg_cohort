# PG Cohort — Student Accommodation and Roommate Matching Platform

## 1. Introduction
PG Cohort is a database-backed prototype intended to help students explore paying-guest (PG) accommodation and find potential roommates with similar preferences. Students often need to consider rent, location, daily habits, study preferences, and cleanliness when choosing accommodation.

## 2. Objectives
- Store student information and roommate preferences in a relational database.
- Display PG listings and filter them by location and rent.
- Suggest potential roommates based on shared preferences.
- Record booking requests and their status.
- Demonstrate relational database concepts such as primary keys, foreign keys, constraints, joins, grouping, and subqueries.

## 3. Technology Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python and Flask
- Database: SQLite

## 4. Modules
1. **Home:** overview of sample students, PGs, and booking requests.
2. **PG listings:** displays available accommodations and supports location/rent filtering.
3. **Roommate matching:** calculates a simple weighted compatibility score based on budget, sleep schedule, study style, cleanliness, smoking preference, and preferred location.
4. **Booking requests:** inserts requests into the database and displays them using joins.
5. **Schema overview:** explains the tables and their relationships.

## 5. Database Design
### Students
`student_id` (PK), `full_name`, `email` (UNIQUE), `college`, `gender`, `city`

### PG Accommodations
`pg_id` (PK), `pg_name`, `location`, `monthly_rent`, `room_type`, `facilities`, `available_beds`, `distance_km`, `description`

### Roommate Preferences
`preference_id` (PK), `student_id` (FK and UNIQUE), `budget`, `sleep_schedule`, `study_style`, `cleanliness`, `smoking_preference`, `preferred_location`

### Bookings
`booking_id` (PK), `student_id` (FK), `pg_id` (FK), `request_date`, `status`, `message`

## 6. Relationships
- One student has one preference record (one-to-one).
- One student can submit many booking requests (one-to-many).
- One PG can receive many booking requests (one-to-many).

## 7. Matching Method
The prototype assigns points for similar budget and matching preferences. The score is a heuristic to rank potential roommates, not a guarantee of compatibility and not an implementation of Irving's algorithm.

## 8. Sample Testing
- Open PG listings and confirm that sample PG records appear.
- Filter listings by `North Campus` and a maximum rent.
- Select a student on the roommate page and confirm matches are ranked by score.
- Submit a booking request and confirm it appears on the bookings page with Pending status.
- Run the SQL statements in `database_queries.sql`.

## 9. Limitations
This is a classroom prototype using fictional sample data. It does not include authentication, online payments, property verification, real-time availability synchronization, or deployment security. The booking action records a request; it does not confirm a real reservation. The original synopsis lists Irving's, Ford–Fulkerson, Dijkstra's, and 0/1 Knapsack, but these algorithms are not implemented in this version.

## 10. Future Scope
- Add login and role-based access for students and PG owners.
- Add images, map integration, reviews, and verified listings.
- Improve roommate matching and let users set preference weights.
- Add an owner/admin interface to approve or reject requests.
- Add and test algorithm modules if required by project evaluation.

## 11. Conclusion
PG Cohort demonstrates how a relational database can support student accommodation discovery, preference-based roommate suggestions, and booking request management through a simple web application.


## ADA Algorithm Integration: Dijkstra's Shortest Path

PG Cohort includes a shortest-route demonstration based on Dijkstra's algorithm from Unit 4. The road network is represented as a weighted graph: locations are vertices and road links are edges with non-negative distance weights. A priority queue selects the currently closest unprocessed vertex, and shorter distances are relaxed until the shortest routes are determined. The page displays the calculated distance and path from a selected campus to each PG location.

**Complexity:** Using an adjacency list and a binary-heap priority queue, time complexity is O((V + E) log V), and space complexity is O(V + E). The road network uses illustrative sample distances for academic demonstration, not live navigation data.
