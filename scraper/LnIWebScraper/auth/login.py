import requests

LOGIN_URL = "https://www.indeed.com/account/login"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

#email:pattersonbroski@gmail.com
#password:Coffee!1425

def login(session, email, password):
    payload = {
        "email": email,
        "password": password
    }
    response = session.post(LOGIN_URL, headers=HEADERS, data=payload)

    if response.status_code == 200:
        print("✅ Login successful!")
    else:
        print("❌ Login failed!")

    return session