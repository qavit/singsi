# SingSi Project Structure

## Current Project Directory Layout

```
/singsi/
│
├── app/                               # Application Main Directory
│   ├── api/                           # API Endpoint Definitions
│   │   ├── __init__.py
│   │   └── ai.py                      # AI Services Related APIs
│   │
│   ├── core/                          # Core Configuration
│   │   └── config.py                  # Configuration Management
│   │
│   ├── examples/                      # Example Code & Usage Demos
│   │   └── conversation_example.py    # Simple AI conversation demo
│   │
│   ├── models/                        # Data Models
│   ├── schemas/                       # Pydantic Schemas
│   ├── services/                      # Business Logic Services
│   │   ├── ai/                        # AI related modules
│   │   │   ├── __init__.py
│   │   │   ├── base/                       # Base AI definitions
│   │   │   │   └── ai_service_abstract.py  # AIService interface
│   │   │   ├── factory/                    # AI Service factory module
│   │   │   │   └── ai_service_factory.py   # Factory for AI service instances
│   │   │   ├── implementations/            # Specific AI platform implementations
│   │   │   │   └── openai_service.py       # OpenAI service implementation
│   │   │   └── utils/                      # Shared tools for AI functionalities
│   │   │       └── logging_utils.py        # Logging utilities
│   │   ├── other_services.py               # Other business logic modules
│   │   └── __init__.py
│   ├── tasks/                         # Asynchronous Tasks
│   ├── utils/                         # Utility Functions and Shared Tools
│   ├── __init__.py
│   └── main.py                        # Application Entry Point
│
├── tests/                             # Unit and Integration Tests
├── alembic/                           # Database Migrations
├── docs/                              # Documentation Files
│   ├── design_proposals.md            # Design Overview & Patterns
│   ├── PRD_EN.md                      # Product Requirements Document (English)
│   ├── PRD_zh_TW.md                   # Product Requirements Document (Traditional Chinese)
│   └── project_structure.md           # This Project Structure Document
│
├── Dockerfile                         # Docker Configuration
├── docker-compose.yml                 # Docker Compose Configuration
├── .env                               # Environment Variables
├── .gitignore                         # Git Ignore File
├── requirements.txt                   # Dependency List
└── README.md                          # Project Documentation
```

## Key Components

- **AI Service Modules**: Located at `app/services/ai/` with proper separation of interfaces, implementations, and factories
- **Configuration Management**: Centralized in `app/core/config.py` using Pydantic settings
- **API Layer**: RESTful endpoints defined in `app/api/` directory
- **Examples**: Sample code in `app/examples/` to demonstrate usage patterns
- **Utility Functions**: Located at `app/utils/` with common helper modules:
  - `prompts.py` - AI prompt templates and management
  - `file_utils.py` - File processing and manipulation utilities
  - `date_utils.py` - Date/time handling and formatting
  - `serializers.py` - Data conversion and serialization helpers
  - `constants.py` - Shared constants and settings
  - `response_utils.py` - API response formatting and standardization

## Architecture Notes

The project follows a modular design with clear separation of concerns:

1. Abstract interfaces define capabilities without implementation details
2. Concrete implementations provide specific functionality
3. Factory modules handle object creation with dependency injection
4. Configuration settings are centralized and strongly typed

This structure enables easy testing, extension, and maintenance of the codebase.
