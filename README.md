# Secure REST API with Flask

## Overview
A secure REST API built with Flask, featuring JWT authentication, Swagger documentation, and PostgreSQL integration.

## Features
- JWT Authentication with refresh tokens
- Interactive Swagger UI documentation
- PostgreSQL database integration
- Rate limiting and security features (CORS, CSP)
- User registration and authentication
- Protected API endpoints

## Prerequisites
- Python 3.11+
- PostgreSQL database
- Required environment variables:
  - DATABASE_URL
  - FLASK_SECRET_KEY
  - Other PostgreSQL configuration variables

## Installation
```bash
# Clone repository
git clone <repository-url>
cd secure-api-wizard

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export FLASK_SECRET_KEY='your-secret-key'
export DATABASE_URL='postgresql://...'

# Run the application
python main.py
```

## API Documentation
Access the interactive API documentation at `http://localhost:8000/`

### Available Endpoints
#### Authentication
- POST /api/v1/auth/register - Register new user
- POST /api/v1/auth/login - Login and get JWT tokens
- POST /api/v1/auth/refresh - Refresh access token
- POST /api/v1/auth/logout - Logout (revoke token)

#### Protected Resources
- GET /api/v1/api/users - List all users
- GET /api/v1/api/users/{id} - Get user by ID
- GET /api/v1/api/profile - Get current user profile

## Security Features
- JWT Authentication
- Token refresh mechanism
- Rate limiting (100 requests per hour)
- CORS protection
- Content Security Policy (CSP)
- Token blacklisting
- Secure password hashing

## Development
The application uses Flask-RESTX for API development and Swagger documentation. Key configuration files:
- `app.py` - Application setup
- `core/config.py` - Configuration settings
- `api/` - API endpoints and resources
- `models/` - Database models

## Deployment
Currently configured for development. For production:
1. Use a production WSGI server
2. Enable HTTPS
3. Set appropriate environment variables
4. Configure proper database credentials

## License
MIT License

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
