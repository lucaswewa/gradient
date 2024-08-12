import uvicorn
import asyncio


async def app(scope, receive, send):
    assert scope["type"] == "http"
    print(scope["path"])

    body = f'Received {scope["method"]} request to {scope["path"]}'
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/plain"],
            ],
        }
    )
    await send({"type": "http.response.body", "body": body.encode("utf-8")})


async def main():
    config = uvicorn.Config(
        "test:app", host="0.0.0.0", port=5000, reload=True, log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
