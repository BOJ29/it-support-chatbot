import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "it@agmasiltd.com"
sender_password = "internal@2005"
recipient = "support@agmasiltd.com"

servers_to_try = [
    ("smtppro.zoho.com", 465, "SSL"),
    ("smtp.zoho.com", 587, "TLS"),
    ("smtp.zoho.com", 465, "SSL"),
]

for server_name, port, method in servers_to_try:
    print(f"\nTrying {server_name}:{port} ({method})...")
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = "Test from IT Chatbot"
        msg.attach(MIMEText("Testing email!", 'plain'))
        
        if method == "SSL":
            server = smtplib.SMTP_SSL(server_name, port)
        else:
            server = smtplib.SMTP(server_name, port)
            server.starttls()
        
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ SUCCESS with {server_name}:{port}!")
        break
        
    except Exception as e:
        print(f"❌ Failed: {e}")