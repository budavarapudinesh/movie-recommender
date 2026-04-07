from jose import jwt
import json
from datetime import datetime, timedelta, timezone

secret_key = "super_secret_key"
algorithm = "HS256"

data = {"sub": 52}
expire = datetime.now(timezone.utc) + timedelta(minutes=30)
data.update({"exp": expire})

token = jwt.encode(data, secret_key, algorithm=algorithm)
print("Token:", token)

try:
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    print("Payload:", payload)
except Exception as e:
    print("Error:", e)
