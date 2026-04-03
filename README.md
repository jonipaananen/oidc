# Simple POC for Maconomy API OIDC authentication

This python script authenticates the user with Entra OIDC, exchanges the code from entra to a Maconomy reconnect token,
which then can be used for authenticated calls.

## Authentication flow

1. The authorization url is built, given the Entra tenant id and client id:
    `https://login.microsoftonline.com/TENANT_ID/oauth2/authorize?client_id=CLIENT_ID&scope=openid&response_type=code&redirect_uri=REDIRECT_URI`
2. Ff the authentication is successful, entra redirects back to `http://localhost/`, with the authorization code.
3. The script has started an http server, and extracts the code. The code can then be used to call Maconomy and
    exchange it for a reconnect token:
    
    ```python
   encoded_code = base64.b64encode(f"<http://localhost/>:{code}".encode())

    url = "https://b3iaccess.deltekenterprise.com/maconomy-api/auth/b3"

    headers = {
        "Authorization": f"X-OIDC-Code {encoded_code.decode("utf-8")}",
        "maconomy-authentication": "X-Reconnect",
    }
    response = requests.get(url, headers=headers)
    reconnect_token = response.headers['Maconomy-Reconnect']
   ```
4. Given the reconnect token, it's now possible to make authenticated requests:

    ```python
    url = "https://b3iaccess.deltekenterprise.com/maconomy-api/environment/b3?variables=user.employeeinfo.name1"
    headers = {
        "authorization": f"X-Reconnect {reconnect_token}",
        "maconomy-authentication": f"X-Reconnect",
    }
    response = requests.get(url, headers=headers)
   ```
   Keep in mind that the reconnect token might have been updated in the last response, so for future requests, save it
   from the `Maconomy-Reconnect` header

## How to run

Set up a .env file:
```commandline
cp template.env .env
```

Enter the client id, tenant id, maconomy host, and maconomy installation in the [.env](.env) file

Set up a virtual environment:
```commandline
python -m venv .
```
Powershell: ``.venv/Scripts/Activate.ps1``

bash: ``.venv/bin/activate``

```commandline
pip install -r requirements.txt
```

execute:
```commandline
python app.py
```