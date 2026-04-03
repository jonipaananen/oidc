import base64
import os
import urllib.parse
import webbrowser
import http.server
import threading

import requests
from dotenv import load_dotenv
import traceback
import urllib
from urllib.parse import urlparse



load_dotenv()

authority_url = os.environ["AUTHORITY_URL"]
token_endpoint = f"{authority_url}/oauth2/v2.0/token"
authorization_endpoint = f"{authority_url}/oauth2/v2.0/authorize"
client_id = os.environ["CLIENT_ID"]
scope = os.environ["SCOPE"]
callback_url = os.environ["REDIRECT_URL"]

maconomy_host = os.environ["MACONOMY_HOST"]
maconomy_installation = os.environ["MACONOMY_INSTALLATION"]


def init_auth_code_flow():

    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": callback_url,
    }
    authorization_url = f"{authorization_endpoint}?{urllib.parse.urlencode(params)}"
    webbrowser.open(authorization_url)

def set_reconnect_header(code):

    encoded_code = base64.b64encode(f"<http://localhost/>:{code}".encode())

    url = f"https://{maconomy_host}/maconomy-api/auth/{maconomy_installation}"

    headers = {
        "Authorization": f"X-OIDC-Code {encoded_code.decode("utf-8")}",
        "maconomy-authentication": "X-Reconnect",
    }
    response = requests.get(url, headers=headers)

    global reconnect_token
    reconnect_token = response.headers['Maconomy-Reconnect']


class AuthCodeResponseHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            set_reconnect_header(self.extract_code())
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Reconnect token is: {reconnect_token}".encode())
        except Exception as e:
            raise e
        finally:
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    def response_error(self):
        self.send_response(500)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(traceback.format_exc().encode())

    def response_success(self, tokens: str):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(tokens.encode())

    def extract_code(self) -> str:
        host = self.headers.get("Host")
        full_url = f"http://{host}{self.path}"
        parsed_url = urlparse(full_url)
        return urllib.parse.parse_qs(parsed_url.query).get("code")[0]

    # Silence logging
    def log_message(self, format, *args):
        return


def get_user_info():
    url = f"https://{maconomy_host}/maconomy-api/environment/{maconomy_installation}?variables=user.employeeinfo.name1"
    headers = {
        "authorization": f"X-Reconnect {reconnect_token}",
        "maconomy-authentication": f"X-Reconnect",
    }
    response = requests.get(url, headers=headers)
    print(response.json())


if __name__ == '__main__':
    init_auth_code_flow()
    server = http.server.HTTPServer(("0.0.0.0", 80), AuthCodeResponseHandler)
    server.serve_forever()
    get_user_info()

