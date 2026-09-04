from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from chatbot import ITSupportChatbot
import sqlite3
import uuid
import os
import csv
import io

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
    
    cursor.execute('DROP TABLE IF EXISTS tickets')
    
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
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            sender TEXT,
            message TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with staff columns and messages table")

init_db()

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
    try:
        data = request.json
        user_id = data.get('user_id', data.get('staff_email', str(uuid.uuid4())))
        staff_name = data.get('staff_name', '')
        staff_email = data.get('staff_email', user_id)
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        response = chatbot.process_message(user_id, message, staff_name=staff_name, staff_email=staff_email)
        response['user_id'] = user_id
        response['staff_name'] = staff_name
        
        return jsonify(response)
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'message': f'❌ Error processing message: {str(e)}', 'type': 'error'}), 500

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
# MESSAGING ROUTES
# ============================================

@app.route('/api/ticket/<int:ticket_id>/messages', methods=['GET'])
def get_messages(ticket_id):
    """Get all messages for a ticket"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE ticket_id = ? ORDER BY created_date ASC', (ticket_id,))
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(messages)
    except Exception as e:
        print(f"Error getting messages: {e}")
        return jsonify([])

@app.route('/api/ticket/<int:ticket_id>/send', methods=['POST'])
def send_message(ticket_id):
    """Send a message from IT support"""
    try:
        data = request.json
        sender = data.get('sender', 'IT Support')
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message'}), 400
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (ticket_id, sender, message)
            VALUES (?, ?, ?)
        ''', (ticket_id, sender, message))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>/messages', methods=['GET'])
def get_user_messages(user_id):
    """Get messages for a user's ticket"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM tickets 
            WHERE user_id = ? OR staff_email = ?
            ORDER BY created_date DESC 
            LIMIT 1
        ''', (user_id, user_id))
        
        ticket = cursor.fetchone()
        
        if not ticket:
            conn.close()
            return jsonify([])
        
        ticket_id = ticket['id']
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE ticket_id = ? 
            ORDER BY created_date ASC
        ''', (ticket_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(messages)
    except Exception as e:
        print(f"Error getting user messages: {e}")
        return jsonify([])

@app.route('/api/user/<user_id>/reply', methods=['POST'])
def user_reply(user_id):
    """User replies to IT support message"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message'}), 400
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, staff_name FROM tickets 
            WHERE user_id = ? OR staff_email = ?
            ORDER BY created_date DESC 
            LIMIT 1
        ''', (user_id, user_id))
        
        ticket = cursor.fetchone()
        
        if not ticket:
            conn.close()
            return jsonify({'error': 'No ticket found'}), 404
        
        ticket_id = ticket['id']
        sender = ticket['staff_name'] or 'Staff'
        
        cursor.execute('''
            INSERT INTO messages (ticket_id, sender, message)
            VALUES (?, ?, ?)
        ''', (ticket_id, sender, message))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error sending reply: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# EXPORT ROUTES
# ============================================

@app.route('/api/export-tickets')
def export_tickets():
    """Export tickets as CSV for Excel"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets ORDER BY created_date DESC')
        tickets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Ticket ID', 'Staff Name', 'Staff Email', 'Issue', 'Priority', 'Status', 'Created Date', 'Resolved Date'])
        
        for ticket in tickets:
            writer.writerow([
                ticket.get('id', ''),
                ticket.get('staff_name', ''),
                ticket.get('staff_email', ''),
                ticket.get('issue_description', ''),
                ticket.get('priority', ''),
                ticket.get('status', ''),
                ticket.get('created_date', ''),
                ticket.get('resolved_date', '')
            ])
        
        csv_data = output.getvalue()
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=it_tickets_report.csv'}
        )
    
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get monthly statistics"""
    try:
        from datetime import datetime
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        current_month = datetime.now().strftime('%Y-%m')
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_tickets,
                SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) as high_priority,
                SUM(CASE WHEN priority = 'Medium' THEN 1 ELSE 0 END) as medium_priority,
                SUM(CASE WHEN priority = 'Critical' THEN 1 ELSE 0 END) as critical_priority
            FROM tickets 
            WHERE created_date LIKE ?
        """, (current_month + '%',))
        
        month_stats = dict(cursor.fetchone())
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN issue_description LIKE '%printer%' OR issue_description LIKE '%print%' THEN 'Printer'
                    WHEN issue_description LIKE '%network%' OR issue_description LIKE '%internet%' OR issue_description LIKE '%wifi%' THEN 'Network'
                    WHEN issue_description LIKE '%freez%' OR issue_description LIKE '%slow%' OR issue_description LIKE '%crash%' THEN 'System'
                    WHEN issue_description LIKE '%install%' OR issue_description LIKE '%software%' OR issue_description LIKE '%app%' THEN 'Software'
                    ELSE 'Other'
                END as category,
                COUNT(*) as count
            FROM tickets
            WHERE created_date LIKE ?
            GROUP BY category
        """, (current_month + '%',))
        
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'month': current_month,
            'month_stats': month_stats,
            'categories': categories
        })
    
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500

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