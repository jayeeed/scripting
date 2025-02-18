from fastapi import FastAPI, WebSocket, HTTPException
import time
import itertools
import threading

app = FastAPI()


class LeakyBucket:
    def __init__(self, capacity: int, leak_rate: float):
        """
        Initialize a leaky bucket for a channel.

        :param capacity: Maximum capacity of the bucket (number of requests)
        :param leak_rate: Number of requests that can be processed per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0  # Current water level (requests in the bucket)
        self.last_checked = time.time()
        self.lock = threading.Lock()  # Ensure thread safety

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
        self.leak()  # Update the bucket before reporting status
        return self.water


# Create 4 independent channels (each with its own bucket)
NUM_CHANNELS = 4
channels = {i: LeakyBucket(capacity=500, leak_rate=250) for i in range(NUM_CHANNELS)}

# Round-robin iterator for channel selection
channel_iterator = itertools.cycle(range(NUM_CHANNELS))


@app.get("/request/")
async def process_request():
    """
    Process an API request and automatically assign it to an available channel.

    :return: Response indicating whether the request is allowed or denied.
    """
    for _ in range(NUM_CHANNELS):  # Try all channels before rejecting
        channel_id = next(channel_iterator)  # Get the next channel in round-robin order

        if channels[channel_id].add_request():
            return {"channel": channel_id, "status": "Allowed"}

    # If all channels are full, deny the request
    raise HTTPException(
        status_code=429, detail="Too Many Requests. Please try again later."
    )


@app.websocket("/status/")
async def websocket_status(websocket: WebSocket):
    """
    WebSocket endpoint to stream bucket status in real-time.
    """
    await websocket.accept()
    try:
        while True:
            status = {
                f"channel_{i}": channels[i].get_status() for i in range(NUM_CHANNELS)
            }
            await websocket.send_json(status)  # Send real-time data
            time.sleep(1)  # Send updates every second
    except Exception as e:
        print(f"WebSocket disconnected: {e}")
