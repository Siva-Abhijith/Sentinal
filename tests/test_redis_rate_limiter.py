import uuid

from app.redis_client import redis_client
from app.redis_rate_limiter import RedisRateLimiter


def test_redis_rate_limiter_allows_requests():
    client_id = f"test-{uuid.uuid4()}"

    limiter = RedisRateLimiter(
        capacity=2,
        refill_rate=1,
    )

    assert limiter.allow(client_id) is True
    assert limiter.allow(client_id) is True
    assert limiter.allow(client_id) is False

    redis_client.delete(f"rate_limit:{client_id}")