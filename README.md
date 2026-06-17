# Ride Management API

A Django REST Framework API for managing ride information, users, and ride events.

This project was built as a backend assessment. The main goal is to provide a clean and performant REST API for rides while keeping access restricted to users with an `admin` role.

## Features

* Django REST Framework CRUD APIs
* Models for `User`, `Ride`, and `RideEvent`
* Admin-role token authentication
* Paginated ride list endpoint
* Filter rides by status
* Filter rides by rider email
* Sort rides by pickup time
* Sort rides by distance from a given pickup GPS location
* Optimized ride list query using `select_related` and filtered `Prefetch`
* `todays_ride_events` field that only returns ride events from the last 24 hours
* Automated tests for authentication, filtering, sorting, recent events, and query count
* Bonus raw SQL report for trips longer than 1 hour grouped by month and driver

## Tech Stack

* Python
* Django
* Django REST Framework
* django-filter
* pytest
* pytest-django
* uv for dependency management

## Project Structure

```text
RideManagementAPI/
├── RideManagementAPI/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── rides/
│   ├── authentication.py
│   ├── filters.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── tests/
│       ├── __init__.py
│       └── test_ride_api.py
├── manage.py
├── pyproject.toml
├── uv.lock
├── pytest.ini
├── .gitignore
└── README.md
```

## Main Models

### User

Represents a system user.

Important fields:

```text
id_user
role
first_name
last_name
email
phone_number
```

The `role` field is used for API access control. Only users with:

```text
role = admin
```

can access the API endpoints.

### Ride

Represents a ride booking/trip.

Important fields:

```text
id_ride
status
id_rider
id_driver
pickup_latitude
pickup_longitude
dropoff_latitude
dropoff_longitude
pickup_time
```

### RideEvent

Represents events that happen during a ride.

Important fields:

```text
id_ride_event
id_ride
description
created_at
```

Examples of event descriptions:

```text
Status changed to pickup
Status changed to dropoff
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Reyzal/RideManagementAPI.git
cd RideManagementAPI
```

### 2. Install dependencies

This project uses `uv`.

```bash
uv sync
```

If dependencies need to be added again manually:

```bash
uv add django djangorestframework django-filter
uv add --dev pytest pytest-django
```

### 3. Run migrations

```bash
uv run python manage.py migrate
```

### 4. Check the project

```bash
uv run python manage.py check
```

Expected output:

```text
System check identified no issues
```

### 5. Run the development server

```bash
uv run python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/api/
```

## Authentication

The API uses a simple token-based authentication system connected to the project `User` model.

Only users with:

```text
role = admin
```

can access the API.

Requests must include this header:

```text
Authorization: Token <your-token>
```

Example:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" http://127.0.0.1:8000/api/rides/
```

## Creating an Admin Token for Local Testing

Open the Django shell:

```bash
uv run python manage.py shell
```

Then run:

```python
from rides.models import ApiToken, User

admin = User.objects.create(
    role="admin",
    first_name="Admin",
    last_name="User",
    email="admin@example.com",
    phone_number="09170000000",
)

token = ApiToken.objects.create(user=admin)

