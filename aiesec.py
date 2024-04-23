import requests
from bs4 import BeautifulSoup
import urllib.parse

class EXPA:
    def __init__(self, username, password, enforce_ssl=True):
        self.username = username
        self.password = password
        self.enforce_ssl = enforce_ssl
        self.base_url = 'https://gis-api.aiesec.org/v2'
        self.session = requests.Session()
        self.token = None

    def _get_csrf_token(self):
        login_page_response = self.session.get('https://auth.aiesec.org/users/sign_in', verify=self.enforce_ssl)
        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        meta_tag = soup.find('meta', {'name': 'csrf-token'})
        if meta_tag:
            return meta_tag['content']
        else:
            raise ValueError("CSRF token not found in login page")

    def login(self):
        csrf_token = self._get_csrf_token()
        login_data = {
            'user[email]': self.username,
            'user[password]': self.password,
            'authenticity_token': csrf_token,
            'commit': 'Sign in'
        }
        response = self.session.post('https://auth.aiesec.org/users/sign_in', data=login_data, verify=self.enforce_ssl)
        response.raise_for_status()

        # Extract the session token from the cookie
        cookies = response.headers.get('Set-Cookie', '')
        session_token = self._extract_session_token(cookies)
        if session_token:
            self.token = session_token
            return session_token
        else:
            raise ValueError("Session token not found in response cookies")
        
    def _extract_session_token(self, cookies):
        parsed_cookies = urllib.parse.unquote(cookies)
        token_start = parsed_cookies.find('_gis_identity_v2_session=')
        if token_start != -1:
            token_start += len('_gis_identity_v2_session=')
            token_end = parsed_cookies.find(';', token_start)
            if token_end == -1:
                token_end = len(parsed_cookies)
            session_token = parsed_cookies[token_start:token_end]
            return session_token
        else:
            return None

def main():
    # Prompt for username and password
    username = ""
    password = ""

    # Create an instance of EXPA with provided credentials
    expa_client = EXPA(username, password)

    try:
        # Login and retrieve the session token
        session_token = expa_client.login()
        print("Session token:", session_token)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
   