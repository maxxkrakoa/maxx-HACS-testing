import asyncio
import aiohttp
import requests

async def capture_request(use_aiohttp):
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    
    async def make_request():
        await asyncio.sleep(0.5)
        if use_aiohttp:
            print("--- AIOHTTP ---")
            async with aiohttp.ClientSession() as session:
                try:
                    await session.request(
                        method="POST",
                        url="http://127.0.0.1:8888/SelfAsserted",
                        params={"tx": "123", "p": "B2C"},
                        data={"request_type": "RESPONSE", "logonIdentifier": "u", "password": "p"},
                        headers={
                            "Referer": "http://example.com/?redirect_uri=foo",
                            "X-Csrf-Token": "csrf",
                            "X-Requested-With": "XMLHttpRequest",
                        }
                    )
                except Exception:
                    pass
        else:
            print("--- REQUESTS ---")
            with requests.Session() as session:
                try:
                    session.request(
                        method="POST",
                        url="http://127.0.0.1:8888/SelfAsserted",
                        params={"tx": "123", "p": "B2C"},
                        data={"request_type": "RESPONSE", "logonIdentifier": "u", "password": "p"},
                        headers={
                            "Referer": "http://example.com/?redirect_uri=foo",
                            "X-Csrf-Token": "csrf",
                            "X-Requested-With": "XMLHttpRequest",
                        }
                    )
                except Exception:
                    pass

    task = asyncio.create_task(make_request())
    await task
    server.close()
    await server.wait_closed()

async def handle_client(reader, writer):
    data = await reader.read(4096)
    print(data.decode('utf-8', errors='replace'))
    writer.write(b"HTTP/1.1 200 OK\r\n\r\n")
    writer.close()

asyncio.run(capture_request(True))
asyncio.run(capture_request(False))
