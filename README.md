# POS E-Commerce Backend API

A sample scalable GraphQL-based backend for a POS-integrated e-commerce platform with payment methods, transactions creation, and sales report.

## Overview

This system manages payment processing with dynamic price rates and points modifiers. Compatible to handle high concurrency and easily extend with new payment methods without code changes.

**Key Features:**

- **GraphQL API** - Queries and mutations for payment processing and reporting
- **Configurable Payment Methods** - Add/edit payment methods via database with custom `additional_item_schema` (JSON Schema validation)
- **Transaction Processing** - Process payments with dynamic price modifiers and points calculation
- **Sales Reporting** - Per period aggregated sales (hour, day, week, month) and points data with date range filtering
- **Redis Caching** - Payment method cached
- **Full Test Coverage** - Unit and integration tests

## Project Structure

The project uses combining layered structure (models, services, graphql, REST) with domain-based modules within each layer. Try to balance technical separation with business logic grouping

```
pos-app-backend/
├── src/
│   ├── api/
│   │   ├── graphql/                 # GraphQL layer
│   │   │   ├── schema.py            # Top-level schema aggregator
│   │   │   ├── queries.py           # Root queries
│   │   │   ├── mutations.py         # Root mutations
│   │   │   └── payment/             # Payment domain
│   │   │       ├── queries.py       # Payment-specific queries
│   │   │       ├── mutations.py     # Payment-specific mutations
│   │   │       └── dto/             # Data transfer objects
│   │   │           ├── inputs.py    # Input types
│   │   │           └── outputs.py   # Output types
│   │   │     # Future domains: user/, sales/ etc.
│   │   │
│   │   ├── services/                # Business logic layer
│   │   │   └── payment/             # Payment services
│   │   │       ├── payment_service.py
│   │   │       ├── payment_method_service.py
│   │   │       └── report_service.py
│   │   │     # Future services: user/, sales/ etc.
│   │   │
│   │   ├── models/                  # Database models
│   │   │   ├── base.py              # Base model class
│   │   │   └── payment/             # Payment domain models
│   │   │       ├── payment_method.py
│   │   │       └── transaction.py
│   │   │     # Future models: user/, sales/ etc.
│   │   │
│   │   ├── controllers/             # REST controllers (Currently not being used)
│   │   └── schemas/                 # Pydantic schemas (Plan to use with REST but currently only stored cache schemas)
│   │
│   ├── config/                      # App configuration, database, settings
│   ├── shared/                      # Cross-domain utilities
│   ├── alembic/                     # Database migrations
│   └── tests/
│       ├── conftest.py              # Shared test fixtures & configuration
│       ├── fixtures/                # Test data fixtures
│       ├── unit/payment/            # Domain-specific unit tests
│       └── integration/payment/     # Domain-specific integration tests
```

### Reason choosing this structure

1. **Domain Isolation** - Each business domain is self-contained and independent
2. **Team Scalability** - Multiple devs can work on different domains without conflicts
3. **Clear Boundaries** - Easy to understand what code belongs where, related code lives together (queries, mutations, services, models)
4. **Testability** - Test each domain in isolation
5. **Maintainability** - Changes to payment logic don't affect order logic

### Example Process Flow

```
GraphQL Request
    ↓
payment/queries.py or payment/mutations.py
    ↓
payment/payment_service.py (business logic)
    ↓
payment/payment_method.py (database model)
    ↓
PostgreSQL Database
```

## Tech Stack

| Category         | Technology              |
| ---------------- | ----------------------- |
| **Framework**    | FastAPI + Uvicorn       |
| **GraphQL**      | Strawberry              |
| **Database**     | PostgreSQL.             |
| **ORM**          | SQLAlchemy              |
| **Migrations**   | Alembic                 |
| **Cache**        | Redis                   |
| **Container**    | Docker + Docker Compose |
| **Testing**      | Pytest + pytest-asyncio |
| **Code Quality** | Ruff (linter/formatter) |

## How to Start

### Prerequisites

- Docker
- Git

### 1. Clone & Setup

```bash
git clone git@github.com:suwannachatkul/pos-app-backend.git
cd pos-app-backend
cp .env.example .env
```

