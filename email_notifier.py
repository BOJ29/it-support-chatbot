import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class EmailNotifier:
    def __init__(self):
        # ZOHO MAIL SETTINGS
        self.smtp_server = "smtp.zoho.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get('ZOHO_EMAIL', 'it@agmasiltd.com')
        self.sender_password = os.environ.get('ZOHO_PASSWORD', 'your-app-password')
        
        # IT Team who receives tickets
        self.it_team_emails = [
            os.environ.get('IT_EMAIL_1', 'support@agmasiltd.com'),
            # Add more as needed
        ]
    
    def send_ticket_notification(self, ticket_id, user_id, issue, priority):
        """Send email to IT team when new ticket is created"""
        
        # Priority emoji
        priority_emoji = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }
        emoji = priority_emoji.get(priority, '🔵')
        
        subject = f"{emoji} Ticket #{ticket_id} - {priority} Priority - IT Support"
        
        body = f"""
        ╔══════════════════════════════════════╗
        ║     NEW SUPPORT TICKET CREATED      ║
        ╚══════════════════════════════════════╝

        📋 Ticket ID: #{ticket_id}
        ⚡ Priority: {priority}
        📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        👤 User ID: {user_id}

        ─────────────────────────────────────
        📝 ISSUE DESCRIPTION:
        ─────────────────────────────────────
        {issue}

        ─────────────────────────────────────
        🔗 QUICK ACTIONS:
        ─────────────────────────────────────
        • View all tickets: https://it-support-chatbot-xo65.onrender.com/admin/tickets
        • Resolve this ticket: https://it-support-chatbot-xo65.onrender.com/admin/tickets

        ─────────────────────────────────────
        This is an automated notification from IT Support Chatbot
        """
        
        success_count = 0
        for email in self.it_team_emails:
            if self._send_email(email, subject, body):
                success_count += 1
        
        print(f"✅ Notification sent to {success_count}/{len(self.it_team_emails)} recipients for Ticket #{ticket_id}")
        return True
    
    def _send_email(self, to_email, subject, body):
        """Send single email via Zoho SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Zoho SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email sent to: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send to {to_email}: {str(e)}")
            return False