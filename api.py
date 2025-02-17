import requests
import json

url = "https://pre-prod-api.myalice.ai/api/analytics/projects/262/get-whatsapp-template-activity-logs"
params = {
    "platform": "1945",
    "start": "2025-01-19T00:00:00",
    "end": "2025-01-26T23:59:59",
    "limit": "10",
    "offset": "0",
    "template_ids": "1010667070702193",
    "search": "",
    "status": "all",
}
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,bn;q=0.7",
    "authorization": "Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4MTU1MjE3LCJpYXQiOjE3MzgxMzM2MTcsImp0aSI6ImJiZWYxMTVjMzYxMjQ5ZDA5NjhkNWZmZjYxZmU3ZDgxIiwidXNlcl9pZCI6MTgxOX0.ApJqnk_gJXFYKw66NMlnu1e7b0Kx145TXFGzoiz3YPc",
    "origin": "https://stage.myalice.ai",
    "priority": "u=1, i",
    "referer": "https://stage.myalice.ai/",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers, params=params)

print(response.json())
# Save the response to a variable
data = response.json()

# Create an HTML file and write the response data to it
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Response</title>
</head>
<body>
    <h1>API Response Data</h1>
    <pre>{json.dumps(data, indent=4)}</pre>
</body>
</html>
"""

with open("response.html", "w") as file:
    file.write(html_content)
