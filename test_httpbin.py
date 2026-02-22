import asyncio
import aiohttp
import requests
import json

async def test_aiohttp():
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method="POST",
            url="https://httpbin.org/post",
            data={
                "tx": "123",
                "p": "B2C_1_signin_username"
            },
            headers={
                "Referer": "http://example.com",
                "X-Csrf-Token": "test_token",
                "X-Requested-With": "XMLHttpRequest",
            }
        ) as req:
            res = await req.json()
            print("AIOHTTP REQ HEADERS:")
            print(json.dumps(res["headers"], indent=2))
            print("AIOHTTP REQ BODY:")
            print(res["data"])
            print("AIOHTTP REQ FORM:")
            print(res["form"])

def test_requests():
    with requests.Session() as session:
        req = session.request(
            method="POST",
            url="https://httpbin.org/post",
            data={
                "tx": "123",
                "p": "B2C_1_signin_username"
            },
            headers={
                "Referer": "http://example.com",
                "X-Csrf-Token": "test_token",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        res = req.json()
        print("REQUESTS REQ HEADERS:")
        print(json.dumps(res["headers"], indent=2))
        print("REQUESTS REQ BODY:")
        print(res["data"])
        print("REQUESTS REQ FORM:")
        print(res["form"])

asyncio.run(test_aiohttp())
test_requests()
