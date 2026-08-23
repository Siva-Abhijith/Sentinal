from concurrent.futures import ThreadPoolExecutor
import uuid

from app.redis_client import redis_client
from app.redis_rate_limiter import RedisRateLimiter


def test_naive_rate_limiter_has_race_condition():
    client_id = f"race-{uuid.uuid4()}"
    key = f"rate_limit:{client_id}"

    limiter = RedisRateLimiter(
        capacity=1,
        refill_rate=0,
    )

    def make_request():
        return limiter.allow(client_id)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(
            executor.map(
                lambda _: make_request(),
                range(20),
            )
        )

    allowed = sum(results)

    print(f"\nAllowed requests: {allowed}")

    redis_client.delete(key)

    assert allowed > 1