# Design decisions and trade-offs

These notes describe the implementation that exists today. Alternatives are not advertised as current features.

## Separate authentication from authorization

**Decision:** a custom authenticator resolves `Token <key>`; a separate permission checks `role == "admin"`.

**Why:** credential validity and policy fail differently (`401` versus `403`) and can be tested independently.

**Trade-off:** plain token storage and no expiry, scopes, rotation, revocation API, or audit records make this incomplete for production identity.

## Join singular relations; prefetch collections

**Decision:** use `select_related` for rider/driver and filtered `Prefetch` for events.

**Why:** foreign keys can join the main query; the one-to-many collection needs a second query. Filtering avoids loading full histories.

**Trade-off:** “today's” currently means the rolling previous 24 hours, not a calendar day. Calendar semantics would require an explicit timezone policy.

## Order geospatial results in SQL

**Decision:** annotate great-circle distance and order before pagination.

**Why:** sorting a fetched page in Python would not produce globally nearest rides. `id_ride` is a deterministic tie-breaker.

**Trade-off:** this is not a substitute for production geospatial types, spatial indexes, or target-database query-plan testing.

## Use page-number pagination

**Decision:** DRF returns pages of 20 with a total count.

**Why:** totals and navigation are intuitive for clients and tutorials.

**Trade-off:** counts and deep offsets can become expensive. Cursor pagination is a future option when scale outweighs arbitrary page access.

## Keep one Django app

**Decision:** the small domain remains in `rides`.

**Why:** it stays navigable without speculative layers.

**Trade-off:** dispatching, billing, or integration workflows may eventually justify use-case services and bounded contexts.

## Make query expectations executable

**Decision:** a test asserts four queries for the authenticated ride list.

**Why:** it detects accidental N+1 behavior.

**Trade-off:** exact counts are tied to this request shape and database; they do not establish production latency.

