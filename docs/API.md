# API Documentation

## Authentication

### JWT Token System

The API uses JSON Web Tokens (JWT) for authentication with a dual-token system:

- Access Token: Short-lived token (1 hour) for API access
- Refresh Token: Long-lived token (30 days) for obtaining new access tokens

### Authentication Flow

1. Register user account
2. Login to receive tokens
3. Use access token for API requests
4. Refresh token when access token expires
5. Logout to revoke tokens

## API Versions

### Version 1 (v1)

Base endpoint: `/api/v1`

#### Authentication Endpoints

```http
POST /auth/register
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string"
}

Response: 201 Created
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "is_active": "boolean"
}
```

```http
POST /auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}

Response: 200 OK
{
    "access_token": "string",
    "refresh_token": "string"
}
```

```http
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response: 200 OK
{
    "access_token": "string"
}
```

```http
POST /auth/logout
Authorization: Bearer <access_token>

Response: 200 OK
{
    "message": "Token revoked successfully"
}
```

#### User Management

```http
GET /api/users
Authorization: Bearer <access_token>

Response: 200 OK
[
    {
        "id": "integer",
        "username": "string",
        "email": "string",
        "is_active": "boolean"
    }
]
```

```http
GET /api/profile
Authorization: Bearer <access_token>

Response: 200 OK
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "is_active": "boolean"
}
```

### Version 2 (v2)

Base endpoint: `/api/v2`

Enhanced responses with additional fields:

```http
GET /api/users
Authorization: Bearer <access_token>

Response: 200 OK
[
    {
        "id": "integer",
        "username": "string",
        "email": "string",
        "is_active": "boolean",
        "created_at": "datetime",
        "roles": ["string"]
    }
]
```

## Role-Based Access Control (RBAC)

### Available Roles

- `admin`: Full system access
- `moderator`: Limited administrative access
- `user`: Basic access rights

### Role Management

```http
GET /api/roles
Authorization: Bearer <access_token>
Required Role: admin

Response: 200 OK
[
    {
        "id": "integer",
        "name": "string",
        "description": "string"
    }
]
```

```http
POST /api/roles
Authorization: Bearer <access_token>
Required Role: admin

{
    "name": "string",
    "description": "string"
}

Response: 201 Created
{
    "message": "Role created successfully"
}
```

## GitHub Integration

### Repository Management

```http
GET /github/repositories
Authorization: Bearer <access_token>

Response: 200 OK
[
    {
        "name": "string",
        "description": "string",
        "url": "string",
        "stars": "integer",
        "forks": "integer",
        "language": "string"
    }
]
```

### Issue Analysis

```http
GET /github/repository/{owner}/{repo}/issue/{number}/analysis
Authorization: Bearer <access_token>

Response: 200 OK
{
    "issue_number": "integer",
    "title": "string",
    "complexity": "float",
    "security_impact": "float",
    "performance_impact": "float",
    "ux_impact": "float",
    "implementation_time": "integer",
    "state": "string"
}
```

## Rate Limiting

- Default: 100 requests per hour
- Authentication endpoints: 10 requests per minute
- GitHub integration: 50 requests per hour

## Error Responses

### Common Error Codes

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests

### Error Response Format

```json
{
  "message": "Error description",
  "error": "error_code"
}
```

## Security Features

- JWT token blacklisting
- Rate limiting
- CORS protection
- Content Security Policy (CSP)
- Database connection pooling
