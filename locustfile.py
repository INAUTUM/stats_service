from locust import HttpUser, task, between
import uuid
import random
from datetime import datetime, timedelta

class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        # Создаем тестовые устройства при старте пользователя
        self.device_ids = [str(uuid.uuid4()) for _ in range(5)]
        for device_id in self.device_ids:
            self.client.post(
                f"/devices/",
                json={"user_id": 1}  # Предполагаем, что пользователь с ID=1 существует
            )

    @task(3)
    def post_stat(self):
        device_id = random.choice(self.device_ids)
        self.client.post(
            f"/devices/{device_id}/stats/",
            json={
                "x": random.uniform(0, 100),
                "y": random.uniform(0, 100),
                "z": random.uniform(0, 100)
            },
            name="/devices/[id]/stats/"
        )

    @task(1)
    def get_analytics(self):
        device_id = random.choice(self.device_ids)
        end = datetime.now()
        start = end - timedelta(days=1)
        self.client.get(
            f"/devices/{device_id}/analytics/",
            params={
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            name="/devices/[id]/analytics/"
        )