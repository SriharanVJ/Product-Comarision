# QuickCommerce Comparison Platform

A production-quality web application for comparing grocery/quick-commerce products across multiple platforms in India — search a product once and see prices from Blinkit, Zepto and Swiggy Instamart side by side.

The stack is developed as a FastAPI backend that queries the QuickCommerce API, normalizes the product/price data and exposes it through its own search endpoints, plus a TanStack Start (React + Vite) frontend — the `app-price-whiz` app — wired to the backend through a hot-reload dev proxy (`/api`). A Makefile + Docker Compose workflow (backend, frontend with a persistent node_modules volume) orchestrates the whole stack — API docs included — so it starts with one command.

## 🚀 Getting started

### Run with Docker (recommended)

```bash
# 0. Clone the frontend app (lives in its own repo, referenced as app-price-whiz/)
git clone https://github.com/SriharanVJ/app-price-whiz.git app-price-whiz   # skip if already present

# 1. Configure the backend (QuickCommerce API key)
cd backend
cp .env.example .env
# Edit .env and replace QUICKCOMMERCE_API_KEY=your_api_key_here with your actual key
cd ..

# 2. Build & start backend + frontend
docker compose up --build -d        # or: make docker-up
docker compose logs -f              # follow logs (or: make docker-logs)
```

| Service  | URL                              |
| -------- | -------------------------------- |
| Frontend | http://localhost:5173            |
| API      | http://localhost:8000 (docs at `/docs`) |

Stop with `docker compose down` (or `make docker-down`).

### Run locally (without Docker)

```bash
make setup          # install deps for backend + app-price-whiz
make dev            # run backend (:8000) + frontend (:5173) together in one terminal
```

Or individually: `make backend`, `make whiz`.

## ✅ Verify the QuickCommerce API integration (PHASE 1 test)

This test verifies the QuickCommerce API integration works correctly:

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run the test
python test_quickcommerce_api.py
```

The test will:
- ✅ Verify API authentication
- ✅ Test the group search endpoint
- ✅ Search for "milk" in Chennai
- ✅ Fetch results from BlinkIt, Zepto, and Swiggy
- ✅ Display safe, summarized results (no API keys exposed)

### Expected Output

```
============================================================
QuickCommerce API Integration Test - PHASE 1
============================================================

🔍 Searching for: 'milk'
📍 Location: (13.0827, 80.2707)
🛒 Platforms: BlinkIt, Zepto, Swiggy

📦 BlinkIt Results:
   ✅ Amul Taaza Toned Milk 500ml
      Price: ₹28
      Delivery: 10 min
   ...

📊 TEST SUMMARY
============================================================
Total products found: 15
  BlinkIt: 5 products
  Zepto: 6 products
  Swiggy: 4 products

✅ PHASE 1 TEST PASSED!
```

## 🏗️ Project Architecture

```
User
|
v
TanStack Start Web Application (app-price-whiz)
|
v  /api dev proxy
FastAPI Backend
|
+-------------------+
|                   |
v                   v
Redis             PostgreSQL
|
v
QuickCommerce API
|
+-------------+-------------+
|             |             |
v             v             v
Blinkit       Zepto       Swiggy Instamart
```

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── api/
│   │   │   └── routes/           # API endpoints
│   │   ├── core/                 # Configuration, logging
│   │   ├── clients/              # External API clients
│   │   ├── services/             # Business logic
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── db/                   # Database setup
│   │   └── cache/                # Redis cache
│   ├── tests/                    # Test suite
│   ├── requirements.txt
│   └── .env                      # Environment variables (not in Git)
├── app-price-whiz/               # TanStack Start frontend (Vite)
├── Makefile                      # build & run commands
└── docker-compose.yml             # Full stack deployment
```

## 🔐 Security Notes

- **NEVER** commit `.env` to Git
- **NEVER** expose API keys in frontend code
- **NEVER** log API keys in output
- All external API calls happen on the backend
- API keys are loaded via environment variables only

## 📋 Development Phases

- ✅ **PHASE 1**: QuickCommerce API integration test
- ⏳ **PHASE 2**: Product normalization
- ⏳ **PHASE 3**: Product matching
- ⏳ **PHASE 4**: Price comparison
- ⏳ **PHASE 5**: Search API endpoint
- ⏳ **PHASE 6**: Redis caching
- ⏳ **PHASE 7**: PostgreSQL integration
- ⏳ **PHASE 8**: Next.js frontend
- ⏳ **PHASE 9**: Frontend-backend integration
- ⏳ **PHASE 10**: UX improvements
- ⏳ **PHASE 11**: Docker Compose setup
- ⏳ **PHASE 12**: Tests and documentation

## 🛠️ Technology Stack

### Frontend
- TanStack Start (React + Vite)
- TypeScript
- Tailwind CSS

### Backend
- Python
- FastAPI
- Pydantic
- httpx
- Async/await

### Database & Cache
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis

### Infrastructure
- Docker
- Docker Compose

## 📚 Sources

- [QuickCommerce API Documentation](https://quickcommerceapi.com/docs)
