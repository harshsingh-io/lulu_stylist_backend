import requests
import time
from datetime import datetime
import json

def test_refresh_flow():
    BASE_URL = "http://localhost:8000/api"
    
    # 1. Login
    login_data = {
        "username": "harshtobekind@gmail.com",  
        "password": "helloworld"       
    }
    print(f"\n[{datetime.now()}] 1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/login",
        data=login_data
    )
    
    print(f"Login Response Status: {login_response.status_code}")
    print(f"Login Response Body: {login_response.text}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    tokens = login_response.json()
    print(f"\nReceived tokens: {json.dumps(tokens, indent=2)}")
    
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    
    if not access_token or not refresh_token:
        print("Error: Missing tokens in response")
        return
    
    print("\nLogin successful!")
    print(f"Access Token: {access_token[:20]}...")
    print(f"Refresh Token: {refresh_token[:20]}...")
    
    # 2. Test access token
    print(f"\n[{datetime.now()}] 2. Testing access token...")
    me_response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print(f"Me endpoint response: {me_response.status_code}")
    if me_response.status_code == 200:
        print(f"User data: {me_response.json()}")
    else:
        print(f"Me endpoint failed: {me_response.text}")
    
    # 3. Test refresh token
    print(f"\n[{datetime.now()}] 3. Testing refresh token...")
    refresh_response = requests.post(
        f"{BASE_URL}/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    
    print(f"Refresh response status: {refresh_response.status_code}")
    print(f"Refresh response body: {refresh_response.text}")
    
    if refresh_response.status_code == 200:
        new_tokens = refresh_response.json()
        print("\nSuccessfully got new tokens!")
        print(f"New Access Token: {new_tokens['access_token'][:20]}...")
        print(f"New Refresh Token: {new_tokens['refresh_token'][:20]}...")
    else:
        print(f"Refresh failed: {refresh_response.text}")

if __name__ == "__main__":
    test_refresh_flow()