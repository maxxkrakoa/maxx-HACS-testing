import asyncio
import aiohttp
import requests
import base64
import os
import hashlib
import re

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

def test_requests():
    username = "testuser"
    password = "testpassword"
    
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")
    
    with requests.Session() as session:
        # Not adding headers to session here just like the old code
        url = f"{API_URL.replace('webservice', 'auth-webservice')}/authorize"
        req_code = session.request(
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
        )
        print("REQUESTS GET Status:", req_code.status_code)
        
        csrf_token = str(req_code.cookies.get("x-ms-cpim-csrf"))
        print("REQUESTS Token:", csrf_token)
        
        match = re.search(r"var SETTINGS = (\{[^;]*\});", req_code.text)
        transaction_id = [
            i for i in match.group(1).split('","') if i.startswith("transId")
        ][0][10:]
        
        print("REQUESTS TX:", transaction_id)
        
        req_auth = session.request(
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
                "Referer": req_code.url,
                "X-Csrf-Token": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
            },
            allow_redirects=False,
        )
        print("REQUESTS POST Status:", req_auth.status_code)
        print("REQUESTS Outgoing Headers:", req_auth.request.headers)
        print("REQUESTS POST Body:", req_auth.text)
        
        req_confirm = session.request(
            method="GET",
            url=f"{AUTHN_URL}/api/CombinedSigninAndSignup/confirmed",
            params={
                "rememberMe": str(False),
                "csrf_token": csrf_token,
                "tx": transaction_id,
                "p": OAUTH2_PROFILE,
            },
            allow_redirects=False,
        )
        print("REQUESTS CONFIRM Status:", req_confirm.status_code)
        print("REQUESTS CONFIRM Location:", req_confirm.headers.get("Location"))

test_requests()
