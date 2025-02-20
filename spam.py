import requests
import time
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter

# Configuration
req = 1000
workers = 4
url = "http://127.0.0.1:8000/request/"


session = requests.Session()
adapter = HTTPAdapter(pool_connections=workers, pool_maxsize=workers * 4)
# adapter = HTTPAdapter(pool_connections=workers)
session.mount("http://", adapter)


def send_request():
    try:
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


while True:
    start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(lambda _: send_request(), range(req))

    print(f"Sent {req} requests in {time.time() - start:.2f} seconds")
