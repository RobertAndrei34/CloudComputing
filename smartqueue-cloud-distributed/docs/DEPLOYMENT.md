# Public Deployment Guide

This project is prepared for public deployment, but credentials and cloud accounts must be configured manually.

## Option A: Vercel + Render + Managed PostgreSQL

### Frontend on Vercel

1. Push the repository to GitHub.
2. Import the repository into Vercel.
3. Set the root directory to `frontend`.
4. Build command:

```bash
npm run build
```

5. Output directory:

```text
dist
```

6. Update the frontend API base URL in `frontend/src/api/client.js` to the deployed backend URL.

### Backend on Render

1. Create a new Web Service.
2. Root directory: `backend`.
3. Runtime: Docker.
4. Add environment variables:

```text
DATABASE_URL=<managed PostgreSQL URL>
SECRET_KEY=<secure secret>
REDIS_URL=<managed Redis URL>
RABBITMQ_URL=<managed RabbitMQ URL>
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### Worker on Render

Create a background worker using the same backend image and command:

```bash
python -m app.worker
```

## Option B: Railway

Railway can host:

- backend container;
- notification worker;
- PostgreSQL;
- Redis;
- RabbitMQ plugin or external RabbitMQ service.

## Important Notes

For a real public deployment, do not use:

```text
SECRET_KEY=change-this-secret-key
```

Use a long generated secret.

Also configure CORS to allow only the frontend domain instead of `*`.
