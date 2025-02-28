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

## Technology Stack

- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **AI/ML**: Langchain + OpenAI
- **Async Tasks**: Celery + Redis

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

Visit http://localhost:8000/docs for API documentation.

## Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [Project Structure](docs/project_structure.md)
- [API Documentation](docs/api.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
