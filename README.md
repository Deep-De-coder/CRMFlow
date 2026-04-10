# SalesforceSync

A Python REST service integrating with Salesforce APIs via [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce).
Manages **Accounts**, **Contacts**, **Opportunities**, and **Cases** with full CRUD endpoints.

## Stack

- **FastAPI** — REST framework with automatic OpenAPI docs
- **simple-salesforce** — Salesforce REST API client
- **Pydantic v2** — request/response validation
- **pytest** — unit and integration test suite
- **Docker** — containerized deployment

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your Salesforce credentials
```

Required variables:

| Variable            | Description                              |
|---------------------|------------------------------------------|
| `SF_USERNAME`       | Salesforce login email                   |
| `SF_PASSWORD`       | Salesforce password                      |
| `SF_SECURITY_TOKEN` | Security token (from profile settings)   |
| `SF_DOMAIN`         | `login` for production, `test` for sandbox |

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Docker

```bash
docker build -t salesforce-sync .
docker run -p 8000:8000 \
  -e SF_USERNAME=you@example.com \
  -e SF_PASSWORD=yourpassword \
  -e SF_SECURITY_TOKEN=yourtoken \
  salesforce-sync
```

## API Endpoints

### Accounts

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/accounts/`            | List accounts            |
| GET    | `/accounts/search`      | Search by name           |
| GET    | `/accounts/{id}`        | Get account by ID        |
| POST   | `/accounts/`            | Create account           |
| PATCH  | `/accounts/{id}`        | Update account           |
| DELETE | `/accounts/{id}`        | Delete account           |

### Contacts

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/contacts/`            | List contacts            |
| GET    | `/contacts/{id}`        | Get contact by ID        |
| POST   | `/contacts/`            | Create contact           |
| PATCH  | `/contacts/{id}`        | Update contact           |
| DELETE | `/contacts/{id}`        | Delete contact           |

### Opportunities

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | `/opportunities/`           | List opportunities           |
| GET    | `/opportunities/pipeline`   | Pipeline summary by stage    |
| GET    | `/opportunities/{id}`       | Get opportunity by ID        |
| POST   | `/opportunities/`           | Create opportunity           |
| PATCH  | `/opportunities/{id}`       | Update opportunity           |
| DELETE | `/opportunities/{id}`       | Delete opportunity           |

### Cases

| Method | Path              | Description       |
|--------|-------------------|-------------------|
| GET    | `/cases/`         | List cases        |
| GET    | `/cases/{id}`     | Get case by ID    |
| POST   | `/cases/`         | Create case       |
| PATCH  | `/cases/{id}`     | Update case       |
| DELETE | `/cases/{id}`     | Delete case       |

### Query Parameters

**Accounts:** `?industry=Technology&limit=50&offset=0`

**Contacts:** `?account_id=001ABC&limit=50&offset=0`

**Opportunities:** `?stage=Prospecting&account_id=001ABC&is_closed=false&limit=50&offset=0`

**Cases:** `?status=New&priority=High&account_id=001ABC&limit=50&offset=0`

## Running Tests

```bash
# All tests
pytest

# Unit tests only (no Salesforce connection needed)
pytest -m unit

# Integration tests only
pytest -m integration

# With coverage report
pytest --cov=app --cov-report=html
```

## Project Structure

```
salesforce-sync/
├── app/
│   ├── config.py           # Pydantic settings from environment
│   ├── main.py             # FastAPI app, router registration
│   ├── models/             # Pydantic request/response models
│   ├── services/           # Business logic, SOQL, field mapping
│   │   └── base.py         # Shared CRUD helpers
│   ├── salesforce/
│   │   ├── client.py       # SalesforceClient wrapper
│   │   └── exceptions.py   # Typed error hierarchy
│   └── routers/            # FastAPI route handlers
└── tests/
    ├── conftest.py         # Shared fixtures and sample records
    ├── unit/               # Service-layer tests (mocked SF)
    └── integration/        # API-layer tests (mocked SF client)
```