print(token.key)
```

Copy the printed token and use it in the `Authorization` header.

## API Endpoints

### API Root

```text
GET /api/
```

Shows the available API resources.

### Users

```text
GET    /api/users/
POST   /api/users/
GET    /api/users/{id_user}/
PUT    /api/users/{id_user}/
PATCH  /api/users/{id_user}/
DELETE /api/users/{id_user}/
```

### Rides

```text
GET    /api/rides/
POST   /api/rides/
GET    /api/rides/{id_ride}/
PUT    /api/rides/{id_ride}/
PATCH  /api/rides/{id_ride}/
DELETE /api/rides/{id_ride}/
```

### Ride Events

```text
GET    /api/ride-events/
POST   /api/ride-events/
GET    /api/ride-events/{id_ride_event}/
PUT    /api/ride-events/{id_ride_event}/
PATCH  /api/ride-events/{id_ride_event}/
DELETE /api/ride-events/{id_ride_event}/
```

## Ride List API

The main endpoint is:

```text
GET /api/rides/
```

This endpoint returns a paginated list of rides.

Example response shape:

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id_ride": 1,
      "status": "pickup",
      "id_rider": {
        "id_user": 2,
        "role": "rider",
        "first_name": "Test",
        "last_name": "Rider",
        "email": "rider@example.com",
        "phone_number": "09171111111"
      },
      "id_driver": {
        "id_user": 3,
        "role": "driver",
        "first_name": "Test",
        "last_name": "Driver",
        "email": "driver@example.com",
        "phone_number": "09172222222"
      },
      "pickup_latitude": 10.3157,
      "pickup_longitude": 123.8854,
      "dropoff_latitude": 10.293,
      "dropoff_longitude": 123.902,
      "pickup_time": "2026-06-17T10:00:00Z",
      "todays_ride_events": [
        {
          "id_ride_event": 1,
          "id_ride": 1,
          "description": "Status changed to pickup",
          "created_at": "2026-06-17T10:15:00Z"
        }
      ]
    }
  ]
}
```

## Filtering

### Filter by ride status

```text
GET /api/rides/?status=pickup
```

Example using PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rides/?status=pickup" `
  -Headers @{ Authorization = "Token YOUR_TOKEN_HERE" }
```

### Filter by rider email

```text
GET /api/rides/?rider_email=rider@example.com
```

Example:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rides/?rider_email=rider@example.com" `
  -Headers @{ Authorization = "Token YOUR_TOKEN_HERE" }
```

### Combine filters

```text
GET /api/rides/?status=pickup&rider_email=rider@example.com
```

## Sorting

### Sort by pickup time

Ascending:

```text
GET /api/rides/?ordering=pickup_time
```

Descending:

```text
GET /api/rides/?ordering=-pickup_time
```

### Sort by pickup distance

Distance sorting is calculated in the database so that pagination still works correctly.

```text
GET /api/rides/?sort=distance&lat=10.3157&lng=123.8854
```

Example:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rides/?sort=distance&lat=10.3157&lng=123.8854" `
  -Headers @{ Authorization = "Token YOUR_TOKEN_HERE" }
```

When distance sorting is used, the API includes:

```json
"distance_km": 0.0
```

### Distance sorting validation

The API requires both `lat` and `lng` when using:

```text
sort=distance
```

Invalid examples:

```text
/api/rides/?sort=distance
/api/rides/?sort=distance&lat=999&lng=123.8854
/api/rides/?sort=distance&lat=10.3157&lng=999
```

These return `400 Bad Request`.

## Performance Notes

The ride list endpoint is optimized for large datasets.

### Rider and Driver Loading

The API uses:

```python
select_related("id_rider", "id_driver")
```

This loads the related rider and driver in the same query as the ride list.

### Recent Ride Events Only

The `RideEvent` table is expected to grow very large, so the API must not load the full event history for every ride.

The API uses a filtered prefetch:

```python
Prefetch(
    "ride_events",
    queryset=RideEvent.objects.filter(created_at__gte=last_24_hours),
    to_attr="todays_ride_events",
)
```

This means the API only loads ride events from the last 24 hours and attaches them to each ride as:

```text
todays_ride_events
```

Old ride events are not included in the ride list response.

### Query Count

The ride list is designed to run with a low number of database queries:

```text
1 query for paginated rides with rider and driver
1 query for today's ride events
1 query for pagination count
```

Authentication adds one separate token lookup query.

So in automated tests, the full request is expected to use around:

```text
4 queries total
```

That includes:

```text
1 authentication query
1 pagination count query
1 ride list query with rider and driver
1 filtered today's ride events query
```

## Indexing Notes

Indexes are added for common lookup and sorting fields:

```text
User.email
User.role
Ride.status
Ride.pickup_time
Ride.pickup_latitude + Ride.pickup_longitude
Ride.id_rider + Ride.status
RideEvent.id_ride + RideEvent.created_at
RideEvent.created_at
RideEvent.description
ApiToken.key
```

These indexes help with filtering, sorting, authentication, and recent event lookup.

## Running Tests

Run all tests:

```bash
uv run pytest
```

Expected result:

```text
13 passed
```

The tests cover:

```text
Authentication required
Invalid token rejected
Non-admin user rejected
Admin user allowed
Pagination
Filtering by status
Filtering by rider email
todays_ride_events only includes last 24-hour events
Ordering by pickup_time ascending
Ordering by pickup_time descending
Distance sorting
Distance sorting validation
Ride list query count
```

## Example Local Test Requests

### List rides

```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rides/" `
  -Headers @{ Authorization = "Token YOUR_TOKEN_HERE" }

