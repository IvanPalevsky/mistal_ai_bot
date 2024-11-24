import sqlite3

def save_feedback(user_id, feedback_text):
    conn = sqlite3.connect('feedback.db')
    cur = conn.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback
            (id INTEGER PRIMARY KEY,
            user_id INTEGER,
            feedback TEXT)
    ''')
    
    cur.execute('INSERT INTO feedback (user_id, feedback) VALUES (?, ?)', (user_id, feedback_text))
    
    conn.commit()
    conn.close()