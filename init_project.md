# FastAPI + GraphQL Backend - Project Initialization Guide

## Project Overview

This is a production-ready FastAPI backend application with GraphQL API using Strawberry GraphQL. The project uses Docker Compose for orchestration with PostgreSQL as the database. REST endpoints are available for authentication and other HTTP-specific needs.

## Tech Stack

- **Framework**: FastAPI (0.115.7)
- **GraphQL**: Strawberry GraphQL (0.245.3)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0.32
- **Database Migrations**: Alembic 1.13.2
- **Database Driver**: psycopg 3.2.1
- **Python Version**: 3.13
- **Container**: Docker with Python 3.13 runtime

## Project Structure

```
backend-fastapi-graphql/
├── docker-compose.yml           # Docker orchestration (postgres, postgres_test, api)
├── Dockerfile                   # Container definition
├── Makefile                     # Development & test commands
├── pyproject.toml              # Ruff + pytest configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template (incl. test DB)
├── README.md                  # Project documentation
│
├── data/                      # Persistent data directory
│   └── logs/                 # Application logs
│       └── api/              # API logs
│
├── scripts/
│   └── entrypoint.sh         # Container startup script
│
├── tests/                    # Pytest tests
│   ├── conftest.py           # Test DB engine + app overrides
│   ├── test_api/
│   │   └── test_health.py    # REST health check test
│   └── test_graphql/
│       └── test_queries.py   # GraphQL hello/health tests
│
└── src/                      # Source code
    ├── __init__.py
    ├── alembic.ini           # Alembic configuration
    │
    ├── api/                  # FastAPI + GraphQL application
    │   ├── __init__.py
    │   ├── app.py           # Main FastAPI application
    │   ├── graphql/         # GraphQL schema and resolvers
    │   │   ├── __init__.py
    │   │   ├── schema.py    # Main GraphQL schema
    │   │   ├── queries.py   # GraphQL queries
    │   │   └── mutations.py # GraphQL mutations
    │   ├── controllers/     # REST API controllers
    │   │   └── __init__.py
    │   ├── helpers/
    │   │   ├── __init__.py
    │   │   ├── error_handler.py    # Exception handler
    │   │   └── exceptions.py       # Custom exceptions
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── base.py             # SQLAlchemy Base model
    │   ├── routers/                # REST API routes (auth, etc.)
    │   │   └── __init__.py
    │   └── schemas/                # Pydantic schemas
    │       └── __init__.py
    │
    ├── config/              # Configuration modules
    │   ├── __init__.py
    │   ├── settings.py             # Application settings (Pydantic)
    │   └── database.py             # Database session management
    │
    ├── shared/              # Shared utilities
    │   └── logging.py              # Logging configuration
    │
    └── alembic/             # Database migrations
        ├── env.py                  # Alembic environment
        ├── script.py.mako          # Migration template
        └── versions/               # Migration files
```

## Step-by-Step Setup Instructions

### 1. Create Project Directory Structure

```bash
mkdir -p backend-fastapi-graphql/{data/logs/api,scripts,src}
cd backend-fastapi-graphql
```

### 2. Create Docker Configuration

#### docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    restart: always
    environment:
      POSTGRES_DB: ${DATABASE_NAME:-app_db}
      POSTGRES_USER: ${DATABASE_USERNAME:-app_user}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD:-app_password}
    ports:
      - "${POSTGRES_EXT_PORT:-5432}:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - default
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USERNAME:-app_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Isolated database for running tests safely
  postgres_test:
    image: postgres:16-alpine
    container_name: postgres_test
    restart: always
    environment:
      POSTGRES_DB: ${DATABASE_TEST_NAME:-app_db_test}
      POSTGRES_USER: ${DATABASE_TEST_USERNAME:-app_user}
      POSTGRES_PASSWORD: ${DATABASE_TEST_PASSWORD:-app_password}
    ports:
      - "${POSTGRES_TEST_EXT_PORT:-55432}:5432"
    volumes:
      - postgres-test-data:/var/lib/postgresql/data
    networks:
      - default
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_TEST_USERNAME:-app_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: api
    working_dir: /src
    volumes:
      - ./src:/src:rw
      - ./data:/data:rw
    ports:
      - ${API_EXT_PORT:-8000}:8000
    env_file:
      - .env
    command: bash -c "entrypoint.sh"
    restart: always
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

volumes:
  postgres-data:
  postgres-test-data:
```

#### Dockerfile

```dockerfile
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV LANGUAGE=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src /src
COPY ./scripts /scripts/

RUN chmod +x /scripts/entrypoint.sh

ENV PATH="/scripts:${PATH}"

