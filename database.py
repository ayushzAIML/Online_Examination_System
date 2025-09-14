import sqlite3
import hashlib
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ExamDatabase:
    def __init__(self, db_name: str = "exam_system.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Create tables for users and questions."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL
        )
        ''')
        
        # Create questions table with enhanced fields
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            difficulty TEXT DEFAULT 'Medium',
            points INTEGER DEFAULT 1,
            explanation TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create exam_results table with enhanced fields
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            total_points INTEGER DEFAULT 0,
            time_taken INTEGER DEFAULT 0,
            category_scores TEXT DEFAULT '{}',
            difficulty_scores TEXT DEFAULT '{}',
            exam_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create exam_sessions table for tracking exam progress
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP NULL,
            questions_data TEXT NOT NULL,
            user_answers TEXT DEFAULT '{}',
            is_completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, full_name: str) -> bool:
        """Create a new user account."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
                (username, password_hash, full_name)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Username already exists
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login and return user info if successful."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT id, username, full_name FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[2]
            }
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user information by username."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, full_name FROM users WHERE username = ?",
            (username,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[2]
            }
        return None
    
    def add_question(self, question: str, option_a: str, option_b: str, 
                    option_c: str, option_d: str, correct_option: str, 
                    category: str = "General", difficulty: str = "Medium", 
                    points: int = 1, explanation: str = "") -> bool:
        """Add a new question to the database with enhanced fields."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO questions (question, option_a, option_b, option_c, option_d, 
                                     correct_option, category, difficulty, points, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (question, option_a, option_b, option_c, option_d, correct_option, 
                  category, difficulty, points, explanation))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def get_questions(self, limit: int = 10, category: str = None, 
                     difficulty: str = None, randomize: bool = True) -> List[Dict]:
        """Get questions from database with filtering and randomization."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, question, option_a, option_b, option_c, option_d, 
                   correct_option, category, difficulty, points, explanation 
            FROM questions WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        
        if randomize:
            query += " ORDER BY RANDOM()"
        else:
            query += " ORDER BY id"
        
        query += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        questions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': q[0],
                'question': q[1],
                'option_a': q[2],
                'option_b': q[3],
                'option_c': q[4],
                'option_d': q[5],
                'correct_option': q[6],
                'category': q[7],
                'difficulty': q[8],
                'points': q[9],
                'explanation': q[10]
            }
            for q in questions
        ]
    
    def save_exam_result(self, user_id: int, score: int, total_questions: int,
                        total_points: int = 0, time_taken: int = 0,
                        category_scores: Dict = None, difficulty_scores: Dict = None) -> bool:
        """Save exam result to database with enhanced analytics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            import json
            category_scores_json = json.dumps(category_scores or {})
            difficulty_scores_json = json.dumps(difficulty_scores or {})
            
            cursor.execute(
                """INSERT INTO exam_results 
                   (user_id, score, total_questions, total_points, time_taken, 
                    category_scores, difficulty_scores) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, score, total_questions, total_points, time_taken,
                 category_scores_json, difficulty_scores_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def get_user_results(self, user_id: int) -> List[Dict]:
        """Get exam history for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT score, total_questions, exam_date 
            FROM exam_results 
            WHERE user_id = ? 
            ORDER BY exam_date DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'score': r[0],
                'total_questions': r[1],
                'exam_date': r[2],
                'percentage': round((r[0] / r[1]) * 100, 2)
            }
            for r in results
        ]
    
    def get_categories(self) -> List[str]:
        """Get all available question categories."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM questions ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_difficulties(self) -> List[str]:
        """Get all available difficulty levels."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT difficulty FROM questions ORDER BY difficulty")
        difficulties = [row[0] for row in cursor.fetchall()]
        conn.close()
        return difficulties
    
    def get_question_stats(self) -> Dict:
        """Get statistics about questions in database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total questions
        cursor.execute("SELECT COUNT(*) FROM questions")
        total = cursor.fetchone()[0]
        
        # By category
        cursor.execute("SELECT category, COUNT(*) FROM questions GROUP BY category")
        by_category = dict(cursor.fetchall())
        
        # By difficulty
        cursor.execute("SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty")
        by_difficulty = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total': total,
            'by_category': by_category,
            'by_difficulty': by_difficulty
        }
    
    def get_detailed_analytics(self, user_id: int, limit: int = 10) -> Dict:
        """Get detailed performance analytics for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Recent results
        cursor.execute("""
            SELECT score, total_questions, total_points, time_taken, 
                   category_scores, difficulty_scores, exam_date
            FROM exam_results 
            WHERE user_id = ? 
            ORDER BY exam_date DESC 
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {}
        
        import json
        analytics = {
            'total_exams': len(results),
            'average_score': sum(r[0] for r in results) / len(results),
            'average_percentage': sum((r[0]/r[1])*100 for r in results) / len(results),
            'best_score': max(r[0] for r in results),
            'recent_performance': [],
            'category_performance': {},
            'difficulty_performance': {},
            'time_analysis': {
                'average_time': sum(r[3] for r in results if r[3]) / len([r for r in results if r[3]]) if any(r[3] for r in results) else 0,
                'fastest_time': min(r[3] for r in results if r[3]) if any(r[3] for r in results) else 0
            }
        }
        
        # Process each result
        for result in results:
            score, total, points, time_taken, cat_scores, diff_scores, date = result
            percentage = (score / total) * 100
            
            analytics['recent_performance'].append({
                'date': date,
                'score': score,
                'total': total,
                'percentage': round(percentage, 2),
                'time_taken': time_taken
            })
            
            # Category performance
            if cat_scores:
                try:
                    cat_data = json.loads(cat_scores)
                    for category, cat_score in cat_data.items():
                        if category not in analytics['category_performance']:
                            analytics['category_performance'][category] = []
                        analytics['category_performance'][category].append(cat_score)
                except json.JSONDecodeError:
                    pass
            
            # Difficulty performance
            if diff_scores:
                try:
                    diff_data = json.loads(diff_scores)
                    for difficulty, diff_score in diff_data.items():
                        if difficulty not in analytics['difficulty_performance']:
                            analytics['difficulty_performance'][difficulty] = []
                        analytics['difficulty_performance'][difficulty].append(diff_score)
                except json.JSONDecodeError:
                    pass
        
        return analytics

    def populate_sample_data(self):
        """Add sample users and questions for testing."""
        # Add sample users
        self.create_user("student1", "password123", "John Doe")
        self.create_user("student2", "password456", "Jane Smith")
        self.create_user("admin", "admin123", "Admin User")
        
        # Add sample questions with enhanced fields
        sample_questions = [
            {
                "question": "What is the capital of France?",
                "option_a": "London",
                "option_b": "Berlin",
                "option_c": "Paris",
                "option_d": "Madrid",
                "correct_option": "C",
                "category": "Geography",
                "difficulty": "Easy",
                "points": 1,
                "explanation": "Paris is the capital and most populous city of France."
            },
            {
                "question": "Which programming language is known for its simplicity and readability?",
                "option_a": "C++",
                "option_b": "Python",
                "option_c": "Assembly",
                "option_d": "Java",
                "correct_option": "B",
                "category": "Programming",
                "difficulty": "Easy",
                "points": 1,
                "explanation": "Python is designed to be simple and readable, making it great for beginners."
            },
            {
                "question": "What is 2 + 2?",
                "option_a": "3",
                "option_b": "4",
                "option_c": "5",
                "option_d": "6",
                "correct_option": "B",
                "category": "Mathematics",
                "difficulty": "Easy",
                "points": 1,
                "explanation": "Basic addition: 2 + 2 = 4"
            },
            {
                "question": "Which planet is closest to the Sun?",
                "option_a": "Venus",
                "option_b": "Earth",
                "option_c": "Mercury",
                "option_d": "Mars",
                "correct_option": "C",
                "category": "Science",
                "difficulty": "Medium",
                "points": 2,
                "explanation": "Mercury is the innermost planet in our solar system."
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "option_a": "Charles Dickens",
                "option_b": "William Shakespeare",
                "option_c": "Jane Austen",
                "option_d": "Mark Twain",
                "correct_option": "B",
                "category": "Literature",
                "difficulty": "Medium",
                "points": 2,
                "explanation": "William Shakespeare wrote this famous tragedy around 1594-1596."
            },
            {
                "question": "What is the largest mammal in the world?",
                "option_a": "African Elephant",
                "option_b": "Blue Whale",
                "option_c": "Giraffe",
                "option_d": "Hippopotamus",
                "correct_option": "B",
                "category": "Biology",
                "difficulty": "Easy",
                "points": 1,
                "explanation": "Blue whales can grow up to 100 feet long and weigh up to 200 tons."
            },
            {
                "question": "In which year did World War II end?",
                "option_a": "1944",
                "option_b": "1945",
                "option_c": "1946",
                "option_d": "1947",
                "correct_option": "B",
                "category": "History",
                "difficulty": "Medium",
                "points": 2,
                "explanation": "World War II ended in 1945 with the surrender of Japan in September."
            },
            {
                "question": "What is the chemical symbol for gold?",
                "option_a": "Go",
                "option_b": "Gd",
                "option_c": "Au",
                "option_d": "Ag",
                "correct_option": "C",
                "category": "Chemistry",
                "difficulty": "Hard",
                "points": 3,
                "explanation": "Au comes from the Latin word 'aurum' meaning gold."
            },
            {
                "question": "Which continent is known as the 'Dark Continent'?",
                "option_a": "Asia",
                "option_b": "Africa",
                "option_c": "South America",
                "option_d": "Australia",
                "correct_option": "B",
                "category": "Geography",
                "difficulty": "Medium",
                "points": 2,
                "explanation": "Africa was called the 'Dark Continent' due to European lack of knowledge about it."
            },
            {
                "question": "What is the time complexity of binary search?",
                "option_a": "O(n)",
                "option_b": "O(log n)",
                "option_c": "O(n²)",
                "option_d": "O(1)",
                "correct_option": "B",
                "category": "Programming",
                "difficulty": "Hard",
                "points": 3,
                "explanation": "Binary search eliminates half the elements in each step, giving O(log n) complexity."
            },
            {
                "question": "What is the derivative of x²?",
                "option_a": "x",
                "option_b": "2x",
                "option_c": "x²",
                "option_d": "2",
                "correct_option": "B",
                "category": "Mathematics",
                "difficulty": "Hard",
                "points": 3,
                "explanation": "Using the power rule: d/dx(x²) = 2x^(2-1) = 2x"
            },
            {
                "question": "Which gas makes up approximately 78% of Earth's atmosphere?",
                "option_a": "Oxygen",
                "option_b": "Carbon Dioxide",
                "option_c": "Nitrogen",
                "option_d": "Argon",
                "correct_option": "C",
                "category": "Science",
                "difficulty": "Medium",
                "points": 2,
                "explanation": "Nitrogen (N₂) makes up about 78% of Earth's atmosphere."
            }
        ]
        
        for q in sample_questions:
            self.add_question(**q)
