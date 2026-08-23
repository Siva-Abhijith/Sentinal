import time


class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate

        self.tokens = capacity
        self.last_refill_time = time.monotonic()

    def _refill(self):
        now = time.monotonic()

        elapsed = now - self.last_refill_time
        tokens_to_add = elapsed * self.refill_rate

        self.tokens = min(
            self.capacity,
            self.tokens + tokens_to_add
        )

        self.last_refill_time = now

    def allow(self) -> bool:
        self._refill()

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        return False


class RateLimiter:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate

        self.buckets: dict[str, TokenBucket] = {}

    def allow(self, client_id: str) -> bool:
        if client_id not in self.buckets:
            self.buckets[client_id] = TokenBucket(
                capacity=self.capacity,
                refill_rate=self.refill_rate
            )

        return self.buckets[client_id].allow()
