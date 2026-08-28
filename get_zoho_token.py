import requests
import json

# PUT YOUR ACTUAL VALUES HERE
code = "1000.e30ba4b457c752e77ce705ec5dc7fc95.a116238df8e5d861938e49aaae65bfe3"
client_id = "1000.1KJKGYPV05CC193I0GF186ZBDJE4QH"
client_secret = "43bbbd620a874d4b06278892de78f2e754ddd06601"

url = "https://accounts.zoho.com/oauth/v2/token"
params = {
    "code": code,
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "authorization_code"
}

response = requests.post(url, params=params)
result = response.json()

print("=" * 50)
print("RESPONSE:")
print("=" * 50)
print(json.dumps(result, indent=2))
print("=" * 50)

if "refresh_token" in result:
    print(f"\n✅ REFRESH TOKEN: {result['refresh_token']}")
    print("\nCOPY THIS TOKEN!")