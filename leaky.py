import time


class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        """
        Initialize a leaky bucket for a channel.

        :param capacity: Maximum capacity of the bucket (number of requests)
        :param leak_rate: Number of requests that can be processed per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0  # Current water level (requests in the bucket)
        self.last_checked = time.time()

    def leak(self):
        """Remove requests from the bucket based on the leak rate."""
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


# Create 4 channels with individual leaky buckets
num_channels = 4
channels = [LeakyBucket(capacity=110, leak_rate=10) for _ in range(num_channels)]

# Simulating incoming requests to different channels
for i in range(100):  # Simulating 20 requests
    channel_id = i % num_channels  # Distribute requests across channels
    if channels[channel_id].add_request():
        print(f"Request {i + 1} in Channel {channel_id + 1}: Allowed")
    else:
        print(f"Request {i + 1} in Channel {channel_id + 1}: Denied")

    # time.sleep(0.01)  # Requests arrive every 0.01 seconds