WORKDIR /src
```

### 3. Create Python Dependencies

#### requirements.txt

```
# Core Framework
fastapi[all]==0.115.7
uvicorn[standard]==0.32.1

# GraphQL
strawberry-graphql[fastapi]==0.245.3

# Database
SQLAlchemy==2.0.32
psycopg[binary]==3.2.1
alembic==1.13.2

# Configuration
pydantic>=2.8.2
pydantic-settings>=2.5.2

# Development Tools
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.28.1
ruff==0.8.4
pre-commit==4.0.1
ipython==8.31.0
```

### 4. Create Configuration Files

#### .env.example

```env
# Application Configuration
ENVIRONMENT=development
API_EXT_PORT=8000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# PostgreSQL Configuration
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=app_db
DATABASE_USERNAME=app_user
DATABASE_PASSWORD=app_password
POSTGRES_EXT_PORT=5432

# Test PostgreSQL Configuration
DATABASE_TEST_HOST=postgres_test
DATABASE_TEST_PORT=5432
DATABASE_TEST_NAME=app_db_test
DATABASE_TEST_USERNAME=app_user
DATABASE_TEST_PASSWORD=app_password
POSTGRES_TEST_EXT_PORT=55432

# JWT Configuration (for future auth implementation)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

#### pyproject.toml

```toml
[tool.ruff]
line-length = 88
target-version = "py313"
exclude = ["alembic/versions"]

[tool.ruff.lint]
select = ["A", "C", "E", "F", "I", "RUF", "W", "UP"]
ignore = ["A001", "A002", "C901", "E501", "E712", "E741", "F821", "RUF012"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401", "F403", "F811"]

[tool.ruff.lint.isort]
lines-after-imports = 2

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

#### Makefile

```makefile
.PHONY: help dev test test-cov lint db-migrate db-upgrade db-downgrade clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development server
	docker-compose up --build

test: ## Run tests (brings up test DB)
	docker-compose up -d postgres_test
	docker-compose run --rm api pytest

test-cov: ## Run tests with coverage (brings up test DB)
	docker-compose up -d postgres_test
	docker-compose run --rm api pytest --cov=. --cov-report=html

lint: ## Run linter
	docker-compose run --rm api ruff check .

lint-fix: ## Run linter with auto-fix
	docker-compose run --rm api ruff check . --fix

db-migrate: ## Create a new migration (use message="description")
	docker-compose run --rm api alembic revision --autogenerate -m "$(message)"

db-upgrade: ## Apply migrations
	docker-compose run --rm api alembic upgrade head

db-downgrade: ## Rollback one migration
	docker-compose run --rm api alembic downgrade -1

clean: ## Clean up containers and volumes
	docker-compose down -v
```

### 5a. Testing Setup (Files to add)

Create the following test files to use the isolated test database and override the app's DB dependency during tests.

#### tests/conftest.py

```python
import contextlib
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.app import init_app
from api.models.base import Base
from config import settings
from config.database import get_sync_db as app_get_sync_db


@pytest.fixture(scope="session")
def test_engine():
    # Build test engine using settings from src/config
    engine = create_engine(settings.test_database_url, future=True)
    # Create tables if models exist
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        with contextlib.suppress(Exception):
            Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def app(db_session):
    app = init_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[app_get_sync_db] = override_get_db
    return app


@pytest.fixture()
def client(app) -> TestClient:
    return TestClient(app)
```

#### tests/test_api/test_health.py

```python
def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
```

#### tests/test_graphql/test_queries.py

```python
def test_graphql_queries(client):
    query = """
    query {
      hello
      health
    }
    """
    resp = client.post("/graphql", json={"query": query})
    assert resp.status_code == 200
    data = resp.json().get("data")
    assert data["hello"].startswith("Hello")
    assert "running" in data["health"]
```

### 5. Create Source Code Files

#### src/config/settings.py

```python
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    SRC_BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Database (main)
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str

    # Database (test)
    DATABASE_TEST_HOST: str = "postgres_test"
    DATABASE_TEST_PORT: int = 5432
    DATABASE_TEST_NAME: str = "app_db_test"
    DATABASE_TEST_USERNAME: str = "app_user"
    DATABASE_TEST_PASSWORD: str = "app_password"

    # JWT (for future auth)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def test_database_url(self) -> str:
        return f"postgresql+psycopg://{self.DATABASE_TEST_USERNAME}:{self.DATABASE_TEST_PASSWORD}@{self.DATABASE_TEST_HOST}:{self.DATABASE_TEST_PORT}/{self.DATABASE_TEST_NAME}"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

