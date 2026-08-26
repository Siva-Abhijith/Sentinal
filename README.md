# Sentinel

A distributed rate limiter built with **FastAPI, Valkey, Lua, and the Token Bucket algorithm**.

## Architecture

```text
              Client
             /      \
            v        v
       API :8000   API :8001
            \        /
             v      v
             Valkey
          Shared State
```

Both API instances share the same rate-limit state through Valkey.

Lua executes the bucket update atomically, preventing race conditions when multiple requests arrive concurrently.

## Features

- Token Bucket rate limiting
- Atomic Lua-based state updates
- Distributed rate limiting across API instances
- Valkey/Redis backend
- `429 Too Many Requests` + `Retry-After`
- `503` handling when Valkey is unavailable
- Prometheus metrics
- Docker Compose
- Locust load testing
- Distributed and concurrency tests

## Configuration

Default rate limit:

```text
capacity    = 5 requests
refill_rate = 1 token/second
```

Valkey configuration:

```text
REDIS_HOST=valkey
REDIS_PORT=6379
```

## Run

```bash
docker compose up -d
```

API instances:

```text
http://localhost:8000
http://localhost:8001
```

Health check:

```bash
curl http://localhost:8000/health
```

Metrics:

```bash
curl http://localhost:8000/metrics
```

## Testing

```bash
python -m pytest -v
```

Result:

```text
12 passed
```

Tests cover:

- Redis integration
- Token bucket behavior
- Lua rate limiting
- Lua race conditions
- Backend failure handling
- Distributed rate limiting

## Load Test

```bash
locust -f loadtest/locustfile.py \
    --headless \
    -u 50 \
    -r 10 \
    -t 60s
```

### Benchmark

| Metric | Result |
|---|---:|
| Users | 50 |
| Duration | 60s |
| Requests | 88,914 |
| Throughput | 1,487 req/s |
| Failures | 0% |
| Median | 2 ms |
| p95 | 4 ms |
| p99 | 6 ms |
| Max | 25 ms |

> Benchmark performed locally using two FastAPI containers and Valkey. Results are not a production capacity guarantee.

## Failure Handling

If Valkey becomes unavailable, Sentinel does not hang indefinitely.

Redis connections use:

```text
connect timeout = 1s
socket timeout  = 1s
retries          = 0
```

The API returns:

```http
503 Service Unavailable
```

## Project Structure

```text
sentinel/
├── app/
│   ├── lua/
│   │   └── token_bucket.lua
│   ├── lua_rate_limiter.py
│   ├── main.py
│   └── redis_client.py
├── tests/
├── loadtest/
│   └── locustfile.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Tech Stack

**Python · FastAPI · Valkey · Redis · Lua · Docker · Prometheus · Locust · Pytest**