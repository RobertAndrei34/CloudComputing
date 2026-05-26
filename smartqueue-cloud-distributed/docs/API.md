# API Documentation

FastAPI generates OpenAPI documentation automatically.

## Local Swagger UI

```text
http://localhost:8000/docs
```

## OpenAPI JSON

```text
http://localhost:8000/openapi.json
```

## Main API Groups

- Auth
- Users
- Services
- Appointments
- Queue
- Notifications
- Analytics
- System

## Authentication

Most endpoints require JWT authentication.

```text
POST /auth/login
```

The token is sent as:

```text
Authorization: Bearer <token>
```
