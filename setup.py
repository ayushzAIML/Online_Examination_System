#!/usr/bin/env python3
"""
Online Examination System Setup Script
Automated installation and initialization
"""

import subprocess
import sys
import os
import json
import sqlite3
from pathlib import Path

class ExamSystemSetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.requirements = [
            'matplotlib>=3.5.0',
            'numpy>=1.20.0',
            'reportlab>=3.6.0',
            'Pillow>=8.0.0'
        ]
        
    def install_dependencies(self):
        """Install required Python packages."""
        print("📦 Installing dependencies...")
        
        for package in self.requirements:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                print("Continuing with setup...")
    
    def create_database(self):
        """Create fresh database with sample data."""
        print("🗄️ Creating database...")
        
        # Import and initialize database
        try:
            from database import ExamDatabase
            
            # Initialize database
            db = ExamDatabase()
            
            # Create default users
            print("Creating default users...")
            db.create_user("admin", "admin123", "Administrator")
            db.create_user("student1", "password123", "Demo Student 1")
            db.create_user("student2", "password456", "Demo Student 2")
            
            # Add sample questions
            sample_questions = [
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct": 2,
                    "category": "Geography",
                    "difficulty": "Easy",
                    "points": 1,
                    "explanation": "Paris is the capital and largest city of France."
                },
                {
                    "question": "Which programming language is known as the 'language of the web'?",
                    "options": ["Python", "JavaScript", "Java", "C++"],
                    "correct": 1,
                    "category": "Technology",
                    "difficulty": "Easy",
                    "points": 1,
                    "explanation": "JavaScript is primarily used for web development and is often called the language of the web."
                },
                {
                    "question": "What is 2 + 2 × 3?",
                    "options": ["10", "8", "12", "6"],
                    "correct": 1,
                    "category": "Mathematics",
                    "difficulty": "Medium",
                    "points": 2,
                    "explanation": "Following order of operations: 2 + (2 × 3) = 2 + 6 = 8"
                },
                {
                    "question": "Who wrote 'Romeo and Juliet'?",
                    "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                    "correct": 1,
                    "category": "Literature",
                    "difficulty": "Easy",
                    "points": 1,
                    "explanation": "William Shakespeare wrote the famous tragedy Romeo and Juliet."
                },
                {
                    "question": "What is the chemical symbol for gold?",
                    "options": ["Go", "Gd", "Au", "Ag"],
                    "correct": 2,
                    "category": "Science",
                    "difficulty": "Medium",
                    "points": 2,
                    "explanation": "Au comes from the Latin word 'aurum' meaning gold."
                },
                {
                    "question": "Which planet is closest to the Sun?",
                    "options": ["Venus", "Mercury", "Earth", "Mars"],
                    "correct": 1,
                    "category": "Science",
                    "difficulty": "Easy",
                    "points": 1,
                    "explanation": "Mercury is the smallest planet and closest to the Sun in our solar system."
                },
                {
                    "question": "What is the largest continent by area?",
                    "options": ["Africa", "North America", "Asia", "Europe"],
                    "correct": 2,
                    "category": "Geography",
                    "difficulty": "Easy",
                    "points": 1,
                    "explanation": "Asia is the largest continent covering about 30% of Earth's total land area."
                },
                {
                    "question": "In which year did World War II end?",
                    "options": ["1944", "1945", "1946", "1943"],
                    "correct": 1,
                    "category": "History",
                    "difficulty": "Medium",
                    "points": 2,
                    "explanation": "World War II ended in 1945 with the surrender of Japan in September."
                },
                {
                    "question": "What is the square root of 64?",
                    "options": ["6", "7", "8", "9"],
                    "correct": 2,
                    "category": "Mathematics",
                    "difficulty": "Easy",
                    "points": 1,
                    "explanation": "√64 = 8 because 8 × 8 = 64"
                },
                {
                    "question": "Which of these is NOT a programming paradigm?",
                    "options": ["Object-Oriented", "Functional", "Procedural", "Alphabetical"],
                    "correct": 3,
                    "category": "Technology",
                    "difficulty": "Hard",
                    "points": 3,
                    "explanation": "Alphabetical is not a programming paradigm. The main paradigms include Object-Oriented, Functional, and Procedural."
                }
            ]
            
            # Add questions to database
            for q in sample_questions:
                db.add_question(
                    q["question"], 
                    q["options"][0], q["options"][1], q["options"][2], q["options"][3],
                    chr(ord('A') + q["correct"]),  # Convert index to letter (0->A, 1->B, etc.)
                    q["category"], q["difficulty"], q["points"], q["explanation"]
                )
            
            print("✅ Database created with sample questions")
            
        except Exception as e:
            print(f"❌ Database creation failed: {e}")
    
    def create_config(self):
        """Create or update configuration file."""
        print("⚙️ Creating configuration...")
        
        config = {
            "exam": {
                "duration_minutes": 30,
                "questions_per_exam": 10,
                "randomize_questions": True,
                "randomize_options": True,
                "show_results_immediately": True,
                "allow_review": True,
                "time_warnings": [10, 5, 1]
            },
            "ui": {
                "theme": {
                    "primary": "#2E86AB",
                    "secondary": "#A23B72", 
                    "success": "#F18F01",
                    "danger": "#C73E1D",
                    "light": "#F5F5F5",
                    "dark": "#333333"
                },
                "window": {
                    "width": 1000,
                    "height": 700,
                    "resizable": True
                },
                "fonts": {
                    "default_family": "Arial",
                    "default_size": 12,
                    "title_size": 16,
                    "header_size": 14
                }
            },
            "database": {
                "filename": "exam_system.db",
                "backup_enabled": True,
                "backup_interval_days": 7
            },
            "security": {
                "session_timeout_minutes": 60,
                "max_login_attempts": 3,
                "password_min_length": 6
            }
        }
        
        with open(self.project_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Configuration created")
    
    def verify_files(self):
        """Verify all required files exist."""
        print("🔍 Verifying files...")
        
        required_files = [
            'main.py',
            'database.py', 
            'config.py',
            'pdf_generator.py',
            'config.json'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required files present")
        return True
    
    def test_system(self):
        """Test basic system functionality."""
        print("🧪 Testing system...")
        
        try:
            # Test imports
            from database import ExamDatabase
            from config import ExamConfig
            
            # Test database connection
            db = ExamDatabase()
            questions = db.get_questions(limit=5)
            
            if len(questions) > 0:
                print("✅ System test passed")
                return True
            else:
                print("⚠️ No questions found in database")
                return False
                
        except Exception as e:
            print(f"❌ System test failed: {e}")
            return False
    
    def full_setup(self):
        """Run complete setup process."""
        print("🚀 Starting Online Examination System Setup...\n")
        
        steps = [
            ("Installing Dependencies", self.install_dependencies),
            ("Creating Configuration", self.create_config),
            ("Creating Database", self.create_database),
            ("Verifying Files", self.verify_files),
            ("Testing System", self.test_system)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}")
            print("-" * 40)
            try:
                result = step_func()
                if result is False:
                    print(f"❌ Setup failed at: {step_name}")
                    return False
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                return False
        
        print("\n🎉 Setup completed successfully!")
        print("\n📖 Quick Start:")
        print("   python main.py")
        print("\n🔑 Default Credentials:")
        print("   Admin: admin / admin123")
        print("   Student: student1 / password123")
        print("\n📚 Check README.md for detailed usage instructions")
        
        return True
    
    def reset_system(self):
        """Reset system to clean state."""
        print("🔄 Resetting system...")
        
        # Remove database
        db_file = self.project_dir / 'exam_system.db'
        if db_file.exists():
            db_file.unlink()
            print("✅ Database removed")
        
        # Recreate everything
        self.create_config()
        self.create_database()
        
        print("✅ System reset complete")

def main():
    setup = ExamSystemSetup()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'reset':
            setup.reset_system()
        elif sys.argv[1] == 'install':
            setup.full_setup()
        else:
            print("Usage: python setup.py [install|reset]")
    else:
        setup.full_setup()

if __name__ == "__main__":
    main()
