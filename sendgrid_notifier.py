import requests
import os

class SendGridNotifier:
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY', '')
        self.sender_email = "agmasiltd@gmail.com"
        self.it_team_emails = ["agmasiltd@gmail.com"]
    
    def send_email(self, to_email, subject, body):
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "personalizations": [{
                "to": [{"email": to_email}]
            }],
            "from": {"email": self.sender_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 202:
            print("✅ Email sent via SendGrid!")
            return True
        else:
            print(f"❌ SendGrid error: {response.text}")
            return False