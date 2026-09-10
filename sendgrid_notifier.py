import requests
import os

class SendGridNotifier:
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY', '')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'noreply@yourcompany.com')
        self.it_team_emails = [
            os.environ.get('IT_EMAIL', 'it-support@yourcompany.com'),
        ]
    
    def send_email(self, to_email, subject, body):
        if not self.api_key:
            print("❌ SendGrid API key not set")
            return False
        
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
            print(f"✅ Email sent to {to_email}")
            return True
        else:
            print(f"❌ SendGrid error: {response.text}")
            return False