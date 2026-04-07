import requests

# login
res = requests.post("http://localhost:8000/api/users/login", json={"username": "testuser", "password": "password"})
token = res.json().get("access_token")
print("Token:", token)

if token:
    # get me
    res_me = requests.get("http://localhost:8000/api/users/me", headers={"Authorization": f"Bearer {token}"})
    print("User:", res_me.json())
else:
    print("Login Response:", res.json())
