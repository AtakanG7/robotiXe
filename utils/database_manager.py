import sqlite3
from datetime import datetime
import json
import streamlit as st

class DatabaseManager:
    def __init__(self, db_path="chat_sessions.db"):
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Ensure all tables exist before any operation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    github_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT,
                    avatar_url TEXT,
                    first_auth_time TIMESTAMP NOT NULL,
                    last_auth_time TIMESTAMP NOT NULL
                )
            """)
            
            # Create daily interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    github_id TEXT NOT NULL,
                    interaction_date DATE NOT NULL,
                    question_count INTEGER DEFAULT 0,
                    last_interaction_time TIMESTAMP,
                    FOREIGN KEY (github_id) REFERENCES users (github_id),
                    UNIQUE (github_id, interaction_date)
                )
            """)
            
            # Create chat sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    github_id TEXT NOT NULL,
                    session_start TIMESTAMP NOT NULL,
                    session_end TIMESTAMP,
                    pdf_name TEXT,
                    chat_history TEXT,
                    FOREIGN KEY (github_id) REFERENCES users (github_id)
                )
            """)
            
            conn.commit()

    def can_ask_question(self, github_id):
        """Check if user can ask another question today"""
        today = datetime.now().date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT question_count 
                FROM daily_interactions 
                WHERE github_id = ? AND interaction_date = ?
            """, (github_id, today))
            
            result = cursor.fetchone()
            return not result or result[0] < 3

    def increment_question_count(self, github_id):
        """Increment user's daily question count"""
        current_time = datetime.now()
        today = current_time.date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO daily_interactions (github_id, interaction_date, question_count, last_interaction_time)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(github_id, interaction_date) DO UPDATE SET
                    question_count = question_count + 1,
                    last_interaction_time = excluded.last_interaction_time
            """, (github_id, today, current_time))
            conn.commit()

    def get_user_stats(self, github_id):
        """Get user's stats"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    u.username,
                    u.first_auth_time,
                    u.last_auth_time,
                    COALESCE(d.question_count, 0) as today_questions
                FROM users u
                LEFT JOIN daily_interactions d ON 
                    u.github_id = d.github_id AND 
                    d.interaction_date = date('now')
                WHERE u.github_id = ?
            """, (github_id,))
            
            return cursor.fetchone()

    def record_authentication(self, user_data):
        """Record user authentication"""
        current_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (
                    github_id, username, email, avatar_url, 
                    first_auth_time, last_auth_time
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(github_id) DO UPDATE SET
                    username = excluded.username,
                    email = excluded.email,
                    avatar_url = excluded.avatar_url,
                    last_auth_time = excluded.last_auth_time
            """, (
                str(user_data['id']),
                user_data['login'],
                user_data.get('email', ''),
                user_data.get('avatar_url', ''),
                current_time,
                current_time
            ))
            conn.commit()

    def create_chat_session(self, github_id, pdf_name):
        """Create a new chat session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (github_id, session_start, pdf_name, chat_history)
                VALUES (?, ?, ?, ?)
            """, (github_id, datetime.now(), pdf_name, json.dumps([])))
            return cursor.lastrowid

    def update_chat_history(self, session_id, chat_history):
        """Update chat history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE chat_sessions 
                SET chat_history = ?
                WHERE id = ?
            """, (json.dumps(chat_history), session_id))
            conn.commit()

    def get_user_sessions(self, github_id):
        """Get all chat sessions for a user"""
        with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id,
                        pdf_name,
                        session_start,
                        chat_history,
                        (SELECT COUNT(*) FROM json_each(chat_history)) / 2 as message_count
                    FROM chat_sessions 
                    WHERE github_id = ?
                    ORDER BY session_start DESC
                """, (github_id,))
                
                return cursor.fetchall()

    def get_session_history(self, session_id):
        """Get chat history for a specific session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT chat_history
                FROM chat_sessions 
                WHERE id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return []