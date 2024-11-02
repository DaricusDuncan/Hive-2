# Secure REST API with Flask

## Overview
A secure REST API built with Flask, featuring JWT authentication, Swagger documentation, PostgreSQL integration, and GitHub integration.

## Features
- JWT Authentication with refresh tokens and token blacklisting
- Interactive Swagger UI documentation
- PostgreSQL database integration
- Role-Based Access Control (RBAC)
- API versioning (v1 and v2)
- Rate limiting and security features (CORS, CSP)
- GitHub API integration with issue analysis
- AI-powered issue analysis with Ollama
- Automated testing suite
- Professional commit message convention

## Prerequisites
- Python 3.11+
- PostgreSQL database (automatically configured on Replit)
- GitHub account and personal access token
- Ollama instance (optional, for AI analysis)

## Environment Variables
The following environment variables need to be configured:

### Required
```bash
FLASK_SECRET_KEY=your-secret-key                # Secret key for Flask application
GITHUB_TOKEN=your-github-token                  # GitHub personal access token
```

### Optional (Ollama Integration)
```bash
OLLAMA_API_URL=http://localhost:11434          # Ollama API endpoint
OLLAMA_MODEL=llama2                            # Ollama model to use
```

### Database Configuration
When running on Replit, the following variables are automatically configured:
```bash
DATABASE_URL                                    # Full database connection URL
PGHOST                                         # PostgreSQL host
PGPORT                                         # PostgreSQL port
PGUSER                                         # PostgreSQL username
PGPASSWORD                                     # PostgreSQL password
PGDATABASE                                     # PostgreSQL database name
```

## Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/yourusername/hive-2.git
cd hive-2

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export FLASK_SECRET_KEY='your-secret-key'
export GITHUB_TOKEN='your-github-token'
```

### 2. Database Setup
PostgreSQL connection details will be automatically configured when running on Replit.

### 3. Run the Application
```bash
python main.py
```

Access the API documentation at `http://localhost:8000/`

## API Documentation
- [API Documentation](docs/API.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](docs/SECURITY.md)
- [Commit Convention](COMMIT_CONVENTION.md)
- [Changelog](CHANGELOG.md)

## Project Structure
```
├── api/                  # API endpoints and resources
│   ├── auth.py          # Authentication endpoints
│   ├── github.py        # GitHub integration endpoints
│   ├── resources.py     # Main API resources
│   └── schemas.py       # Data schemas
├── core/                # Core functionality
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database setup
│   ├── rbac.py         # Role-based access control
│   ├── security.py      # Security features
│   └── version.py       # API versioning
├── models/              # Database models
├── services/            # Business logic services
│   ├── github.py        # GitHub API integration
│   └── ollama.py        # AI analysis integration
├── scripts/             # Utility scripts
├── tests/               # Test suites
└── docs/                # Documentation
```

## API Versioning
The API supports multiple versions:
- V1: Basic functionality
- V2: Enhanced responses with additional fields

Use appropriate version in URL: `/api/v1/` or `/api/v2/`

## Development
1. Fork the repository
2. Create a feature branch
3. Follow commit message convention
4. Add tests for new features
5. Submit a pull request

## Testing
```bash
# Run test suite
python -m pytest

# Run with coverage
python -m pytest --cov=.
```

## Security
For security concerns, please see our [Security Policy](docs/SECURITY.md).

## License
MIT License - see [LICENSE](LICENSE) for details
