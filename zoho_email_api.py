import requests

class ZohoEmailAPI:
    def __init__(self):
        self.client_id = "1000.1KJKGYPV05CC193I0GF186ZBDJE4QH"
        self.client_secret = "43bbbd620a874d4b06278892de78f2e754ddd06601"
        self.refresh_token = "1000.1ec3743c404f7b26079d3b0792fa4b73.e5b084184c754a528c122c8bddf55c6b"
        self.sender_email = "it@agmasiltd.com"
        self.access_token = None
    
    def get_access_token(self):
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            return self.access_token
        return None
    
    def send_email(self, to_email, subject, body):
        if not self.access_token:
            self.get_access_token()
        
        url = "https://mail.zoho.com/api/accounts/me/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "fromAddress": self.sender_email,
            "toAddress": to_email,
            "subject": subject,
            "content": body,
            "mailFormat": "html"
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print("Email sent!")
            return True
        else:
            print(f"Failed: {response.text}")
            return False