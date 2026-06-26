import sqlite3
import os

def create_database():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = sqlite3.connect('data/it_support.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            symptoms TEXT,
            solution TEXT NOT NULL,
            difficulty TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            issue_description TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    solutions = [
        ('Network', 'No Internet Connection', 
         'Cannot access websites, network icon shows red X',
         'STEP 1: Check if Ethernet cable is properly plugged in\n'
         'STEP 2: Restart your router/modem (wait 30 seconds)\n'
         'STEP 3: Open Command Prompt as Admin and run:\n'
         '   ipconfig /release\n'
         '   ipconfig /renew\n'
         '   ipconfig /flushdns\n'
         'STEP 4: Check if other devices can connect',
         'Easy'),
        
        ('Printer', 'Printer Not Printing',
         'Print jobs stuck in queue, printer shows offline',
         'STEP 1: Check printer is turned ON and connected\n'
         'STEP 2: Open Services (Win+R, type services.msc)\n'
         'STEP 3: Find "Print Spooler" -> Right-click -> Restart\n'
         'STEP 4: Clear print queue\n'
         'STEP 5: Reinstall printer drivers if needed',
         'Medium'),
        
        ('System', 'Computer Freezing',
         'Screen frozen, mouse not moving, apps not responding',
         'STEP 1: Wait 2-3 minutes (system might recover)\n'
         'STEP 2: Press Ctrl+Alt+Delete -> Task Manager\n'
         'STEP 3: End unresponsive tasks\n'
         'STEP 4: Restart computer if still frozen\n'
         'STEP 5: Run Windows Update\n'
         'STEP 6: Check for malware with Windows Defender',
         'Medium'),
        
        ('Software', 'Cannot Install Application',
         'Installation fails, error messages, permission denied',
         'STEP 1: Right-click installer -> Run as Administrator\n'
         'STEP 2: Temporarily disable antivirus\n'
         'STEP 3: Check available disk space\n'
         'STEP 4: Clear temp files (Win+R, type %temp%)\n'
         'STEP 5: Run Windows Update',
         'Medium')
    ]
    
    cursor.executemany('''
        INSERT INTO solutions (category, problem, symptoms, solution, difficulty)
        VALUES (?, ?, ?, ?, ?)
    ''', solutions)
    
    conn.commit()
    conn.close()
    
    print("Database created successfully with sample solutions!")

if __name__ == "__main__":
    create_database()