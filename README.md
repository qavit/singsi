# SingSi AI Backend

## Introduction

*(TBA)*


## Project Architecture

This project uses FastAPI to build a backend service, providing:

- AI Text Processing Service
- AI Image Generation Service
- User Authentication & Authorization
- Asynchronous Task Processing

## Technology Stack

- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **AI/ML**: Langchain?
- **Async Tasks**: Celery + Redis

## Getting Started

### Environment Setup

1. Clone repository:

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
pip install -r requirements.txt
```

4. Create .env file (refer to .env.example)

### Running the Application

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to view API documentation

## Development Guide

### Setup Development Environment

1. Install both production and development dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

- Use `alembic` for database migrations
- Unit tests are in the `tests` directory
- Follow PEP 8 coding style

### Code Style Guide

We use several tools to maintain code quality:

- **black**: Code formatting (max line length: 88)
- **isort**: Import sorting (follows black profile)
- **flake8**: Style guide enforcement
- **mypy**: Static type checking

Run formatters manually:
```bash
# Format code
black .
isort .

# Check code
flake8 .
mypy app

# Run all checks
pre-commit run --all-files
```

### Branch Strategy

We follow [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow):
1. Create feature branches from `develop`
2. Submit pull requests to `develop`
3. After review and testing, merge to `develop`
4. Periodically merge `develop` to `main` for releases

### Getting Started with Development

1. Clone the repository
2. Switch to develop branch:
```bash
git checkout develop
```
3. Create a new feature branch:
```bash
git checkout -b feature/your-feature-name
```
4. Make your changes and commit
5. Push and create PR to develop branch

## Directory Structure

See [project_structure.md](project_structure.md)
