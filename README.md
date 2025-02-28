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

- Use `alembic` for database migrations
- Unit tests are in the `tests` directory
- Follow PEP 8 coding style

## Directory Structure

See [project_structure.md](project_structure.md)
