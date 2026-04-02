import base64
import hashlib
import json
import os
import urllib.parse
import webbrowser

import requests
from dotenv import load_dotenv

class OIDCAuth:

    def __init__(self):

        load_dotenv()

        self.authority_url = os.environ["AUTHORITY_URL"]
        self.token_endpoint = f"{self.authority_url}/oauth2/v2.0/token"
        self.authorization_endpoint = f"{self.authority_url}/oauth2/v2.0/authorize"
        self.client_id = os.environ["CLIENT_ID"]
        self.client_secret = os.environ["CLIENT_SECRET"]
        self.scope = os.environ["SCOPE"]
        self.callback_url = os.environ["REDIRECT_URL"]
        self.code_verifier = None

    @staticmethod
    def base64url_encode(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')

    @staticmethod
    def decode_jwt(token):
        # Split the JWT into its parts
        header_b64, payload_b64, signature_b64 = token.split('.')

        # Add padding if necessary and decode
        def decode_base64url(data):
            padding = '=' * (-len(data) % 4)
            return base64.urlsafe_b64decode(data + padding)

        header = json.loads(decode_base64url(header_b64))
        payload = json.loads(decode_base64url(payload_b64))

        return {"header": header, "claims": payload}

    # Generates a code verifier for PKCE
    @classmethod
    def generate_code_verifier(cls) -> str:
        raw = cls.base64url_encode(os.urandom(64))
        return raw[:64]

    @classmethod
    # Generates a code challenge for PKCE
    def generate_code_challenge(cls, code_verifier) -> str:
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        return cls.base64url_encode(digest)

    def init_auth_code_flow(self):

        self.code_verifier = self.generate_code_verifier()

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.scope,
            "redirect_uri": self.callback_url,
            "code_challenge": self.generate_code_challenge(self.code_verifier),
            "code_challenge_method": "S256",
        }
        authorization_url = f"{self.authorization_endpoint}?{urllib.parse.urlencode(params)}"

        webbrowser.open(authorization_url)


    def get_tokens(self, code):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": self.code_verifier,
            "redirect_uri": self.callback_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_endpoint, data=data)

        return {
            "access_token": self.decode_jwt(response.json()["access_token"]),
            "id_token": self.decode_jwt(response.json()["id_token"]),
        }