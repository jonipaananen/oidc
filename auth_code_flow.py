import http.server
import threading
import traceback
import urllib
from typing import Any
from urllib.parse import urlparse
import auth
from tokens_to_html import tokens_to_html

authenticator = auth.OIDCAuth()

# HTTP handler that expects an authentication code flow redirect from Entra
# The code parameter is extracted, and used to fetch access and id tokens from Entra.
# A html document is generated that displays the tokens, and then the web server is shut down
class AuthCodeResponseHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            tokens = authenticator.get_tokens(self.extract_code())
            self.response_success(tokens)
        except Exception as e:
            self.response_error()
            raise e
        finally:
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    def response_error(self):
        self.send_response(500)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(traceback.format_exc().encode())

    def response_success(self, tokens: dict[str, dict[str, Any]]):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(tokens_to_html(tokens).encode())

    def extract_code(self) -> str:
        host = self.headers.get("Host")
        full_url = f"http://{host}{self.path}"
        parsed_url = urlparse(full_url)
        return urllib.parse.parse_qs(parsed_url.query).get("code")[0]

    # Silence logging
    def log_message(self, format, *args):
        return

# Initiates authentication with authorization code flow, by opening a web browser to the authentication end point
# in Entra.
# A simple http server is started to handle the redirect back from Entra.
# Entra redirects the browser back to localhost, with a code. The tokens can be retrieved from the Entra token endpoint.
# The tokens are displayed, and the http server is shut down right away.
def authenticate(port=8080):
    authenticator.init_auth_code_flow()
    server = http.server.HTTPServer(("0.0.0.0", port), AuthCodeResponseHandler)
    server.serve_forever()

if __name__ == '__main__':
    authenticate()
