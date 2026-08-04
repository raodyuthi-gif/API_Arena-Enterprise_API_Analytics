# API Arena — Frontend

React + Vite dashboard for the Enterprise API Analytics Platform, with role-based
logins (Admin / Analyst / Viewer) backed by the FastAPI `/auth` endpoints.

## Local development

```bash
cd frontend
cp .env.example .env      # points at http://localhost:8000 by default
npm install
npm run dev                # http://localhost:5173
```

Or via Docker Compose from the repo root (spins up Postgres, Redis, backend,
frontend and monitoring together):

```bash
docker compose up --build
```

## Creating accounts to sign in with

The backend has no default users. Bootstrap an admin, analyst and viewer
account in one shot:

```bash
cd backend
python ../scripts/create_demo_users.py
```

This creates:

| Role    | Email                  | Password        |
| ------- | ----------------------- | ---------------- |
| Admin   | admin@apiarena.dev      | Admin@12345      |
| Analyst | analyst@apiarena.dev    | Analyst@12345    |
| Viewer  | viewer@apiarena.dev     | Viewer@12345     |

Change these passwords (or delete the accounts) before deploying anywhere
public — this script is for local/demo use only.

To see real numbers on the dashboard, also seed synthetic telemetry:

```bash
cd backend
python ../scripts/seed_synthetic_traffic.py --days 30 --apis 3
```

## What each role sees

- **Viewer** — Dashboard, API Registry, Errors & Complaints (read-only).
- **Analyst** — everything a Viewer sees, plus the Forecast Lab (train ML
  models and inspect predictions).
- **Admin** — everything an Analyst sees, plus the Admin Console (create
  users, change roles, deactivate accounts, platform-wide stats).

Route access is enforced both in the UI (`ProtectedRoute` hides nav items and
redirects to `/not-authorized`) and on the backend (FastAPI dependencies
`CurrentAdmin` / `CurrentAnalyst` reject the request regardless of what the
UI shows), so a viewer calling the admin endpoints directly still gets a 403.

## Production build

```bash
docker build -t api-arena-frontend --target production ./frontend
```

This produces the nginx-served static build used by `k8s/base/frontend.yaml`.