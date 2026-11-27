"""Check an EstateFlow Cognito test login using a local OAuth callback."""

import argparse
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import secrets
from time import monotonic
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
import webbrowser


CALLBACK = "http://127.0.0.1:8765/callback"


def authorize(domain: str, client_id: str, verifier: str) -> str:
    state = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
    query = urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": CALLBACK,
        "scope": "openid",
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": challenge.rstrip(b"=").decode(),
    })
    code = None
    denied = False

    class CallbackHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # The callback URL contains the authorization code.

        def do_GET(self):
            nonlocal code, denied
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            if url.path != "/callback":
                self.send_error(404)
                return
            if params.get("state") != [state]:
                self.send_error(400, "Invalid sign-in state")
                return
            codes = params.get("code", [])
            if "error" in params or len(codes) != 1:
                denied = True
                self.send_error(400, "Cognito sign-in did not return a code")
                return
            code = codes[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Callback received. Check the terminal for the result.")

    with HTTPServer(("127.0.0.1", 8765), CallbackHandler) as server:
        server.timeout = 1
        sign_in_url = f"{domain}/oauth2/authorize?{query}"
        if not webbrowser.open(sign_in_url):
            print(f"Open this sign-in URL in your browser:\n{sign_in_url}")
        deadline = monotonic() + 180
        while code is None and not denied and monotonic() < deadline:
            server.handle_request()
    if code is None:
        raise SystemExit("Cognito sign-in failed or timed out. Check the app client and try again.")
    return code


def check_user(domain: str, client_id: str, code: str, verifier: str) -> None:
    token_request = Request(f"{domain}/oauth2/token", data=urlencode({
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": CALLBACK,
        "code": code,
        "code_verifier": verifier,
    }).encode(), headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(token_request, timeout=15) as response:
        access_token = json.load(response)["access_token"]
    user_request = Request(
        f"{domain}/oauth2/userInfo", headers={"Authorization": f"Bearer {access_token}"}
    )
    with urlopen(user_request, timeout=15) as response:
        if not json.load(response).get("sub"):
            raise SystemExit("Cognito userInfo did not return a subject.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain", help="Cognito prefix domain, without https://")
    parser.add_argument("client_id", help="Public app client ID for the smoke check")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+\.auth\.[a-z0-9-]+\.amazoncognito\.com", args.domain):
        parser.error("Use the AWS-provided Cognito prefix domain.")
    domain = f"https://{args.domain}"
    verifier = secrets.token_urlsafe(48)
    try:
        check_user(domain, args.client_id, authorize(domain, args.client_id, verifier), verifier)
    except (OSError, ValueError, KeyError):
        raise SystemExit(
            "Cognito smoke check failed. Check the callback port and app client settings."
        ) from None
    print("Cognito authorization code exchange and userInfo check passed.")


if __name__ == "__main__":
    main()
