import sqlite3
import os

class KnowledgeManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'it_support.db')
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def search_solutions(self, query, category=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        
        if category:
            cursor.execute('''
                SELECT * FROM solutions 
                WHERE (problem LIKE ? OR symptoms LIKE ?) 
                AND category = ?
                LIMIT 5
            ''', (search_term, search_term, category))
        else:
            cursor.execute('''
                SELECT * FROM solutions 
                WHERE problem LIKE ? OR symptoms LIKE ?
                LIMIT 5
            ''', (search_term, search_term))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def create_ticket(self, user_id, issue, priority="Medium", staff_name="", staff_email=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (user_id, staff_name, staff_email, issue_description, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, staff_name, staff_email, issue, priority))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    
    def get_all_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM solutions ORDER BY category')
        categories = [row['category'] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def add_solution(self, category, problem, symptoms, solution, difficulty):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO solutions (category, problem, symptoms, solution, difficulty)
            VALUES (?, ?, ?, ?, ?)
        ''', (category, problem, symptoms, solution, difficulty))
        conn.commit()
        conn.close()
        return True