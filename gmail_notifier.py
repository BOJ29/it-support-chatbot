import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class GmailNotifier:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "agmasiltd@gmail.com"
        self.sender_password = "noazwstentfgnrlg"
        self.it_team_emails = ["agmasiltd@gmail.com"]
    
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
    
    def send_ticket_notification(self, ticket_id, user_id, issue, priority):
        """Send ticket notification to IT team"""
        subject = f"🔧 Ticket #{ticket_id} - {priority} Priority"
        body = f"""
        NEW SUPPORT TICKET CREATED
        
        Ticket ID: #{ticket_id}
        Priority: {priority}
        User ID: {user_id}
        
        ISSUE:
        {issue}
        
        VIEW DASHBOARD:
        https://it-support-chatbot-xo65.onrender.com/admin/tickets
        
        This is an automated notification from IT Support Chatbot
        """
        
        for email in self.it_team_emails:
            self.send_email(email, subject, body)
        
        return True