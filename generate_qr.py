import qrcode
import socket

# Get your IP address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# URLs
chat_url = f"http://{ip_address}:5000"
admin_url = f"http://{ip_address}:5000/admin/tickets"

# Generate QR code for user chat
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(chat_url)
qr.make(fit=True)

img = qr.make_image(fill_color="#014711", back_color="white")
img.save("static/chat_qr.png")

print(f"✅ QR Code generated!")
print(f"📱 Chat URL: {chat_url}")
print(f"📊 Admin URL: {admin_url}")
print(f"📍 QR saved to: static/chat_qr.png")