from fastapi import FastAPI, WebSocket, HTTPException
import time
import itertools
import threading
import asyncio
from contextlib import asynccontextmanager

app = FastAPI()


class LeakyBucket:
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0
        self.last_checked = time.time()
        self.lock = threading.Lock()

    def leak(self):
        """Remove requests from the bucket based on the leak rate."""
        now = time.time()
        elapsed_time = now - self.last_checked
        leaked_water = elapsed_time * self.leak_rate

        with self.lock:
            self.water = max(0, self.water - leaked_water)
            self.last_checked = now

    def add_request(self):
        """Attempt to add a request to the bucket."""
        self.leak()  # Leak before adding a new request

        with self.lock:
            if self.water < self.capacity:
                self.water += 1
                return True  # Request is allowed
            else:
                return False  # Request is denied (bucket is full)

    def get_status(self):
        """Return the current number of requests in the bucket."""
        self.leak()  # Ensure bucket is updated before reporting status
        return self.water


NUM_CHANNELS = 4
channels = {i: LeakyBucket(capacity=1000, leak_rate=100) for i in range(NUM_CHANNELS)}
channel_iterator = itertools.cycle(range(NUM_CHANNELS))


async def leak_continuously():
    """Continuously leaks requests from all buckets even if no new requests are sent."""
    while True:
        for bucket in channels.values():
            bucket.leak()
        await asyncio.sleep(1)  # Run leak every 1 second


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background leak task on startup."""
    leak_task = asyncio.create_task(leak_continuously())  # Run leak in background
    yield
    leak_task.cancel()  # Cancel on shutdown


app = FastAPI(lifespan=lifespan)


@app.get("/request/")
async def process_request():
    """Process an API request and automatically assign it to an available channel."""
    for _ in range(NUM_CHANNELS):
        channel_id = next(channel_iterator)

        if channels[channel_id].add_request():
            return {"channel": channel_id, "status": "Allowed"}

    raise HTTPException(
        status_code=429, detail="Too Many Requests. Please try again later."
    )


@app.websocket("/status/")
async def websocket_status(websocket: WebSocket):
    """WebSocket endpoint to stream bucket status in real-time."""
    await websocket.accept()
    try:
        while True:
            status = {
                f"channel_{i}": channels[i].get_status() for i in range(NUM_CHANNELS)
            }
            await websocket.send_json(status)
            await asyncio.sleep(3)  # Send updates every 3 seconds
    except Exception as e:
        print(f"WebSocket disconnected: {e}")