### 2. Start Services

```bash
# Start all services (API, PostgreSQL, Redis)
make dev

# Or manually
docker-compose up -d
```

The API will be available at:

- **GraphQL Playground**: http://localhost:8000/graphql
- **REST Docs**: http://localhost:8000/docs

### 3. Database Migrations

Migrations run automatically on startup ([entrypoint.sh](./scripts/entrypoint.sh)) for ease of running this project without extra commands, but you can also manually run:

```bash
# Create new migration
make db-migrate message="add payment methods table"

# Apply migrations
make db-upgrade

# Rollback
make db-downgrade
```

## Testing

```bash
# Run all tests
make test

# Lint code
make lint
```

Tests use an isolated PostgreSQL instance (`postgres_test`) to avoid affecting development data.

## API Usage

### GraphQL Examples

#### Process Payment Mutation

**Case 1: No Additional Item**

```graphql
mutation {
  processPayment(
    input: {
      customerId: 1234
      price: 1000
      priceModifier: 1.0
      paymentMethod: "CASH"
      datetime: "2022-09-01T04:00:00Z"
    }
  ) {
    ... on PaymentResult {
      finalPrice
      points
    }
  }
}
```

Response:

```json
{
  "data": {
    "processPayment": {
      "finalPrice": 1000,
      "points": 50
    }
  }
}
```

**Case 2: With last4 (Credit Card)**

```graphql
mutation {
  processPayment(
    input: {
      customerId: 1234
      price: 1000
      priceModifier: 1.0
      paymentMethod: "VISA"
      datetime: "2022-09-01T04:00:00Z"
      additionalItem: { last4: "3333" }
    }
  ) {
    ... on PaymentResult {
      finalPrice
      points
    }
  }
}
```

Response:

```json
{
  "data": {
    "processPayment": {
      "finalPrice": 1000,
      "points": 50
    }
  }
}
```

**Case 3: With Courier**

```graphql
mutation {
  processPayment(
    input: {
      customerId: 1234
      price: 1000
      priceModifier: 1.0
      paymentMethod: "COD"
      datetime: "2022-09-01T04:00:00Z"
      additionalItem: { courier: "Kerry Express" }
    }
  ) {
    ... on PaymentResult {
      finalPrice
      points
    }
  }
}
```

Response:

```json
{
  "data": {
    "processPayment": {
      "finalPrice": 1000,
      "points": 50
    }
  }
}
```

**Case 4: With Bank and Account Number**

```graphql
mutation {
  processPayment(
    input: {
      customerId: 1234
      price: 1000
      priceModifier: 1.0
      paymentMethod: "BANK_TRANSFER"
      datetime: "2022-09-01T04:00:00Z"
      additionalItem: { bank: "SCB", account_number: "1234567890" }
    }
  ) {
    ... on PaymentResult {
      finalPrice
      points
    }
  }
}
```

Response:

```json
{
  "data": {
    "processPayment": {
      "finalPrice": 1000,
      "points": 50
    }
  }
}
```

**Case 5: Error Handling - Invalid Additional Item**

```graphql
mutation ErrorTest {
  processPayment(
    input: {
      customerId: 1234
      price: 1000
      priceModifier: 1.0
      paymentMethod: "CASH_ON_DELIVERY"
      datetime: "2022-09-01T04:00:00Z"
      additionalItem: { courier: "TEST" }
    }
  ) {
    ... on PaymentResult {
      finalPrice
      points
    }
    ... on GraphQLError {
      details
      code
      message
    }
  }
}
```

Response:

```json
{
  "data": {
    "processPayment": {
      "details": null,
      "code": "INVALID_INPUT",
      "message": "Invalid additional data for CASH_ON_DELIVERY: 'TEST' is not one of ['YAMATO', 'SAGAWA']"
    }
  }
}
```

#### Query Sales Report

```graphql
query {
  salesReport(
    startDatetime: "2022-09-01T00:00:00Z"
    endDatetime: "2022-09-01T03:00:00Z"
  ) {
    datetime
    points
    sales
  }
}
```

Response:

