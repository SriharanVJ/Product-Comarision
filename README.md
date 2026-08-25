# QuickCommerce Comparison Platform

A production-quality web application for comparing grocery/quick-commerce products across multiple platforms in India.

## 🚀 PHASE 1: QuickCommerce API Integration Test

**Before running any tests, you need a QuickCommerce API key.**

### Getting Your API Key

1. Visit [QuickCommerce API](https://quickcommerceapi.com)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to `backend/.env`:

```bash
cd backend
cp .env.example .env
# Edit .env and replace QUICKCOMMERCE_API_KEY=your_api_key_here with your actual key
```

### Running PHASE 1 Test

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
Next.js Web Application
|
v
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
├── frontend/                     # Next.js application
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
- Next.js
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
