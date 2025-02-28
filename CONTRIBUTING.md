# Contributing to SingSi.AI

Thank you for your interest in contributing to SingSi.AI! This document provides guidelines and instructions for contribution.

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- PostgreSQL (for local development)
- Redis (for async tasks)

### Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd singsi
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
# Install both production and development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Code Style

We use **[Ruff](https://docs.astral.sh/ruff/)** for code formatting and linting. Configuration is in `pyproject.toml`:

- Line length: 88 characters
- Quote style: single quotes
- Import sorting: following isort rules

```bash
# Check and fix code style
ruff check --fix .      # Fix lint issues
ruff format .          # Format code

# Check specific file
ruff check path/to/file.py
```

### 2. Pre-commit Hooks

Every commit is automatically checked using pre-commit hooks:

```bash
# Run checks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Update hooks
pre-commit autoupdate
```

The hooks will:
1. Check code style with Ruff
2. Format code with Ruff formatter
3. Verify formatting

If checks fail:
1. Review error messages
2. Fix the issues
3. Stage changes and retry commit

### 3. Testing

We use **[PyTest](https://docs.pytest.org/en/stable/)** for testing. Tests are organized into three categories:

- **Unit Tests**: Testing individual components
- **Integration Tests**: Testing component interactions
- **Functional Tests**: Testing API endpoints

```bash
# Run specific test categories
pytest tests/unit -v         # Run unit tests
pytest tests/integration -v  # Run integration tests
pytest tests/functional -v   # Run functional tests

# Run tests by markers
pytest -v -m unit        # Run all unit tests
pytest -v -m integration # Run all integration tests
pytest -v -m functional  # Run all functional tests

# Run all tests
pytest -v

# Run with coverage report
pytest -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/unit/services/test_document_service.py -v

# Run tests matching a pattern
pytest -v -k "document"  # Run all tests with "document" in the name
```

Test files should use appropriate markers:
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_something():
    # ...

@pytest.mark.integration
def test_integration():
    # ...

@pytest.mark.functional
def test_api():
    # ...
```

### 4. Database Management

We use **[Alembic](https://alembic.sqlalchemy.org/en/latest/)** for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "describe changes"

# Apply migrations
alembic upgrade head                # Apply all migrations
alembic upgrade +1                  # Apply next migration
alembic downgrade -1                # Rollback last migration
```

## Branch Strategy

We follow **[GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)**:

1. Branch from `develop`:
```bash
git checkout develop
git pull
git checkout -b feature/your-feature
```

2. Make changes and commit regularly
3. Push and create PR to `develop`
4. After review and tests pass, merge to `develop`

## Pull Request Guidelines

1. Ensure PR description clearly explains the changes
2. Update documentation if needed
3. Add tests for new features
4. Ensure all checks pass:
   - Ruff style checks
   - Tests
   - Type checks
5. Obtain code review approval

## Getting Help

- Check [existing issues](https://github.com/qavit/singsi/issues)
- ~~Join our [Discord community](#)~~
- Read our [documentation](docs/)

## Project Structure

See [project_structure.md](docs/project_structure.md) for detailed information about the codebase organization.
