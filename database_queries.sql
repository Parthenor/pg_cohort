-- PG Cohort: SQL examples for DBMS demonstration
-- Run these in DB Browser for SQLite or a SQLite command-line client after app.py has run.

-- 1. Display all available PG listings
SELECT * FROM pg_accommodations WHERE available_beds > 0;

-- 2. Find PGs in North Campus with rent up to 12,000
SELECT pg_name, location, monthly_rent, facilities
FROM pg_accommodations
WHERE location = 'North Campus' AND monthly_rent <= 12000;

-- 3. INNER JOIN: student preferences with student details
SELECT s.full_name, s.college, p.budget, p.sleep_schedule, p.study_style
FROM students s
INNER JOIN roommate_preferences p ON s.student_id = p.student_id;

-- 4. Show all booking requests with student and PG names
SELECT b.booking_id, s.full_name, p.pg_name, b.status, b.request_date
FROM bookings b
INNER JOIN students s ON b.student_id = s.student_id
INNER JOIN pg_accommodations p ON b.pg_id = p.pg_id;

-- 5. Aggregate: number of PGs per location
SELECT location, COUNT(*) AS total_pgs, MIN(monthly_rent) AS lowest_rent
FROM pg_accommodations
GROUP BY location;

-- 6. HAVING: locations with at least two listed PGs
SELECT location, COUNT(*) AS total_pgs
FROM pg_accommodations
GROUP BY location
HAVING COUNT(*) >= 2;

-- 7. Subquery: PGs below the average listed rent
SELECT pg_name, monthly_rent
FROM pg_accommodations
WHERE monthly_rent < (SELECT AVG(monthly_rent) FROM pg_accommodations);

-- 8. UPDATE example (use only if you want to demonstrate updates)
-- UPDATE bookings SET status = 'Approved' WHERE booking_id = 1;

-- 9. DELETE example (use only if you want to demonstrate deletion)
-- DELETE FROM bookings WHERE booking_id = 1;

-- 10. Index example (optional)
CREATE INDEX IF NOT EXISTS idx_pg_location ON pg_accommodations(location);
CREATE INDEX IF NOT EXISTS idx_pg_rent ON pg_accommodations(monthly_rent);
