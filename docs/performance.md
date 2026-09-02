# Performance, indexes, and query-count reasoning

## Four-query regression budget

| # | Query | Purpose |
|---:|---|---|
| 1 | Token joined to user | Authentication and role evaluation |
| 2 | `COUNT(*)` | Page-number total |
| 3 | Ride page joined to rider/driver | Records and nested users |
| 4 | Recent events for page rides | Collection data without N+1 queries |

The count applies to the tested list path. SQL complexity, rows, serialization, concurrency, and indexes also affect latency.

## Distance before pagination

The view annotates every matching ride with great-circle distance, then orders by `distance_km` and `id_ride`. DRF paginates that queryset. Sorting an already-fetched page would find the nearest ride only within an arbitrary subset.

The latitude/longitude B-tree index does not make the trigonometric expression a spatial nearest-neighbor lookup. At scale, validate the target plan and consider geospatial types, bounding boxes, and spatial indexes.

## Index-to-access-path map

| Declaration | Intended path | Caveat |
|---|---|---|
| `ApiToken.key` | Credential lookup | Unique constraints typically index; `db_index` may be redundant |
| `User.email` | Rider-email filter | `iexact` behavior depends on database/collation |
| `User.role` | Role lookups | Permission uses the loaded user; selectivity may be low |
| `Ride.status` | Status filter | Field and explicit single-column indexes are both declared |
| `Ride.pickup_time` | Time ordering | Field and explicit indexes are both declared |
| `(id_rider, status)` | Rider/status combinations | Public filter uses rider email; validate the plan |
| `(pickup_latitude, pickup_longitude)` | Coordinate access | Does not directly accelerate trig sorting |
| `(id_ride, created_at)` | Recent events for selected rides | Closely matches the prefetch |
| `RideEvent.created_at` | Time window | Field and explicit indexes are both declared |
| `RideEvent.description` | Reporting | No current API filter |

This documents intent, not proof of index use. Redundant indexes cost writes/storage; cleanup requires a reviewed migration and target-database evidence.

## Evaluation method

1. Keep the query-count test for N+1 detection.
2. Seed representative volumes and distributions.
3. Capture SQL and use the target database's `EXPLAIN ANALYZE`.
4. Measure p50/p95 latency, database time, rows, and concurrency.
5. Change queries/indexes with evidence, then rerun tests and measurements.

SQLite is a fast tutorial baseline. Production claims require the deployment database.

