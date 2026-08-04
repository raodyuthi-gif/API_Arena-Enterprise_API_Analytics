# API Reference

Base URL (local dev): `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs` (Swagger) / `http://localhost:8000/redoc`

All endpoints except `/auth/login` and `/auth/refresh` require a Bearer JWT:
`Authorization: Bearer <access_token>`

Roles: `viewer` (read-only), `analyst` (read + write telemetry/registry/forecasts), `admin` (full access + user management).

---

## Authentication — `/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | none | Exchange email/password for an access + refresh token pair |
| POST | `/auth/refresh` | none (refresh token) | Exchange a refresh token for a new token pair |
| POST | `/auth/api-keys` | any user | Create a long-lived API key (shown once) |

## Users — `/users`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users/me` | any user | Current user's profile |
| GET | `/users` | admin | Paginated user list |
| POST | `/users` | admin | Create a user |
| GET | `/users/{id}` | admin | Get a user |
| PATCH | `/users/{id}` | admin | Update a user |
| DELETE | `/users/{id}` | admin | Delete a user |

## API Registry — `/apis`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/apis` | any user | List/search registered APIs (paginated) |
| POST | `/apis` | analyst+ | Register a new API |
| GET | `/apis/{id}` | any user | Get one API with tags + versions |
| PATCH | `/apis/{id}` | analyst+ | Update an API's status/SLA/ownership |
| DELETE | `/apis/{id}` | analyst+ | Remove an API from the registry |
| POST | `/apis/{id}/versions` | analyst+ | Add a version to an API |
| GET | `/apis/tags` | any user | List tags |
| POST | `/apis/tags` | analyst+ | Create a tag |

## Telemetry — `/telemetry`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/telemetry/ingest` | any user | Ingest up to 1000 request logs per call |

## Analytics — `/analytics`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/analytics/latency?api_id=&window=` | any user | P50/P90/P99 latency time series (`window`: `1h`\|`6h`\|`24h`\|`7d`\|`30d`) |
| GET | `/analytics/errors?api_id=&window=` | any user | Error rate + top failing endpoints |
| GET | `/analytics/traffic?api_id=&window=` | any user | Request volume time series |
| GET | `/analytics/summary` | any user | Platform-wide KPI summary |

## Health — `/health`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | any user | Composite health score for every registered API |
| GET | `/health/{api_id}` | any user | Health score for one API (persists a `health_checks` row) |

Health score is a weighted composite (`uptime 35% · error_rate 30% · latency 25% · trend 10%`) computed from the last hour of telemetry against each API's configured SLA. `>=85` healthy, `>=60` degraded, else critical.

## Forecast (ML) — `/forecast`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/forecast/train?api_id=` | analyst+ | Train a Prophet or Ridge model on historical telemetry |
| GET | `/forecast/{api_id}?horizon_hours=` | any user | Predicted hourly traffic with confidence bounds (max 720h) |
| GET | `/forecast/{api_id}/anomalies?lookback_hours=&sigma_threshold=` | any user | Flag traffic points that deviate from the model's prediction by more than N std deviations |

See [`ml-approach.md`](./ml-approach.md) for model selection rationale and training data details.

## Dashboard — `/dashboard`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/dashboard/overview` | any user | KPI summary + health counts in one call |
| WS | `/dashboard/realtime` | — | WebSocket heartbeat/live-metric stream |

## Admin — `/admin`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/stats` | admin | System-wide counts (users, APIs, request logs) |

## Observability

| Path | Description |
|---|---|
| `/metrics` | Prometheus scrape endpoint (enabled via `PROMETHEUS_ENABLED`) |
| `/` | Root liveness/info endpoint |
