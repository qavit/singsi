# SingSi.AI Backend

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Maintainer](https://img.shields.io/badge/maintainer-qavit-yellow)
![Status](https://img.shields.io/badge/status-alpha-orange)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

## Introduction

**SingSi.AI** is an intelligent teaching assistant system that revolutionizes educational experiences through AI-powered tools. Our platform helps teachers streamline their workflow by:

- Automating lesson plan creation from teaching materials
- Generating personalized assignments and assessments
- Providing real-time feedback and grading
- Offering data-driven insights into student performance

Built with modern cloud-native technologies and state-of-the-art AI models, SingSi.AI aims to enhance teaching efficiency while delivering personalized learning experiences at scale.

## Current Implementation Status

- **AI Service Layer**: ✅ Modular AI service architecture supporting multiple providers (backend only)
- **Document Management**: ✅ Basic upload, storage and retrieval of educational materials
- **Document Analysis**: 🔄 Initial document passing to AI (no real document parsing yet)
- **Image Processing**: 📝 Framework only, functionality not implemented
- **API Endpoints**: ✅ Initial RESTful API with Swagger documentation
- **Database Integration**: ✅ PostgreSQL integration with SQLAlchemy models
- **Frontend Interface**: 🔄 Basic informational frontend only
- **Prompt Management**: ✅ Flexible templating system with variable substitution and versioning

### Not Yet Implemented:

- ❌ Advanced document content extraction
- ❌ Actual image analysis
- ❌ Educational material generation
- ❌ Learning analytics & dashboards
- ❌ Assessment generation system
- ❌ Adaptive learning features
- ❌ User authentication & authorization
- ❌ Comprehensive frontend interface

## Technology Stack

- **Web Framework**: FastAPI with Async support
- **ORM**: SQLAlchemy (Async)
- **Database**: PostgreSQL
- **AI Integration**:
  - OpenAI (primary)
  - Support for Gemini, Claude, DeepSeek (planned)
- **Design Patterns**: Factory Pattern, Dependency Injection, Strategy Pattern
- **Documentation**: OpenAPI/Swagger, ReDoc

## Project Architecture

The project follows SOLID principles with a clean separation of concerns:
- Abstract interfaces define capabilities (e.g., `AIService`)
- Concrete implementations provide specific functionality (e.g., `OpenAIService`)
- Factory modules handle object creation and dependency injection
- Configuration is centralized and strongly typed using Pydantic

## Quick Start

1. Clone and setup:
```bash
git clone <repository-url>
cd singsi
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Create `.env` file (see `.env.example`)

3. Run the application:
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000 for home page or http://localhost:8000/docs for API documentation (Swagger UI).

## Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Documentation

- [Product Requirements Document](docs/PRD_en.md)
- [Design Proposals](docs/design_proposals_en.md)
- [Project Structure](docs/project_structure_en.md)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
