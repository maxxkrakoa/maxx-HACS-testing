import asyncio
import aiohttp
import base64
import os
import hashlib
import re
import urllib.parse

OAUTH2_PROFILE = "B2C_1_signin_username"
AUTHN_URL = f"https://brunatab2cprod.b2clogin.com/brunatab2cprod.onmicrosoft.com/{OAUTH2_PROFILE}"
API_URL = "https://online.brunata.com/online-webservice/v1/rest"
CLIENT_ID = "e1d10965-78dc-4051-a1e5-251483e74d03"
REDIRECT = "https://online.brunata.com/auth-response"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en",
    "Connection": "keep-alive",
}

async def test():
    username = "testuser"
    password = "testpassword"
    
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")
    
    # We create a session, add HEADERS as the old code did NOT do (wait, the old code didn't!)
    # Actually let's try WITHOUT HEADERS first.
    jar = aiohttp.CookieJar(unsafe=True, quote_cookie=False)
    async with aiohttp.ClientSession(headers=HEADERS, cookie_jar=jar) as session:
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
        async with session.request(
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
        ) as req_auth:
            print("Auth status:", req_auth.status)
            print("AIOHTTP Outgoing Headers:", req_auth.request_info.headers)
            print("Auth text:", await req_auth.text())

        print("GET confirmed")
        async with session.request(
            method="GET",
            url=f"{AUTHN_URL}/api/CombinedSigninAndSignup/confirmed",
            params={
                "rememberMe": str(False),
                "csrf_token": csrf_token,
                "tx": transaction_id,
                "p": OAUTH2_PROFILE,
            },
            allow_redirects=False,
        ) as req_confirm:
            print("AIOHTTP CONFIRM Status:", req_confirm.status)
            print("AIOHTTP CONFIRM Location:", req_confirm.headers.get("Location"))

asyncio.run(test())
