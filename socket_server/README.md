# Socket Server

Production-ready Socket.IO server for real-time chat streaming with the dbiz_ai_agent frontend.

## Run locally

```bash
npm install
npm start
```

Development with auto-reload:

```bash
npm run dev
```

## Environment

| Variable | Description | Default |
|----------|-------------|---------|
| `SIO_PORT` | Server port | `5179` |
| `SIO_CORS` | Allowed CORS origin(s); required in production | `*` (dev) |
| `SIO_AUTH_TOKEN` | Optional auth token for connections | — |
| `SIO_MAX_CONNECTIONS` | Max concurrent connections | `1000` |
| `SIO_RATE_LIMIT_MAX` | Max events per client per window | `100` |
| `SIO_RATE_LIMIT_WINDOW` | Rate limit window (ms) | `60000` |

Copy `.env.example` to `.env` and set values as needed.

## Docker

```bash
docker compose up -d
```

Health check: `http://localhost:5179/health` (or your `SIO_PORT`).

## Requirements

- Node.js >= 18
- npm >= 9
