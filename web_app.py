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
    conn = sqlite3.connect('data/it_support.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets 
        SET status = 'Resolved', resolved_date = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============================================
# START THE SERVER
# ============================================

if __name__ == '__main__':
    print("🚀 Starting IT Support Chatbot...")
    print("=" * 50)
    print("👤 User Chat:     http://localhost:5000")
    print("📊 Admin Tickets: http://localhost:5000/admin/tickets")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)