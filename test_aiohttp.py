import asyncio
import aiohttp
from custom_components.maxx_hacs_testing.brunata.const import CLIENT_ID, REDIRECT, AUTHN_URL, OAUTH2_PROFILE, API_URL
import base64
import os
import hashlib
import re

async def test():
    # Use dummy user and pass
    username = "testuser"
    password = "testpassword"
    
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")
    
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL.replace('webservice', 'auth-webservice')}/authorize"
        print(f"GET {url}")
        async with session.request(
            method="GET",
            url=url,
            params={
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT,
                "scope": f"{CLIENT_ID} offline_access",
                "response_type": "code",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
        ) as req_code:
            print("Status:", req_code.status)
            req_code_url = str(req_code.url)
            print("Final URL:", req_code_url)
            
            csrf_token = None
            if "x-ms-cpim-csrf" in req_code.cookies:
                csrf_token = req_code.cookies["x-ms-cpim-csrf"].value
                print("Cookie from response:", csrf_token)
            else:
                cookies = session.cookie_jar.filter_cookies(req_code.url)
                if "x-ms-cpim-csrf" in cookies:
                    csrf_token = cookies["x-ms-cpim-csrf"].value
                    print("Cookie from jar:", csrf_token)
            
            req_code_text = await req_code.text()
            match = re.search(r"var SETTINGS = (\{[^;]*\});", req_code_text)
            if match:
                transaction_id = [
                    i for i in match.group(1).split('","') if i.startswith("transId")
                ][0][10:]
                print("TX:", transaction_id)
            else:
                print("No tx")
                return

        print("POST SelfAsserted")
        req_auth = await session.request(
            method="POST",
            url=f"{AUTHN_URL}/SelfAsserted",
            params={
                "tx": transaction_id,
                "p": OAUTH2_PROFILE,
            },
            data={
                "request_type": "RESPONSE",
                "logonIdentifier": username,
                "password": password,
            },
            headers={
                "Referer": req_code_url,
                "X-Csrf-Token": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        print("Auth status:", req_auth.status)
        print("Auth text:", await req_auth.text())

asyncio.run(test())
