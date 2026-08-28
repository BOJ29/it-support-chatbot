import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class GmailNotifier:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get('GMAIL_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.environ.get('GMAIL_PASSWORD', 'your-app-password')
        self.it_team_emails = ["support@agmasiltd.com"]
    
    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False