```json
{
  "data": {
    "salesReport": [
      {
        "datetime": "2022-09-01T00:00:00",
        "points": 340,
        "sales": 8000
      },
      {
        "datetime": "2022-09-01T01:00:00",
        "points": 200,
        "sales": 6000
      },
      {
        "datetime": "2022-09-01T02:00:00",
        "points": 0,
        "sales": 0
      },
      {
        "datetime": "2022-09-01T03:00:00",
        "points": 0,
        "sales": 2000
      }
    ]
  }
}
```

#### Query Available Payment Methods

```graphql
query {
  availablePaymentMethods {
    id
    name
    minModifier
    maxModifier
    pointsModifier
    additionalItemSchema
  }
}
```

Response:

```json
{
  "data": {
    "availablePaymentMethods": [
      {
        "id": "1",
        "name": "CASH",
        "minModifier": 0.9,
        "maxModifier": 1,
        "pointsModifier": 0.05,
        "additionalItemSchema": null
      },
      {
        "id": "2",
        "name": "VISA",
        "minModifier": 0.95,
        "maxModifier": 1,
        "pointsModifier": 0.03,
        "additionalItemSchema": {
          "type": "object",
          "required": ["last4"],
          "properties": {
            "last4": {
              "type": "string",
              "pattern": "^[0-9]{4}$",
              "description": "Last 4 digits of card"
            }
          }
        }
      }
      .
      .
      .
    ]
  }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

Automated CI pipeline runs on pull request:

**Pipeline Steps:**

1. **Code Linting** - Ruff checks code quality and formatting
2. **Unit & Integration Tests** - Pytest with PostgreSQL test database
3. **Coverage Report** - Automated coverage comments on PRs

**(Optional) Pre-commit Hooks:**

- Ruff auto-formatting and linting
- Validate JSON, YAML, TOML files
- Spell checking with codespell

**Setup Pre-commit:**

```bash
pip install pre-commit
pre-commit install
```

## Scaling Considerations

### Vertical Scaling (Current Implementation)

**Already Implemented:**

1. **Async I/O** - All database operations use `async`/`await` with SQLAlchemy AsyncSession
2. **Redis Caching** - Payment methods cached, ready to extend caching to other read-heavy data.
3. **Connection Pooling** - SQLAlchemy async engine with connection pool (default: 5 connections)
4. **Non-blocking Operations** - GraphQL resolvers run on FastAPI + Uvicorn

**Additional Optimizations Available:**

1. **Database Connection Pool Tuning** (Configurable via environment variables)

   ```bash
   # Edit .env
   DATABASE_POOL_SIZE=20        # Max connections in pool (default: 5)
   DATABASE_MAX_OVERFLOW=10     # Additional connections (default: 10)
   ```

2. **Uvicorn Workers** (Production)

   ```bash
   # Update entrypoint.sh for production
   uvicorn api.app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Redis Connection Pool** (Configurable via environment variables)

   ```bash
   # Edit .env
   REDIS_POOL_SIZE=50           # Max connections in pool (default: 50)
   REDIS_POOL_TIMEOUT=1         # Connection timeout in seconds (default: 1)
   ```

4. **Query Optimization**

   - Add indexes on expected to be frequently queried columns
     - PaymentMethod (`name`)
     - Transaction (`customer_id`, `datetime`, `payment_method`)
   - Use `selectinload()` for relationship loading instead of lazy loading
   - No Lazy loading used in PaymentMethod models to avoid N+1 issues

### Horizontal Scaling

**Current Setup:**

- Stateless API design (no local state stored in API server)
- Shared PostgreSQL for data persistence
- Redis for distributed caching (Can be shared across instances)

## Future Update if possible

- More tests (services unit tests not being implement, more test cases/fixtures)
- Centralize Error with error translation/localization
- Hashing sensitive data in additional items (e.g., card last4, bank account number, etc.)
- Update/Add/Delete payment methods (Maybe REST?)
- Authentication & Authorization (JWT, OAuth)
- More customizable sales reports (filter/group by payment method, customer, etc.)
- Limit sales report query range (e.g., max 1 month, max transactions)
- Cache strategy for transactions/sales reports (Is it worth caching?)
- Integration with other services (external payment gateways, customer management)
- Currency support & conversion
