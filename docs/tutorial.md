# Tutorial: trace one request through the API

## 1. Establish a baseline

```bash
uv sync --locked
uv run python manage.py migrate
uv run python manage.py check
uv run pytest
```

Start at `RideManagementAPI/urls.py`, then follow `rides/urls.py`. **Checkpoint:** which classes handle the ride list and serialization?

## 2. Trace access

Read `rides/authentication.py`, then `rides/permissions.py`. Follow these tested paths: no/unknown token → `401`; valid non-admin token → `403`. **Checkpoint:** why are these separate?

## 3. Follow the queryset

Read `RideViewSet.get_queryset()`. `select_related` handles the user foreign keys; filtered `Prefetch` handles events and exposes `todays_ride_events` to the serializer. **Checkpoint:** what N+1 behavior would appear without these?

## 4. Compose filters and ordering

Read `rides/filters.py` and `ordering_fields`:

```text
/api/rides/?status=pickup
/api/rides/?rider_email=rider@example.com
/api/rides/?ordering=-pickup_time
```

**Checkpoint:** why is distance handled separately?

## 5. Understand pagination-safe distance

`_order_by_pickup_distance()` validates coordinates, builds a great-circle SQL expression, and orders before slicing.

```text
/api/rides/?sort=distance&lat=10.3157&lng=123.8854
```

**Checkpoint:** why would sorting only 20 fetched rows be incorrect?

## 6. Explain four queries

Run:

```bash
uv run pytest rides/tests/test_ride_api.py::test_ride_list_query_count_is_low -q
```

The budget covers authentication, pagination count, the joined ride page, and one event prefetch. **Checkpoint:** why does adding rides not add event queries?

## 7. Treat indexes as hypotheses

Compare `Meta.indexes` and `db_index` with [performance.md](performance.md). Several fields currently declare both a field index and an explicit single-column index; verify migrations and simplify only through a future schema change.

## 8. Identify the production gap

Read the README limitations and [design decisions](design-decisions.md). Propose one small next pull request and its tests. **Checkpoint:** can you distinguish implemented behavior from future hardening?

