from zoho_email_api import ZohoEmailAPI

print("Testing Zoho API email...")

email = ZohoEmailAPI()

result = email.send_email(
    to_email="support@agmasiltd.com",
    subject="Test from IT Chatbot",
    body="This is a test email using Zoho API!"
)

if result:
    print("✅ SUCCESS! Check support@agmasiltd.com inbox!")
else:
    print("❌ Failed. Check the error above.")