SettingsData = Annotated[Settings, Depends(get_settings)]
```

#### src/config/database.py

```python
from collections.abc import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import settings


# Sync engine (for Alembic migrations)
sync_engine = create_engine(settings.database_url)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine (for FastAPI/GraphQL)
async_engine = create_async_engine(
    settings.database_url.replace("postgresql+psycopg://", "postgresql+psycopg://"),
    echo=not settings.is_production,
    future=True,
)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Dependency for sync sessions (Alembic, testing)
def get_sync_db() -> Generator[Session, None, None]:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for async sessions (FastAPI, GraphQL)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### src/api/models/base.py

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

#### src/api/graphql/schema.py

```python
import strawberry
from strawberry.fastapi import GraphQLRouter

from .mutations import Mutation
from .queries import Query


# Create the main GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)


# Create the GraphQL router for FastAPI
def create_graphql_router() -> GraphQLRouter:
    return GraphQLRouter(schema, path="/graphql")
```

#### src/api/graphql/queries.py

```python
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        """A simple hello world query."""
        return "Hello from GraphQL!"

    @strawberry.field
    def health(self) -> str:
        """Health check query."""
        return "GraphQL API is running"
```

#### src/api/graphql/mutations.py

```python
import strawberry


@strawberry.type
class Mutation:
    @strawberry.mutation
    def placeholder(self) -> str:
        """Placeholder mutation - replace with your actual mutations."""
        return "Mutation placeholder"
```

#### src/api/app.py

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from api.graphql.schema import create_graphql_router
from config import settings
from shared.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.info("Initializing API with startup event")
        yield
    finally:
        logger.info("Shutting down API with shutdown event")


def init_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    app = FastAPI(
        title="Backend API with GraphQL",
        description="FastAPI + Strawberry GraphQL backend",
        version="1.0.0",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    # CORS configuration
    origins = [str(origin).strip("/") for origin in settings.CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint (REST)
    @app.get("/health", response_class=JSONResponse, status_code=status.HTTP_200_OK)
    def health() -> JSONResponse:
        return JSONResponse({"status": "healthy", "service": "backend-api"})

    # Root endpoint
    @app.get("/", response_class=JSONResponse, status_code=status.HTTP_200_OK)
    def root() -> JSONResponse:
        return JSONResponse(
            {
                "message": "Backend API is running",
                "graphql": "/graphql",
                "docs": "/docs" if not settings.is_production else None,
            }
        )

    # Include GraphQL router
    graphql_router = create_graphql_router()
    app.include_router(graphql_router)

    # Include REST routers (for auth, etc.)
    # from api.routers import auth
    # app.include_router(auth.router, prefix="/auth", tags=["auth"])

    return app


app = init_app()
```

#### src/api/helpers/exceptions.py

```python
from fastapi import HTTPException


class BadRequestException(HTTPException):
    """400 Bad Request"""
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(HTTPException):
    """401 Unauthorized"""
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    """403 Forbidden"""
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=403, detail=detail)


class NotFoundException(HTTPException):
    """404 Not Found"""
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(status_code=404, detail=detail)


class ConflictException(HTTPException):
    """409 Conflict"""
    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status_code=409, detail=detail)
```

#### src/api/helpers/error_handler.py

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
            }
        },
    )
```

#### src/shared/logging.py

```python
import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from uvicorn.logging import DefaultFormatter


def setup_logging() -> None:
    """Setup structured logging configuration."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s [%(name)s] %(message)s",
                    "use_colors": None,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {
                    "handlers": ["access"],
                    "level": "INFO",
                    "propagate": False,
                },
                "app": {"handlers": ["default"], "level": "INFO", "propagate": False},
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )


setup_logging()


@lru_cache
def get_logger() -> logging.Logger:
    return logging.getLogger("app")


logger = get_logger()

Logger = Annotated[logging.Logger, Depends(get_logger)]
```

#### scripts/entrypoint.sh

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting API server..."
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

#### src/alembic.ini

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
```

#### src/alembic/env.py

```python
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from api.models.base import Base
from config import settings

# Alembic Config object
config = context.config

# Setup Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### Create empty **init**.py files

```bash
touch src/__init__.py
touch src/api/__init__.py
touch src/api/controllers/__init__.py
touch src/api/graphql/__init__.py
touch src/api/helpers/__init__.py
touch src/api/models/__init__.py
touch src/api/routers/__init__.py
touch src/api/schemas/__init__.py
touch src/config/__init__.py
```

### 6. Initialize the Project

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env

# Make scripts executable
chmod +x scripts/entrypoint.sh

# Build and start containers
docker-compose up -d --build

