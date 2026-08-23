import time

from app.redis_client import redis_client


class RedisRateLimiter:
    def __init__(
        self,
        capacity: float,
        refill_rate: float,
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate

    def allow(self, client_id: str) -> bool:
        key = f"rate_limit:{client_id}"

        # Read current state
        state = redis_client.hgetall(key)

        if not state:
            tokens = self.capacity
            last_refill_time = time.monotonic()
        else:
            tokens = float(state["tokens"])
            last_refill_time = float(state["last_refill_time"])

        # Refill
        now = time.monotonic()
        elapsed = now - last_refill_time

        tokens_to_add = elapsed * self.refill_rate

        tokens = min(
            self.capacity,
            tokens + tokens_to_add,
        )

        # Check whether request can be allowed
        if tokens < 1:
            return False

        tokens -= 1

        # Write updated state
        redis_client.hset(
            key,
            mapping={
                "tokens": tokens,
                "last_refill_time": now,
            },
        )

        return True