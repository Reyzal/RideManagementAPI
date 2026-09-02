# Testing strategy

The suite uses pytest, pytest-django, and DRF's `APIClient` against the HTTP and database boundary.

| Concern | Evidence |
|---|---|
| Authentication | Missing/invalid tokens return `401` |
| Authorization | Non-admin returns `403`; admin succeeds |
| Pagination | List includes count and results |
| Filtering | Status and rider email select expected rides |
| Event window | Events older than 24 hours are excluded |
| Ordering | Pickup time asc/desc |
| Geospatial sorting | Nearest pickup first; `distance_km` present |
| Validation | Missing coordinates/out-of-range latitude return `400` |
| Query behavior | Ride list is held to four queries |

```bash
uv run pytest
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

The suite does not prove load capacity, target-database plans, token lifecycle, exhaustive coordinate edges, full write validation, published schema compatibility, or deployment correctness. The query count catches N+1 regressions; it is not a benchmark.

When adding behavior, test the public contract, invalid input and access paths, deterministic ordering, relationship query counts, and migration drift.

