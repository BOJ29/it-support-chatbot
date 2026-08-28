import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "agmasiltd@gmail.com"
sender_password = "noazwstentfgnrlg"
recipient = "agmasiltd@gmail.com"

try:
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = "Test from IT Chatbot"
    msg.attach(MIMEText("Testing Gmail!", 'plain'))
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Failed: {e}")