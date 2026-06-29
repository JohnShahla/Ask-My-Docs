# Orbit Analytics — API Reference

## Authentication

The Orbit API uses **bearer token authentication**. Generate an API key from the
project settings page and pass it in the `Authorization` header:

```
Authorization: Bearer orbit_sk_live_...
```

API keys are scoped to a single project. Never expose a secret key in client-side
code.

## Rate Limits

Rate limits are enforced per project and depend on the plan:

- **Free** — 60 requests per minute.
- **Pro** — 600 requests per minute.
- **Enterprise** — Custom limits negotiated per contract.

When a limit is exceeded, the API returns HTTP `429 Too Many Requests` with a
`Retry-After` header indicating how many seconds to wait.

## Endpoints

- `POST /v1/events` — Ingest one or more analytics events.
- `GET /v1/users/{id}` — Retrieve a user profile and its computed traits.
- `GET /v1/funnels/{id}` — Retrieve a funnel definition and its conversion rates.

## Errors

The API uses conventional HTTP status codes:

- `401 Unauthorized` — Missing or invalid API key.
- `404 Not Found` — The requested resource does not exist.
- `429 Too Many Requests` — Rate limit exceeded; respect the `Retry-After` header.
- `5xx` — A server error occurred; retries with exponential backoff are safe.
