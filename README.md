# Enterprise API Analytics & Performance Management Platform

[![CI](https://github.com/your-org/enterprise-api-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/enterprise-api-analytics/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **production-grade, full-stack platform** that gives enterprises a single pane of glass for monitoring, analyzing, and forecasting the health and performance of every API they expose.

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| **API Registry** | Central catalog — register, version, tag every API |
| **Usage Tracking** | Real-time telemetry ingestion with batch POST |
| **Latency Analytics** | P50/P90/P99 percentile charts per endpoint |
| **Error Analytics** | Error-rate heatmaps, top-failing endpoints |
| **Traffic Prediction** | Facebook Prophet (default) or Ridge regression, with confidence bounds |
| **Health Dashboard** | Composite health score with live WebSocket updates |
| **ML Forecasting** | Auto-retrains on a schedule (APScheduler), detects anomalies (>2σ residual) |
| **User Management** | JWT auth, RBAC (Admin/Analyst/Viewer), API keys |

---

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Alembic
- **Database**: PostgreSQL 15
- **Cache / Pub-Sub**: Redis 7
- **ML**: Prophet, scikit-learn, pandas
- **Frontend**: React 18 + Vite, Chart.js, Recharts
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes + Helm
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

---

## ⚡ Quick Start (Local Dev)

### Prerequisites
- Docker Desktop
- Python 3.11+
- Node.js 20+

### 1. Clone and configure
```bash
git clone https://github.com/your-org/enterprise-api-analytics.git
cd enterprise-api-analytics
cp .env.example .env
# Edit .env with your settings
```

### 2. Start with Docker Compose
```bash
docker-compose up --build
```

### 3. Run database migrations
```bash
make migrate
```

### 3b. Seed demo data (optional, recommended)
A fresh system has no telemetry, so ML training will fail with "not enough
historical data" until something is ingested. Seed realistic historical
traffic (with injected incidents) to try forecasting/health/anomalies immediately:
```bash
make seed            # 30 days, 3 demo APIs
make seed DAYS=14 APIS=1
```
See [`docs/ml-approach.md`](docs/ml-approach.md) for what's simulated and why.

### 4. Access the platform
| Service | URL |
|---------|-----|
| API Docs (Swagger) | http://localhost:8000/docs |
| Frontend Dashboard | http://localhost:5173 |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |

---

## 🛠️ Development

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run backend dev server
make dev-backend

# Install frontend dependencies
cd frontend
npm install

# Run frontend dev server
make dev-frontend

# Run all tests
make test

# Run linting
make lint
```

---

## 🐳 Docker

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down
```

---

## ☸️ Kubernetes Deployment

```bash
# Apply base manifests
kubectl apply -k k8s/overlays/dev/

# Or use Helm
helm upgrade --install api-analytics ./helm/api-analytics \
  --namespace api-analytics \
  --create-namespace \
  -f helm/api-analytics/values.yaml
```

---

## 📊 API Endpoints (Key)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Get JWT token pair |
| GET | `/users/me` | Current user profile |
| GET/POST | `/apis` | List / register APIs |
| POST | `/telemetry/ingest` | Ingest request logs |
| GET | `/analytics/latency` | Latency percentiles |
| GET | `/analytics/errors` | Error rates |
| GET | `/health/apis` | All API health scores |
| POST | `/forecast/train` | Train ML model |
| GET | `/forecast/{api_id}` | Get traffic prediction |
| WS | `/dashboard/realtime` | Live metric stream |

Full API reference: [docs/api-reference.md](docs/api-reference.md)

---

## 📁 Project Structure

```
enterprise-api-analytics/
├── backend/          # FastAPI application
├── frontend/         # React + Vite dashboard
├── migrations/       # Alembic DB migrations
├── tests/            # Unit + Integration tests
├── k8s/              # Kubernetes manifests
├── helm/             # Helm chart
├── .github/          # GitHub Actions CI/CD
├── monitoring/       # Prometheus + Grafana config
└── docs/             # Architecture & API docs
```

---

## 🤝 Contributing

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'feat: add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
