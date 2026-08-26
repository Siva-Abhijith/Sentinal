from random import choice

from locust import HttpUser, task, between


class SentinelUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(0.01, 0.05)

    @task
    def request(self):
        host = choice([
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8001",
        ])

        with self.client.get(
            f"{host}/",
            catch_response=True,
            name="GET /",
        ) as response:
            if response.status_code in (200, 429):
                response.success()
            else:
                response.failure(
                    f"Unexpected status: {response.status_code}"
                )