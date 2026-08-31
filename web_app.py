from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot import ITSupportChatbot
import sqlite3
import uuid
import os

app = Flask(__name__)
CORS(app)
chatbot = ITSupportChatbot()

# Create database if it doesn't exist
def init_db():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            staff_name TEXT,
            staff_email TEXT,
            issue_description TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# ============================================
# USER CHAT ROUTES
# ============================================

@app.route('/')
def home():
    """Main chat interface for users"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat"""
    data = request.json
    user_id = data.get('user_id', data.get('staff_email', str(uuid.uuid4())))
    staff_name = data.get('staff_name', '')
    staff_email = data.get('staff_email', user_id)
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Pass staff info to chatbot
    response = chatbot.process_message(user_id, message, staff_name=staff_name, staff_email=staff_email)
    response['user_id'] = user_id
    response['staff_name'] = staff_name
    
    return jsonify(response)

# ============================================
# IT SUPPORT TEAM - TICKET DASHBOARD
# ============================================

@app.route('/admin/tickets')
def admin_dashboard():
    """IT Admin dashboard to view all tickets"""
    return render_template('admin_tickets.html')

@app.route('/api/tickets')
def get_tickets():
    """API to get all tickets"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets ORDER BY created_date DESC')
        tickets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(tickets)
    except Exception as e:
        print(f"Error fetching tickets: {e}")
        return jsonify([])

@app.route('/api/resolve/<int:ticket_id>', methods=['POST'])
def resolve_ticket(ticket_id):
    """Mark a ticket as resolved"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET status = 'Resolved'
            WHERE id = ?
        ''', (ticket_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error resolving ticket: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# EMAIL TEST
# ============================================

@app.route('/test-email')
def test_email():
    """Test email sending"""
    try:
        from sendgrid_notifier import SendGridNotifier
        sg = SendGridNotifier()
        
        if not sg.api_key:
            return "❌ API Key is empty! Add SENDGRID_API_KEY to Render Environment."
        
        result = sg.send_email(
            "agmasiltd@gmail.com",
            "Test from IT Chatbot",
            "This is a test email!"
        )
        
        if result:
            return "✅ Email sent! Check agmasiltd@gmail.com"
        else:
            return "❌ Email failed. Check Render logs."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================
# START THE SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting IT Support Chatbot...")
    print(f"👤 User Chat:     http://0.0.0.0:{port}")
    print(f"📊 Admin Tickets: http://0.0.0.0:{port}/admin/tickets")
    app.run(debug=False, host='0.0.0.0', port=port)