$response | ConvertTo-Json -Depth 10
```

### Filter pickup rides

```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rides/?status=pickup" `
  -Headers @{ Authorization = "Token YOUR_TOKEN_HERE" }

$response | ConvertTo-Json -Depth 10
```

### Sort by distance

```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rides/?sort=distance&lat=10.3157&lng=123.8854" `
  -Headers @{ Authorization = "Token YOUR_TOKEN_HERE" }

$response | ConvertTo-Json -Depth 10
```

## Bonus SQL Report

The reporting requirement is to count trips where the duration from pickup to dropoff was more than 1 hour, grouped by month and driver.

A pickup event is identified by:

```text
Status changed to pickup
```

A dropoff event is identified by:

```text
Status changed to dropoff
```

The query below assumes the default Django table names:

```text
rides_ride
rides_user
rides_rideevent
```

### PostgreSQL SQL

```sql
SELECT
    TO_CHAR(pickup_event.created_at, 'YYYY-MM') AS month,
    CONCAT(driver.first_name, ' ', driver.last_name) AS driver,
    COUNT(*) AS count_of_trips_gt_1_hr
FROM rides_ride AS ride
JOIN rides_user AS driver
    ON driver.id_user = ride.id_driver
JOIN rides_rideevent AS pickup_event
    ON pickup_event.id_ride = ride.id_ride
    AND pickup_event.description = 'Status changed to pickup'
JOIN rides_rideevent AS dropoff_event
    ON dropoff_event.id_ride = ride.id_ride
    AND dropoff_event.description = 'Status changed to dropoff'
WHERE dropoff_event.created_at - pickup_event.created_at > INTERVAL '1 hour'
GROUP BY
    TO_CHAR(pickup_event.created_at, 'YYYY-MM'),
    driver.first_name,
    driver.last_name
ORDER BY
    month,
    driver;
```

Example output:

```text
Month    Driver      Count of Trips > 1 hr
2024-01  Chris H     4
2024-01  Howard Y    5
2024-02  Chris H     7
2024-03  Randy W     11
```

## Design Decisions

### Why use a custom token model?

The assessment requires access control based on a `User.role` field. Because the project has its own `User` model for the assessment data, I used a simple `ApiToken` model connected directly to that user.

This keeps the authentication logic easy to review:

```text
Token belongs to User
User.role must be admin
Only admin can access the API
```

### Why use filtered prefetch?

The ride event table can become very large. Loading all events for every ride would cause serious performance issues.

Filtered `Prefetch` solves this by only loading events from the last 24 hours and keeping the query count low.

### Why calculate distance in SQL?

Distance sorting must work with pagination. If rides were sorted in Python after fetching, pagination could return the wrong results.

By annotating the queryset with `distance_km` and ordering in the database, sorting remains efficient and pagination stays correct.

## Security Notes

* `.env` files are ignored by Git.
* PyCharm `.idea/` files are ignored by Git.
* Local SQLite databases are ignored by Git.
* API tokens should not be committed.
* Real secrets should be stored in environment variables.
* If a token is accidentally shared, delete it from the database and create a new one.



