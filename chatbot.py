from knowledge_manager import KnowledgeManager
from ai_engine import AIEngine
import os

# Try to import email notifier, but don't crash if it fails
try:
    from email_notifier import EmailNotifier
    HAS_EMAIL = True
except:
    HAS_EMAIL = False
    print("Email notifier not available - tickets will still work")

class ITSupportChatbot:
    def __init__(self):
        self.knowledge = KnowledgeManager()
        self.ai = AIEngine()
        if HAS_EMAIL:
            self.email = EmailNotifier()
        self.user_sessions = {}
        
        all_solutions = self.knowledge.search_solutions("")
        if all_solutions:
            self.ai.prepare_solutions(all_solutions)
    
    def process_message(self, user_id, message):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'attempts': 0,
                'category': None,
                'last_issue': None,
                'awaiting_feedback': False
            }
        
        session = self.user_sessions[user_id]
        message_lower = message.lower().strip()
        
        if session.get('awaiting_feedback'):
            return self._handle_feedback(user_id, message_lower, session)
        
        if self._is_greeting(message_lower):
            return self._handle_greeting()
        
        if self._is_farewell(message_lower):
            return self._handle_farewell()
        
        if self._should_escalate(message_lower):
            return self._escalate_issue(user_id, session)
        
        category = self._detect_category(message_lower)
        if category:
            session['category'] = category
        
        session['last_issue'] = message
        
        ai_results = self.ai.find_best_match(message)
        kb_results = self.knowledge.search_solutions(message, category)
        
        if ai_results and ai_results[0]['confidence'] > 30:
            session['awaiting_feedback'] = True
            return self._format_solution_response(ai_results[0])
        elif kb_results:
            session['awaiting_feedback'] = True
            return self._format_kb_response(kb_results[0])
        else:
            session['attempts'] += 1
            if session['attempts'] >= 3:
                return self._escalate_issue(user_id, session)
            return self._ask_more_details(session)
    
    def _handle_feedback(self, user_id, message, session):
        positive_words = ['yes', 'yeah', 'yep', 'great', 'worked', 'working', 'solved',
                          'fixed', 'thanks', 'thank you', 'perfect', 'awesome', 'done',
                          'ok', 'okay', 'fine', 'good', 'helped', 'resolved']
        negative_words = ['no', 'nope', 'not', 'still', 'didn\'t', 'doesn\'t', 'escalate',
                          'help', 'did not', 'not working', 'still broken']
        
        if any(word in message for word in positive_words) and not any(word in message for word in negative_words):
            session['awaiting_feedback'] = False
            session['attempts'] = 0
            return {
                'message': "Great! I'm glad that helped! 😊\n\nIs there anything else I can assist you with?",
                'type': 'feedback_positive'
            }
        elif any(word in message for word in negative_words) or 'escalate' in message:
            session['awaiting_feedback'] = False
            return self._escalate_issue(user_id, session)
        else:
            return {
                'message': "I didn't quite catch that. Did the solution work?\n\n• Type 'yes' if it worked\n• Type 'escalate' if you still need help",
                'type': 'clarification'
            }
    
    def _is_greeting(self, text):
        greetings = ['hi', 'hello', 'hey', 'good morning', 'help', 'yo']
        return any(greet in text for greet in greetings)
    
    def _is_farewell(self, text):
        farewells = ['thank', 'thanks', 'bye', 'goodbye', 'appreciate', 'great', 'awesome']
        return any(word in text for word in farewells)
    
    def _handle_greeting(self):
        response = (
            "👋 Hello! I'm your IT Support Assistant.\n\n"
            "I can help with:\n"
            "• Network Issues\n"
            "• Printer Problems\n"
            "• System Freezing\n"
            "• Software Installation\n\n"
            "Just describe your problem and I'll guide you!\n"
            "For example: 'My printer is not working'"
        )
        return {'message': response, 'type': 'greeting'}
    
    def _handle_farewell(self):
        response = "You're welcome! 😊 Type 'help' anytime you need assistance."
        return {'message': response, 'type': 'farewell'}
    
    def _detect_category(self, text):
        categories = {
            'Network': ['network', 'internet', 'wifi', 'ethernet', 'connection', 'dns', 'ip', 'router'],
            'Printer': ['printer', 'print', 'scan', 'paper', 'toner', 'ink', 'jam'],
            'System': ['freeze', 'slow', 'crash', 'blue screen', 'bsod', 'hang', 'stuck', 'restart'],
            'Software': ['install', 'app', 'application', 'software', 'program', 'office', 'excel', 'word']
        }
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        return None
    
    def _should_escalate(self, text):
        escalation_phrases = ['escalate', 'not helping', 'still not working', 'didn\'t work',
                              'talk to human', 'real person', 'it team', 'urgent', 'critical']
        return any(phrase in text for phrase in escalation_phrases)
    
    def _format_solution_response(self, ai_result):
        solution = ai_result['solution']
        confidence = ai_result['confidence']
        response = (
            f"🎯 Here's what I recommend:\n\n"
            f"{solution['solution']}\n\n"
            f"📊 Difficulty: {solution['difficulty']}\n"
            f"📂 Category: {solution['category']}\n\n"
            f"Did this solve your problem?\n"
            f"• Type 'yes' if it worked\n"
            f"• Type 'escalate' if you still need help"
        )
        return {'message': response, 'type': 'solution', 'solution': solution, 'confidence': confidence}
    
    def _format_kb_response(self, solution):
        response = (
            f"💡 I found this solution:\n\n"
            f"{solution['solution']}\n\n"
            f"📊 Difficulty: {solution['difficulty']}\n"
            f"📂 Category: {solution['category']}\n\n"
            f"Did this solve your problem?\n"
            f"• Type 'yes' if it worked\n"
            f"• Type 'escalate' if you still need help"
        )
        return {'message': response, 'type': 'solution', 'solution': solution, 'confidence': 75}
    
    def _ask_more_details(self, session):
        attempts = session.get('attempts', 1)
        if attempts == 1:
            response = (
                "I need more details to help better. Can you tell me:\n\n"
                "• What exactly is happening?\n"
                "• When did it start?\n"
                "• Any error messages?\n\n"
                "The more details, the better I can help!"
            )
        else:
            response = (
                "I'm still having trouble finding the right solution.\n\n"
                "Try:\n"
                "• Describing the problem differently\n"
                "• Mentioning specific error codes\n"
                "• Or type 'escalate' to contact IT staff directly"
            )
        return {'message': response, 'type': 'clarification'}
    
    def _escalate_issue(self, user_id, session):
        priority = 'Medium'
        if session.get('category') == 'System':
            priority = 'High'
        
        last_issue = session.get('last_issue', 'Issue escalated by user')
        
        try:
            ticket_id = self.knowledge.create_ticket(user_id, last_issue, priority)
            
            # Try sending email if available
            if HAS_EMAIL:
                try:
                    import threading
                    email_thread = threading.Thread(
                        target=self.email.send_ticket_notification,
                        args=(ticket_id, user_id, last_issue, priority),
                        daemon=True 
                    )
                except Exception as e:
                    print(f"Email notification failed: {e}")
            
            # Reset session
            self.user_sessions[user_id] = {
                'attempts': 0,
                'category': None,
                'last_issue': None,
                'awaiting_feedback': False
            }
            
            return {
                'message': (
                    f"🚨 SUPPORT TICKET CREATED!\n\n"
                    f"🎫 Ticket ID: #{ticket_id}\n"
                    f"⚡ Priority: {priority}\n"
                    f"📋 Status: Open\n\n"
                    f"An IT staff member will address this shortly.\n\n"
                    f"💡 While waiting, you can try restarting your computer."
                ),
                'type': 'escalation',
                'ticket_id': ticket_id,
                'priority': priority
            }
        
        except Exception as e:
            print(f"Ticket creation failed: {e}")
            # Even if ticket fails, reset session
            self.user_sessions[user_id] = {
                'attempts': 0,
                'category': None,
                'last_issue': None,
                'awaiting_feedback': False
            }
            return {
                'message': (
                    f"⚠️ I've noted your issue. The IT team will be notified.\n\n"
                    f"Is there anything else I can help with?"
                ),
                'type': 'escalation',
                'ticket_id': None
            }