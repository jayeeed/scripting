import requests
import time

session = requests.Session()

req = 1000

while True:
    start = time.time()
    for _ in range(req):
        try:
            response = session.get("http://127.0.0.1:8000/request/")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
    print(f"Sent {req} requests in {time.time() - start:.2f} seconds")
