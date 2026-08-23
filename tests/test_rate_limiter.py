from app.rate_limiter import TokenBucket


def test_bucket_allows_requests_when_tokens_are_available():
    bucket = TokenBucket(capacity=3, refill_rate=1)

    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is True


def test_bucket_rejects_when_empty():
    bucket = TokenBucket(capacity=2, refill_rate=1)

    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_bucket_refills_tokens():
    bucket = TokenBucket(capacity=3, refill_rate=1)

    # Consume all tokens.
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False

    # Simulate 2 seconds passing.
    bucket.last_refill_time -= 2

    # 2 tokens should have refilled.
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_bucket_does_not_exceed_capacity():
    bucket = TokenBucket(capacity=3, refill_rate=10)

    # Pretend 10 seconds passed.
    bucket.last_refill_time -= 10

    # Bucket should still contain only 3 tokens.
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_different_clients_have_independent_buckets():
    from app.rate_limiter import RateLimiter

    limiter = RateLimiter(capacity=2, refill_rate=1)

    assert limiter.allow("client_a") is True
    assert limiter.allow("client_a") is True
    assert limiter.allow("client_a") is False

    assert limiter.allow("client_b") is True
    assert limiter.allow("client_b") is True
    assert limiter.allow("client_b") is False


def test_same_client_shares_one_bucket():
    from app.rate_limiter import RateLimiter

    limiter = RateLimiter(capacity=2, refill_rate=1)

    assert limiter.allow("client_a") is True
    assert limiter.allow("client_a") is True
    assert limiter.allow("client_a") is False
