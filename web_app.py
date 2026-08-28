from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot import ITSupportChatbot
import sqlite3
import uuid

app = Flask(__name__)
CORS(app)
chatbot = ITSupportChatbot()

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
    user_id = data.get('user_id', str(uuid.uuid4()))
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = chatbot.process_message(user_id, message)
    response['user_id'] = user_id
    
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
    conn = sqlite3.connect('data/it_support.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets ORDER BY created_date DESC')
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tickets)

@app.route('/api/resolve/<int:ticket_id>', methods=['POST'])
def resolve_ticket(ticket_id):
    """Mark a ticket as resolved"""
    try:
        conn = sqlite3.connect('data/it_support.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET status = 'Resolved', resolved_date = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (ticket_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Ticket #{ticket_id} resolved'})
    except Exception as e:
        print(f"Error resolving ticket: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# START THE SERVER
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
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting IT Support Chatbot...")
    print(f"👤 User Chat:     http://0.0.0.0:{port}")
    print(f"📊 Admin Tickets: http://0.0.0.0:{port}/admin/tickets")
    app.run(debug=False, host='0.0.0.0', port=port)