# Check logs
docker-compose logs -f api

# Access GraphQL playground
open http://localhost:8000/graphql

# Start the isolated test database (optional: starts automatically in make test)
docker-compose up -d postgres_test
```

### 7. Verify Installation & Run Tests

```bash
# Check health endpoint
curl http://localhost:8000/health

# Access GraphQL playground
# Visit http://localhost:8000/graphql in your browser
# Try this query:
# query {
#   hello
#   health
# }

# View API documentation
open http://localhost:8000/docs

# Run all tests (ensures test DB is up)
make test

# Run with coverage
make test-cov

# Run specific test file directly
docker-compose up -d postgres_test
docker-compose run --rm api pytest tests/test_graphql/test_queries.py
```

## Key Features

### GraphQL with Strawberry

- **Type-safe**: Python type hints are used to define GraphQL types
- **Async Support**: Full async/await support for queries and mutations
- **Playground**: Built-in GraphQL playground for testing queries
- **Federation Ready**: Can be extended to support Apollo Federation

### Dual API Support

- **GraphQL**: For complex queries and data fetching
- **REST**: For authentication, file uploads, webhooks, etc.

### Database

- **PostgreSQL Only**: Production-ready database
- **Async SQLAlchemy**: Full async support for better concurrency
- **Type-safe ORM**: Using SQLAlchemy 2.0 style with type hints
- **Migrations**: Alembic for database version control

### Development Experience

- **Hot Reload**: Automatic reload on code changes
- **Type Checking**: Full type hints throughout codebase
- **Linting**: Ruff for fast Python linting
- **Testing**: pytest with async support

## Project Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│   API Layer (GraphQL + REST)       │  ← Entry points
├─────────────────────────────────────┤
│   Service Layer                     │  ← Business logic
├─────────────────────────────────────┤
│   Repository Layer                  │  ← Data access
├─────────────────────────────────────┤
│   Database Layer (PostgreSQL)       │  ← Persistence
└─────────────────────────────────────┘
```

### Pattern Recommendations

1. **Strategy Pattern**: For payment methods or different business rules
2. **Repository Pattern**: For database operations
3. **Dependency Injection**: Using FastAPI's `Depends()`
4. **DTO Pattern**: Using Strawberry types for GraphQL and Pydantic for REST

## Testing

### Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
docker-compose run --rm api pytest tests/test_example.py
```

### Test Structure

```
tests/
├── conftest.py              # Test DB + app overrides
├── test_graphql/
│   └── test_queries.py
└── test_api/
    └── test_health.py
```

## Common Issues and Solutions

### Issue: Database connection errors

**Solution**: Ensure PostgreSQL containers are healthy before starting API/tests. For tests, run `docker-compose up -d postgres_test` first or use `make test`.

### Issue: Port already in use

**Solution**: Change `API_EXT_PORT` in `.env` file or stop other services using port 8000

### Issue: GraphQL playground not loading

**Solution**: Ensure you're not in production mode (`ENVIRONMENT=development` in `.env`)

### Issue: Migrations fail

**Solution**:

1. Check database connection in `.env`
2. Ensure PostgreSQL is running: `docker-compose ps`
3. Check models are imported in `api/models/__init__.py`

## Environment Variables Reference

| Variable             | Description                          | Default       | Required |
| -------------------- | ------------------------------------ | ------------- | -------- |
| `ENVIRONMENT`        | Environment (development/production) | `development` | No       |
| `API_EXT_PORT`       | External API port                    | `8000`        | No       |
| `CORS_ORIGINS`       | Allowed CORS origins                 | -             | Yes      |
| `DATABASE_HOST`      | PostgreSQL host                      | `postgres`    | Yes      |
| `DATABASE_PORT`      | PostgreSQL port                      | `5432`        | Yes      |
| `DATABASE_NAME`      | PostgreSQL database name             | -             | Yes      |
| `DATABASE_USERNAME`  | PostgreSQL username                  | -             | Yes      |
| `DATABASE_PASSWORD`  | PostgreSQL password                  | -             | Yes      |
| `POSTGRES_EXT_PORT`  | External PostgreSQL port             | `5432`        | No       |
| `JWT_SECRET_KEY`     | Secret key for JWT tokens            | -             | Yes      |
| `JWT_ALGORITHM`      | JWT algorithm                        | `HS256`       | No       |
| `JWT_EXPIRE_MINUTES` | JWT expiration time                  | `30`          | No       |

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Strawberry GraphQL Documentation](https://strawberry.rocks/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)

---

**Created**: 2026-01-05  
**Version**: 1.0.0  
**Type**: Generic Boilerplate
