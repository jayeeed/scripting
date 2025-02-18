import time


class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0
        self.last_checked = time.time()

    def leak(self):
        now = time.time()
        elapsed_time = now - self.last_checked
        leaked_water = elapsed_time * self.leak_rate

        # Reduce the water level based on leak rate, ensuring it doesn't go negative
        self.water = max(0, self.water - leaked_water)
        self.last_checked = now

    def add_request(self):
        """Attempt to add a request to the bucket."""
        self.leak()  # Leak before adding a new request

        if self.water < self.capacity:
            self.water += 1
            return True  # Request is allowed
        else:
            return False  # Request is denied (bucket is full)


# Example Usage
bucket = LeakyBucket(capacity=5, leak_rate=1)  # Max 5 requests, leaks 1 req/sec

for i in range(10):
    if bucket.add_request():
        print(f"Request {i + 1}: Allowed")
    else:
        print(f"Request {i + 1}: Denied")
    time.sleep(0.4)
