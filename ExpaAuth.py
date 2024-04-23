import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# AIESEC OAuth Configuration
AUTHORIZATION_URL = "https://auth.aiesec.org/oauth/authorize"
TOKEN_URL = "https://auth.aiesec.org/oauth/token"
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:8000"  # Update with your redirect URI
SCOPE = ""  # Specify required scope if needed
AUTHENTICATION_TYPE = "login"  # or "signup" based on your requirement

class AuthorizationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the query parameters from the requested URL
        query_params = parse_qs(urlparse(self.path).query)
        authorization_code = query_params.get("code")

        if authorization_code:
            authorization_code = authorization_code[0]  # Extract authorization code

            # Exchange authorization code for access token
            print("Exchanging authorization code for access token...")
            payload = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI
            }

            response = requests.post(TOKEN_URL, data=payload)
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                print("Access Token:", access_token)
            else:
                print("Token exchange failed:", response.text)

            # Respond to the client with a simple message
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization Successful!</h1></body></html>")
        else:
            # Handle error case where no authorization code is found
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization Failed</h1></body></html>")

def authenticate_with_aiesec():
    # Step 1: Open authorization URL in browser
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "authentication_type": AUTHENTICATION_TYPE,
        "scope": SCOPE
    }
    auth_url = AUTHORIZATION_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    print("Opening authorization URL in browser...")
    webbrowser.open_new(auth_url)  # Open URL in a new tab

    # Step 2: Start a local HTTP server to capture the redirect URL
    print("Waiting for authorization...")
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, AuthorizationHandler)
    httpd.handle_request()  # Serve a single request and then shut down

if __name__ == "__main__":
    authenticate_with_aiesec()