# Ride Management API

A compact Django REST Framework case study in designing a query-efficient, authenticated API for ride operations.

This repository is both a runnable portfolio project and a guided tour of practical backend decisions: explicit authorization, safe filtering, pagination-preserving geospatial ordering, and prevention of N+1 queries.

> **Project boundary:** this is an educational reference implementation. It uses SQLite and development settings locally. The custom token model demonstrates the authentication flow, but it is not a drop-in production identity system.

## What this project demonstrates

- CRUD viewsets for users, rides, and ride events
- Custom token authentication separated from admin-role authorization
- Case-insensitive filtering by ride status and rider email
- Deterministic ordering and page-number pagination (20 records per page)
- Database-side great-circle distance ordering from a pickup location
- `select_related` and filtered `Prefetch` to bound ride-list queries
- Explicit model indexes for common access patterns
- Behavioral, authorization, validation, ordering, and query-count tests
- Reproducible dependencies through `uv.lock`

## Architecture at a glance

```text
Client
  │  Authorization: Token <key>
  ▼
DRF router → ApiTokenAuthentication → IsAdminRole
  │
  ▼
ModelViewSet → filters / ordering / pagination → serializer
  │
  ▼
Django ORM → SQLite (local development)
              ├─ rides joined with rider + driver
              └─ recent events loaded in one filtered prefetch
```

Read the [architecture walkthrough](docs/architecture.md) for the request lifecycle, data model, and module boundaries.

## Quick start

Prerequisites: Git and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Reyzal/RideManagementAPI.git
cd RideManagementAPI
uv sync --locked
uv run python manage.py migrate
uv run python manage.py check
uv run pytest
uv run python manage.py runserver
```

The API root is `http://127.0.0.1:8000/api/`. The current suite contains 13 tests.

### Create a local admin token

Start `uv run python manage.py shell`, then:

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

```bash
curl -H "Authorization: Token YOUR_TOKEN" http://127.0.0.1:8000/api/rides/
```

Do not commit or share generated tokens.

## API guide

All endpoints require a valid token belonging to a user whose `role` is exactly `admin`.

| Resource | Collection | Detail | Operations |
|---|---|---|---|
| Users | `/api/users/` | `/api/users/{id_user}/` | GET, POST, PUT, PATCH, DELETE |
| Rides | `/api/rides/` | `/api/rides/{id_ride}/` | GET, POST, PUT, PATCH, DELETE |
| Ride events | `/api/ride-events/` | `/api/ride-events/{id_ride_event}/` | GET, POST, PUT, PATCH, DELETE |

### Ride list examples

```text
GET /api/rides/?status=pickup
GET /api/rides/?rider_email=rider@example.com
GET /api/rides/?status=pickup&rider_email=rider@example.com
GET /api/rides/?ordering=pickup_time
GET /api/rides/?ordering=-pickup_time
GET /api/rides/?sort=distance&lat=10.3157&lng=123.8854
GET /api/rides/?page=2
```

`status` and `rider_email` use case-insensitive exact matching. Supported `ordering` fields are `pickup_time` and `id_ride`. Distance ordering requires both coordinates, validates their ranges, returns `distance_km`, and uses `id_ride` as a stable tie-breaker. Invalid parameters return `400 Bad Request`.

A paginated response has DRF's standard `count`, `next`, `previous`, and `results` fields. Each ride embeds its rider and driver and includes only events from the previous 24 hours at request time.

## Performance model

1. `select_related("id_rider", "id_driver")` joins both users into the ride query.
2. A filtered `Prefetch` retrieves recent events for all rides on the page in one query.
3. Distance is calculated in SQL so the complete result set is ordered before pagination.
4. A regression test asserts four queries for an authenticated, paginated list request.

| Query | Purpose |
|---|---|
| 1 | Look up the token and its user |
| 2 | Count matching rides for pagination |
| 3 | Fetch the page of rides with rider and driver |
| 4 | Fetch recent events for the rides on that page |

This is a regression budget for the tested implementation, not a universal latency claim. See [performance and data access](docs/performance.md) for indexing rationale and measurement guidance.

## Authentication and security boundary

`ApiTokenAuthentication` returns `401` for malformed or unknown credentials. `IsAdminRole` then returns `403` for an authenticated non-admin. Keeping these responsibilities separate makes both paths independently testable.

Current limitations are intentional and visible:

- Tokens are stored directly; there is no expiry, rotation, revocation endpoint, or audit trail.
- Roles are free-form strings rather than constrained choices or a policy model.
- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` are development settings.
- SQLite is convenient for the tutorial; production query plans must be validated separately.
- The API has no throttling, published schema, deployment configuration, or observability stack.

For a real service, use environment-specific settings, HTTPS, maintained identity, token lifecycle controls, least-privilege authorization, throttling, structured logging, and production-database testing.

## Learn through the repository

Follow the [tutorial learning path](docs/tutorial.md):

1. Run the service and map router URLs to viewsets.
2. Trace authentication and authorization.
3. Follow filtering, query composition, and serialization.
4. Inspect pagination-safe distance ordering.
5. Explain the four-query budget.
6. Evaluate indexes and production trade-offs.

Deep dives:

- [Architecture](docs/architecture.md)
- [Design decisions and trade-offs](docs/design-decisions.md)
- [Performance, indexes, and query-count reasoning](docs/performance.md)
- [Testing strategy](docs/testing.md)

## Project layout

```text
RideManagementAPI/
├── RideManagementAPI/       # Settings and root URLs
├── rides/
│   ├── authentication.py    # Credential lookup
│   ├── permissions.py       # Admin authorization
│   ├── filters.py           # Ride filters
│   ├── models.py            # Data model and indexes
│   ├── serializers.py       # API representation
│   ├── views.py             # Query and endpoint behavior
│   └── tests/               # API and query-budget tests
├── docs/
├── pyproject.toml
├── uv.lock
└── pytest.ini
```

## Verification

```bash
uv sync --locked
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest
```

GitHub Actions runs these checks for pull requests and pushes to `master`.

## Evolution path

Useful next increments—not current capabilities—include PostgreSQL query-plan validation, geospatial types and indexes, hashed/expiring credentials or standards-based identity, per-action permissions, OpenAPI documentation, observability, and deployment hardening.

