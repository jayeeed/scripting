import asyncio
import httpx
import uuid

URL = "https://prod-api.myalice.ai/webhooks/livechat/main/8cf6595625a611f088838edd0f08bcc3"


async def send_request(client, i):
    sender_id = uuid.uuid4().hex
    payload = {
        "type": "message",
        "source": "customer",
        "sender_id": sender_id,
        "data": {"payload": "", "type": "text", "text": f"hi {i}"},
    }
    response = await client.post(URL, json=payload)
    print(f"Request {i}: Status {response.status_code}")


# async def main():
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         tasks = [send_request(client, i) for i in range(1, 11)]
#         await asyncio.gather(*tasks)


async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        for i in range(1, 2):
            await send_request(client, i)


if __name__ == "__main__":
    asyncio.run(main())
