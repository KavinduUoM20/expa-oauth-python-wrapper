import requests
import re
import json

class EXPA:
    def __init__(self, username, password, enforce_ssl=True):
        self.username = username
        self.password = password
        self.enforce_ssl = enforce_ssl
        self.base_url = 'https://gis-api.aiesec.org/v2'
        self.session = requests.Session()

    def _get_csrf_token(self):
        try:
            # Perform a GET request to fetch the CSRF token from the sign-in page
            login_url = 'https://auth.aiesec.org/users/sign_in'
            response = self.session.get(login_url, verify=self.enforce_ssl)

            # Extract CSRF token from the response using regex      
            csrf_token_match = re.search(r'<meta name="csrf-token" content="(.*?)" \/>', response.text)

            if csrf_token_match:
                csrf_token = csrf_token_match.group(1)
                print(f"CSRF Token: {csrf_token}")
                print("CSRF Generation Running")
                return csrf_token
            else:
                print("CSRF token not found in response.")
                raise RuntimeError('CSRF token not found in the response')
                
        except Exception as e:
            raise RuntimeError(f'Error fetching CSRF token: {e}')

    def _authenticate(self, csrf_token):
        try:
            # Authenticate by making a POST request with username, password, and CSRF token
            login_url = 'https://auth.aiesec.org/users/sign_in'
            data = {
                "user[email]": self.username,
                "user[password]": self.password,
                "authenticity_token": csrf_token,
                "commit": 'Sign in'
            }
            response = self.session.post(login_url, data=data, verify=self.enforce_ssl)
            print("Authentication Running")
            # Check if authentication was successful
            if '<h2>Invalid email or password.' in response.text:
                raise RuntimeError('Invalid email or password')
        except Exception as e:
            raise RuntimeError(f'Error authenticating: {e}')

    def get_new_token(self):
        try:
            # Get a new authentication token
            csrf_token = self._get_csrf_token()
            # Print cookies before authentication
            print('Cookies before authentication:', self.session.cookies)
            self._authenticate(csrf_token)
            print('Cookies after authentication:', self.session.cookies)
            # Extract the authentication token (aiesec_token) from cookies
            aiesec_token = self.session.cookies.get('aiesec_token')
            if not aiesec_token:
                raise RuntimeError('Authentication token (aiesec_token) not found in cookies')

            # Parse the token to obtain the access token
            token_data = json.loads(aiesec_token.replace('aiesec_token=', ''))
            access_token = token_data['token']['access_token']
            return access_token
        except Exception as e:
            raise RuntimeError(f'Error getting new token: {e}')

    def get_token(self):
        try:
            # Get the existing authentication token or fetch a new one if needed
            if 'aiesec_token' in self.session.cookies:
                print("Checking Cookies")
                aiesec_token = self.session.cookies.get('aiesec_token')
                return aiesec_token
            else:
                print("Get New Token")
                new_token = self.get_new_token()
                print("New token", new_token)
                return new_token
        except Exception as e:
            raise RuntimeError(f'Error getting token: {e}')


# Example usage: Retrieve the authentication token


# Example usage: Retrieve the authentication token
if __name__ == "__main__":
    # Replace 'your_username' and 'your_password' with your AIESEC credentials
    username = ""
    password = ""

    # Instantiate an EXPA object with your credentials
    expa = EXPA(username, password)

    try:
        # Retrieve the authentication token
        token = expa.get_token()
        print('Authentication Token:', token)

    except requests.exceptions.RequestException as e:
        print('Error:', e)
    except RuntimeError as e:
        print('Authentication Error:', e)
