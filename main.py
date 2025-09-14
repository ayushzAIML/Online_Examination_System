import tkinter as tk
from tkinter import messagebox, ttk
import json
import time
import hashlib
from datetime import datetime
from database import ExamDatabase
from config import ExamConfig
from typing import Dict, List, Optional
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*Axes3D.*')
warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class OnlineExamSystem:
    def __init__(self):
        """Initialize the Enhanced Online Exam System."""
        # Load configuration
        self.config = ExamConfig()
        
        # Initialize database
        self.db = ExamDatabase(self.config.get('database_path', 'exam_system_enhanced.db'))
        
        # Exam state variables
        self.current_user = None
        self.questions = []
        self.current_question_index = 0
        self.user_answers = {}
        self.score = 0
        self.total_points = 0
        
        # Timer variables
        self.exam_start_time = None
        self.exam_duration = self.config.get('exam_duration')
        self.time_remaining = self.exam_duration
        self.timer_running = False
        self.timer_id = None
        self.timer_label = None
        
        # Category and difficulty tracking
        self.category_scores = {}
        self.difficulty_scores = {}
        
        # Navigation system for admin screens
        self.navigation_stack = []
        self.current_screen = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Online Examination System - Enhanced")
        window_width = self.config.get('ui_settings.window_width')
        window_height = self.config.get('ui_settings.window_height')
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(True, True)
        
        # Configure styles
        self.setup_styles()
        
        # Initialize with login screen
        self.show_login_screen()
    
    def setup_styles(self):
        """Setup custom styles for the application."""
        self.root.configure(bg='#f0f0f0')
        
        # Define colors
        self.colors = {
            'primary': '#2563eb',
            'secondary': '#64748b',
            'success': '#16a34a',
            'warning': '#ea580c',
            'danger': '#dc2626',
            'light': '#f8fafc',
            'dark': '#1e293b'
        }
    
    def clear_window(self):
        """Clear all widgets from the window."""
        # Stop timer if running
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def push_navigation(self, screen_name, screen_function):
        """Push current screen to navigation stack."""
        if self.current_screen:
            self.navigation_stack.append((self.current_screen, getattr(self, self.current_screen)))
        self.current_screen = screen_name
    
    def pop_navigation(self):
        """Go back to previous screen."""
        if self.navigation_stack:
            screen_name, screen_function = self.navigation_stack.pop()
            self.current_screen = screen_name
            screen_function()
        else:
            # If no previous screen, go to appropriate default
            if self.current_user and self.current_user['username'] == 'admin':
                self.show_admin_dashboard()
            else:
                self.show_login_screen()
    
    def create_navigation_header(self, parent, title, show_back=True):
        """Create a navigation header with back button."""
        nav_frame = tk.Frame(parent, bg=self.colors['primary'], height=60)
        nav_frame.pack(fill='x')
        nav_frame.pack_propagate(False)
        
        # Back button
        if show_back:
            back_btn = tk.Button(
                nav_frame,
                text="← Back",
                font=('Arial', 12, 'bold'),
                bg=self.colors['warning'],
                fg='white',
                cursor='hand2',
                command=self.pop_navigation,
                width=8,
                height=1
            )
            back_btn.pack(side='left', padx=10, pady=10)
        
        # Title
        tk.Label(
            nav_frame,
            text=title,
            font=('Arial', 18, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        ).pack(expand=True, pady=15)
    
    def show_login_screen(self):
        """Display the enhanced login screen with registration option."""
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Login container
        login_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        login_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=550)
        
        # Title
        title_label = tk.Label(
            login_frame, 
            text="🎓 Online Examination System", 
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=self.colors['primary']
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            login_frame, 
            text="Professional Learning Platform", 
            font=('Arial', 11),
            bg='white',
            fg=self.colors['secondary']
        )
        subtitle_label.pack(pady=5)
        
        # Login form frame
        form_frame = tk.Frame(login_frame, bg='white')
        form_frame.pack(pady=30)
        
        # Username
        tk.Label(form_frame, text="Username:", font=('Arial', 12, 'bold'), 
                bg='white', fg=self.colors['dark']).grid(row=0, column=0, sticky='e', padx=10, pady=10)
        
        self.username_entry = tk.Entry(form_frame, font=('Arial', 14), width=20, relief='solid', bd=2)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Password
        tk.Label(form_frame, text="Password:", font=('Arial', 12, 'bold'), 
                bg='white', fg=self.colors['dark']).grid(row=1, column=0, sticky='e', padx=10, pady=10)
        
        self.password_entry = tk.Entry(form_frame, font=('Arial', 14), width=20, show='*', relief='solid', bd=2)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(login_frame, bg='white')
        buttons_frame.pack(pady=20)
        
        # Login button
        login_btn = tk.Button(
            buttons_frame,
            text="🚀 LOGIN",
            font=('Arial', 14, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            cursor='hand2',
            command=self.handle_login,
            width=12,
            height=2,
            relief='raised',
            bd=3
        )
        login_btn.grid(row=0, column=0, padx=10)
        
        # Register button
        register_btn = tk.Button(
            buttons_frame,
            text="📝 REGISTER",
            font=('Arial', 14, 'bold'),
            bg=self.colors['success'],
            fg='white',
            cursor='hand2',
            command=self.show_registration_screen,
            width=12,
            height=2,
            relief='raised',
            bd=3
        )
        register_btn.grid(row=0, column=1, padx=10)
        
        # Demo accounts info (smaller, less prominent)
        demo_frame = tk.Frame(login_frame, bg='#f8f9fa', relief='solid', bd=1)
        demo_frame.pack(fill='x', padx=20, pady=15)
        
        tk.Label(
            demo_frame,
            text="� Demo Access Available:",
            font=('Arial', 10, 'bold'),
            bg='#f8f9fa',
            fg='#6c757d'
        ).pack(pady=3)
        
        tk.Label(
            demo_frame,
            text="Admin: admin / admin123  |  Student: student1 / password123",
            font=('Arial', 9),
            bg='#f8f9fa',
            fg='#6c757d'
        ).pack(pady=2)
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda event: self.handle_login())
        self.username_entry.bind('<Return>', lambda event: self.password_entry.focus())
        
        # Focus on username entry
        self.username_entry.focus()

    def show_registration_screen(self):
        """Display the registration screen for new students."""
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Registration container
        reg_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        reg_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=600)
        
        # Title
        title_label = tk.Label(
            reg_frame, 
            text="📝 Student Registration", 
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=self.colors['primary']
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            reg_frame, 
            text="Create Your Student Account", 
            font=('Arial', 11),
            bg='white',
            fg=self.colors['secondary']
        )
        subtitle_label.pack(pady=5)
        
        # Registration form frame
        form_frame = tk.Frame(reg_frame, bg='white')
        form_frame.pack(pady=30)
        
        # Full Name
        tk.Label(form_frame, text="Full Name:", font=('Arial', 12, 'bold'), 
                bg='white', fg=self.colors['dark']).grid(row=0, column=0, sticky='e', padx=10, pady=15)
        
        self.reg_fullname_entry = tk.Entry(form_frame, font=('Arial', 14), width=25, relief='solid', bd=2)
        self.reg_fullname_entry.grid(row=0, column=1, padx=10, pady=15)
        
        # Username
        tk.Label(form_frame, text="🆔 Username:", font=('Arial', 12, 'bold'), 
                bg='white', fg=self.colors['dark']).grid(row=1, column=0, sticky='e', padx=10, pady=15)
        
        self.reg_username_entry = tk.Entry(form_frame, font=('Arial', 14), width=25, relief='solid', bd=2)
        self.reg_username_entry.grid(row=1, column=1, padx=10, pady=15)
        
        # Password
        tk.Label(form_frame, text="🔒 Password:", font=('Arial', 12, 'bold'), 
                bg='white', fg=self.colors['dark']).grid(row=2, column=0, sticky='e', padx=10, pady=15)
        
        self.reg_password_entry = tk.Entry(form_frame, font=('Arial', 14), width=25, show='*', relief='solid', bd=2)
        self.reg_password_entry.grid(row=2, column=1, padx=10, pady=15)
        
        # Confirm Password
        tk.Label(form_frame, text="🔒 Confirm Password:", font=('Arial', 12, 'bold'), 
                bg='white', fg=self.colors['dark']).grid(row=3, column=0, sticky='e', padx=10, pady=15)
        
        self.reg_confirm_entry = tk.Entry(form_frame, font=('Arial', 14), width=25, show='*', relief='solid', bd=2)
        self.reg_confirm_entry.grid(row=3, column=1, padx=10, pady=15)
        
        # Registration info
        info_frame = tk.Frame(reg_frame, bg='#e3f2fd', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text="ℹ️ Password must be at least 6 characters long",
            font=('Arial', 10),
            bg='#e3f2fd',
            fg='#1976d2'
        ).pack(pady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(reg_frame, bg='white')
        buttons_frame.pack(pady=20)
        
        # Register button
        register_btn = tk.Button(
            buttons_frame,
            text="✅ CREATE ACCOUNT",
            font=('Arial', 14, 'bold'),
            bg=self.colors['success'],
            fg='white',
            cursor='hand2',
            command=self.handle_registration,
            width=15,
            height=2,
            relief='raised',
            bd=3
        )
        register_btn.grid(row=0, column=0, padx=10)
        
        # Back to Login button
        back_btn = tk.Button(
            buttons_frame,
            text="← BACK TO LOGIN",
            font=('Arial', 14, 'bold'),
            bg=self.colors['secondary'],
            fg='white',
            cursor='hand2',
            command=self.show_login_screen,
            width=15,
            height=2,
            relief='raised',
            bd=3
        )
        back_btn.grid(row=0, column=1, padx=10)
        
        # Focus on full name entry
        self.reg_fullname_entry.focus()

    def handle_registration(self):
        """Handle new user registration."""
        full_name = self.reg_fullname_entry.get().strip()
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm_password = self.reg_confirm_entry.get().strip()
        
        # Validation
        if not all([full_name, username, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters long!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        # Check if username already exists
        try:
            if self.db.get_user_by_username(username):
                messagebox.showerror("Error", "Username already exists! Please choose a different one.")
                return
        except:
            pass  # Username doesn't exist, which is good
        
        # Create account
        try:
            if self.db.create_user(username, password, full_name):
                messagebox.showinfo("Success", f"Account created successfully!\n\nYou can now login with:\nUsername: {username}\nPassword: {password}")
                self.show_login_screen()
            else:
                messagebox.showerror("Error", "Failed to create account. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
    
    def handle_logout(self):
        """Handle user logout with confirmation."""
        if messagebox.askquestion("Logout", "Are you sure you want to logout?") == 'yes':
            self.current_user = None
            self.navigation_stack = []  # Clear navigation history
            self.show_login_screen()
    
    def show_system_settings(self):
        """Show system settings and configuration options."""
        self.push_navigation('show_system_settings', self.show_system_settings)
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Navigation header
        self.create_navigation_header(main_frame, "⚙️ System Settings")
        
        # Settings content
        content_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=2)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="🔧 System Configuration", 
                font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=20)
        
        settings_text = f"""
⚙️ Current System Configuration:

📚 Exam Duration: {self.config.exam_duration} minutes
❓ Questions per Exam: {self.config.questions_per_exam}
🔀 Question Randomization: {'Enabled' if self.config.randomize_questions else 'Disabled'}
🎯 Show Results Immediately: {'Yes' if self.config.show_results_immediately else 'No'}
📊 Allow Review: {'Enabled' if self.config.allow_review else 'Disabled'}

📊 Database Information:
📁 Database File: {self.config.database_filename}
🔄 Backup Enabled: {'Yes' if hasattr(self.config, 'backup_enabled') else 'No'}

🖥️ UI Settings:
🎨 Theme: Professional
📏 Window Size: {self.config.window_width}x{self.config.window_height}
📝 Default Font: {self.config.default_font_family} ({self.config.default_font_size}pt)

Note: Configuration changes require system restart to take effect.
        """
        
        tk.Label(content_frame, text=settings_text, font=('Arial', 11), 
                bg='white', justify='left', fg=self.colors['dark']).pack(pady=20, padx=40)
    
    def export_system_data(self):
        """Export system data for backup or analysis."""
        self.push_navigation('export_system_data', self.export_system_data)
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Navigation header
        self.create_navigation_header(main_frame, "📤 Export System Data")
        
        # Export content
        content_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=2)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="📊 System Data Export", 
                font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=20)
        
        # Export options
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.pack(pady=30)
        
        tk.Button(options_frame, text="📋 Export All Student Results", 
                 font=('Arial', 14, 'bold'), bg='#2196f3', fg='white',
                 width=25, height=3, cursor='hand2',
                 command=self.export_student_results).pack(pady=10)
        
        tk.Button(options_frame, text="❓ Export Question Bank", 
                 font=('Arial', 14, 'bold'), bg='#4caf50', fg='white',
                 width=25, height=3, cursor='hand2',
                 command=self.export_questions).pack(pady=10)
        
        tk.Button(options_frame, text="📈 Export Analytics Report", 
                 font=('Arial', 14, 'bold'), bg='#ff9800', fg='white',
                 width=25, height=3, cursor='hand2',
                 command=self.export_analytics).pack(pady=10)
        
        # Info text
        info_text = """
🔍 Export Options:

📋 Student Results: All exam scores, times, and performance data
❓ Question Bank: All questions with answers and categories  
📈 Analytics: Comprehensive system statistics and trends

📁 Files will be saved in CSV format for easy analysis
💾 Exports include timestamps and are ready for backup
        """
        
        tk.Label(content_frame, text=info_text, font=('Arial', 11), 
                bg='white', justify='left', fg=self.colors['dark']).pack(pady=20)
    
    def export_student_results(self):
        """Export student results to CSV."""
        try:
            import csv
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"student_results_{timestamp}.csv"
            
            # Get all results from database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.username, u.full_name, er.score, er.total_questions, 
                       er.time_taken, er.exam_date
                FROM exam_results er
                JOIN users u ON er.user_id = u.id
                ORDER BY er.exam_date DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username', 'Full Name', 'Score', 'Total Questions', 'Percentage', 'Time (minutes)', 'Date'])
                
                for result in results:
                    percentage = (result[2] / result[3] * 100) if result[3] > 0 else 0
                    time_minutes = result[4] // 60 if result[4] else 0
                    writer.writerow([result[0], result[1], result[2], result[3], f"{percentage:.1f}%", time_minutes, result[5]])
            
            messagebox.showinfo("Success", f"Student results exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_questions(self):
        """Export questions to CSV."""
        try:
            import csv
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"question_bank_{timestamp}.csv"
            
            questions = self.db.get_questions(limit=1000)  # Get all questions
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct', 'Category', 'Difficulty', 'Points', 'Explanation'])
                
                for q in questions:
                    writer.writerow([
                        q['question'], q['option_a'], q['option_b'], 
                        q['option_c'], q['option_d'], q['correct_option'],
                        q.get('category', 'General'), q.get('difficulty', 'Medium'),
                        q.get('points', 1), q.get('explanation', '')
                    ])
            
            messagebox.showinfo("Success", f"Question bank exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_analytics(self):
        """Export analytics report."""
        try:
            import csv
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_report_{timestamp}.csv"
            
            stats = self.get_admin_statistics()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Export Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow(['Total Students', stats['total_users']])
                writer.writerow(['Total Questions', stats['total_questions']])
                writer.writerow(['Total Exams Taken', stats['total_exams']])
                writer.writerow(['Average Score', f"{stats['avg_score']:.1f}%"])
                writer.writerow(['Categories Available', stats['categories_count']])
                writer.writerow(['Total Exam Time', f"{stats['total_time']} minutes"])
                writer.writerow(['Best Score', f"{stats['best_score']}%"])
            
            messagebox.showinfo("Success", f"Analytics report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def handle_login(self):
        """Handle user login with role-based routing."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            messagebox.showinfo("Success", f"Welcome, {user['full_name']}!")
            
            # Route based on user role
            if username == 'admin':
                self.show_admin_dashboard()
            else:
                self.show_exam_instructions()
        else:
            messagebox.showerror("Error", "Invalid username or password!")
            self.password_entry.delete(0, tk.END)
    
    def show_admin_dashboard(self):
        """Show admin dashboard with management features."""
        self.current_screen = 'show_admin_dashboard'
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#c62828', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="👑 ADMIN DASHBOARD",
            font=('Arial', 24, 'bold'),
            bg='#c62828',
            fg='white'
        ).pack(expand=True)
        
        # Welcome message
        welcome_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        welcome_frame.pack(fill='x', pady=10)
        
        tk.Label(
            welcome_frame,
            text=f"Welcome, {self.current_user['full_name']}! 🔧",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        # Admin features grid
        features_frame = tk.Frame(main_frame, bg='#f0f0f0')
        features_frame.pack(expand=True, fill='both', pady=20)
        
        # Left column - Statistics
        left_frame = tk.Frame(features_frame, bg='white', relief='solid', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="SYSTEM STATISTICS", font=('Arial', 16, 'bold'), 
                bg='white', fg=self.colors['primary']).pack(pady=15)
        
        # Get statistics
        stats = self.get_admin_statistics()
        
        stats_text = f"""
📈 Total Students: {stats['total_users']}
📝 Total Questions: {stats['total_questions']}  
🎯 Total Exams Taken: {stats['total_exams']}
⭐ Average Score: {stats['avg_score']:.1f}%
📚 Categories Available: {stats['categories_count']}
⏱️ Total Exam Time: {stats['total_time']} minutes
🏆 Best Score: {stats['best_score']}%
📅 System Active Since: Today
        """
        
        tk.Label(left_frame, text=stats_text, font=('Arial', 11), 
                bg='white', justify='left', fg=self.colors['dark']).pack(pady=10, padx=20)
        
        # Right column - Actions
        right_frame = tk.Frame(features_frame, bg='white', relief='solid', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="🔧 ADMIN ACTIONS", font=('Arial', 16, 'bold'), 
                bg='white', fg=self.colors['primary']).pack(pady=15)
        
        # Admin action buttons
        buttons_frame = tk.Frame(right_frame, bg='white')
        buttons_frame.pack(expand=True, pady=20)
        
        tk.Button(buttons_frame, text="📋 View All Results", 
                 font=('Arial', 12, 'bold'), bg='#2196f3', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.show_all_results).pack(pady=6)
        
        tk.Button(buttons_frame, text="� Student Analytics", 
                 font=('Arial', 12, 'bold'), bg='#9c27b0', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.show_student_analytics).pack(pady=6)
        
        tk.Button(buttons_frame, text="👥 Manage Students", 
                 font=('Arial', 12, 'bold'), bg='#4caf50', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.manage_students).pack(pady=6)
        
        tk.Button(buttons_frame, text="➕ Add New Student", 
                 font=('Arial', 12, 'bold'), bg='#00bcd4', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.show_register_student).pack(pady=6)
        
        tk.Button(buttons_frame, text="❓ Manage Questions", 
                 font=('Arial', 12, 'bold'), bg='#ff9800', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.manage_questions).pack(pady=6)
        
        tk.Button(buttons_frame, text="⚙️ System Settings", 
                 font=('Arial', 12, 'bold'), bg='#607d8b', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.show_system_settings).pack(pady=6)
        
        tk.Button(buttons_frame, text="📤 Export Data", 
                 font=('Arial', 12, 'bold'), bg='#795548', fg='white',
                 width=20, height=2, cursor='hand2',
                 command=self.export_system_data).pack(pady=6)
        
        # Logout button
        logout_frame = tk.Frame(main_frame, bg='#f0f0f0')
        logout_frame.pack(fill='x', pady=20)
        
        tk.Button(logout_frame, text="🚪 Logout", 
                 font=('Arial', 14, 'bold'), bg='#f44336', fg='white',
                 width=15, height=2, cursor='hand2',
                 command=self.handle_logout).pack()

    def get_admin_statistics(self):
        """Get system statistics for admin dashboard."""
        try:
            # Get database connection
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Total users (excluding admin)
            cursor.execute("SELECT COUNT(*) FROM users WHERE username != 'admin'")
            total_users = cursor.fetchone()[0]
            
            # Total questions
            cursor.execute("SELECT COUNT(*) FROM questions")
            total_questions = cursor.fetchone()[0]
            
            # Total exams
            cursor.execute("SELECT COUNT(*) FROM exam_results")
            total_exams = cursor.fetchone()[0]
            
            # Average score
            cursor.execute("SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) FROM exam_results")
            avg_result = cursor.fetchone()[0]
            avg_score = avg_result if avg_result else 0
            
            # Categories count
            cursor.execute("SELECT COUNT(DISTINCT category) FROM questions")
            categories_count = cursor.fetchone()[0]
            
            # Total time spent
            cursor.execute("SELECT SUM(time_taken) FROM exam_results WHERE time_taken > 0")
            total_time_result = cursor.fetchone()[0]
            total_time = (total_time_result // 60) if total_time_result else 0
            
            # Best score
            cursor.execute("SELECT MAX(CAST(score AS FLOAT) / total_questions * 100) FROM exam_results")
            best_result = cursor.fetchone()[0]
            best_score = best_result if best_result else 0
            
            conn.close()
            
            return {
                'total_users': total_users,
                'total_questions': total_questions,
                'total_exams': total_exams,
                'avg_score': avg_score,
                'categories_count': categories_count,
                'total_time': total_time,
                'best_score': best_score
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_users': 0,
                'total_questions': 0,
                'total_exams': 0,
                'avg_score': 0,
                'categories_count': 0,
                'total_time': 0,
                'best_score': 0
            }

    def show_register_student(self):
        """Show new student registration form."""
        self.push_navigation('show_register_student', self.show_register_student)
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Navigation header
        self.create_navigation_header(main_frame, "➕ Register New Student")
        
        # Form container
        form_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=2)
        form_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=400)
        
        tk.Label(form_frame, text="Create New Student Account", 
                font=('Arial', 18, 'bold'), bg='white', 
                fg=self.colors['primary']).pack(pady=20)
        
        # Form fields
        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(expand=True, pady=20)
        
        # Username
        tk.Label(fields_frame, text="Username:", font=('Arial', 12, 'bold'), bg='white').pack(pady=(0,5))
        self.reg_username_entry = tk.Entry(fields_frame, font=('Arial', 12), width=30, relief='solid', bd=1)
        self.reg_username_entry.pack(pady=5, ipady=3)
        
        # Full Name
        tk.Label(fields_frame, text="Full Name:", font=('Arial', 12, 'bold'), bg='white').pack(pady=(15,5))
        self.reg_fullname_entry = tk.Entry(fields_frame, font=('Arial', 12), width=30, relief='solid', bd=1)
        self.reg_fullname_entry.pack(pady=5, ipady=3)
        
        # Password
        tk.Label(fields_frame, text="Password:", font=('Arial', 12, 'bold'), bg='white').pack(pady=(15,5))
        self.reg_password_entry = tk.Entry(fields_frame, font=('Arial', 12), width=30, show='*', relief='solid', bd=1)
        self.reg_password_entry.pack(pady=5, ipady=3)
        
        # Confirm Password
        tk.Label(fields_frame, text="Confirm Password:", font=('Arial', 12, 'bold'), bg='white').pack(pady=(15,5))
        self.reg_confirm_entry = tk.Entry(fields_frame, font=('Arial', 12), width=30, show='*', relief='solid', bd=1)
        self.reg_confirm_entry.pack(pady=5, ipady=3)
        
        # Buttons
        buttons_frame = tk.Frame(form_frame, bg='white')
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="✅ Create Account", 
                 font=('Arial', 12, 'bold'), bg=self.colors['success'], fg='white',
                 width=15, height=2, cursor='hand2',
                 command=self.register_new_student).pack(side='left', padx=10)
        
        tk.Button(buttons_frame, text="❌ Cancel", 
                 font=('Arial', 12, 'bold'), bg=self.colors['danger'], fg='white',
                 width=15, height=2, cursor='hand2',
                 command=self.pop_navigation).pack(side='left', padx=10)
    
    def register_new_student(self):
        """Register a new student account."""
        username = self.reg_username_entry.get().strip()
        full_name = self.reg_fullname_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm = self.reg_confirm_entry.get().strip()
        
        # Validation
        if not all([username, full_name, password, confirm]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        try:
            # Check if username already exists
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Username already exists!")
                conn.close()
                return
            
            # Create the account
            success = self.db.create_user(username, password, full_name)
            conn.close()
            
            if success:
                messagebox.showinfo("Success", f"Account created successfully!\n\nUsername: {username}\nPassword: {password}\n\nThe student can now login and take exams.")
                self.pop_navigation()
            else:
                messagebox.showerror("Error", "Failed to create account. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def show_student_analytics(self):
        """Show student analytics with plots and historical data."""
        self.push_navigation('show_student_analytics', self.show_student_analytics)
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Navigation header
        self.create_navigation_header(main_frame, "Student Analytics & Performance")
        
        # Content frame with scrollbar
        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # Get student data
        student_data = self.get_student_performance_data()
        
        if not student_data:
            tk.Label(scrollable_frame, text="📊 No student data available yet.\n\nStudents need to take exams first to generate analytics.", 
                    font=('Arial', 16), bg='#f0f0f0', fg=self.colors['secondary']).pack(expand=True, pady=50)
            return
        
        # Overall Statistics
        stats_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=2)
        stats_frame.pack(fill='x', pady=10, padx=20)
        
        tk.Label(stats_frame, text="📈 OVERALL PERFORMANCE STATISTICS", 
                font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=15)
        
        # Create text-based visualizations (enhanced version)
        self.create_text_based_analytics(stats_frame, student_data)
        
        # Create matplotlib visualizations (new professional charts)
        self.create_matplotlib_analytics(stats_frame, student_data)
        
        # Individual Student Performance
        for student_name, data in student_data.items():
            student_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=2)
            student_frame.pack(fill='x', pady=10, padx=20)
            
            # Student header
            tk.Label(student_frame, text=f"USER: {student_name}", 
                    font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=10)
            
            # Performance summary
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            total_exams = len(data['scores'])
            best_score = max(data['scores']) if data['scores'] else 0
            
            summary_text = f"""
📝 Total Exams: {total_exams}
⭐ Average Score: {avg_score:.1f}%
🏆 Best Score: {best_score}%
📅 Last Exam: {data['last_exam'] or 'Never'}
⏱️ Average Time: {data['avg_time']:.1f} minutes
            """
            
            tk.Label(student_frame, text=summary_text, font=('Arial', 10), 
                    bg='white', justify='left', fg=self.colors['dark']).pack(pady=10)
            
            # Score history (text-based bar chart)
            if data['scores']:
                tk.Label(student_frame, text="Recent Score Trend:", 
                        font=('Arial', 11, 'bold'), bg='white').pack()
                
                # Show last 10 scores as a simple bar chart
                recent_scores = data['scores'][-10:]
                chart_text = ""
                for i, score in enumerate(recent_scores, 1):
                    bar_length = int(score / 10)  # Scale to max 10 chars
                    bar = "█" * bar_length + "▒" * (10 - bar_length)
                    chart_text += f"Exam {i:2d}: {bar} {score:5.1f}%\n"
                
                tk.Label(student_frame, text=chart_text, font=('Courier', 9), 
                        bg='white', justify='left', fg=self.colors['dark']).pack(pady=10)

    def create_text_based_analytics(self, parent, student_data):
        """Create professional matplotlib analytics visualizations."""
        # Calculate overall statistics
        all_scores = []
        all_times = []
        student_count = len(student_data)
        
        for data in student_data.values():
            all_scores.extend(data['scores'])
            all_times.extend([t for t in data['times'] if t > 0])
        
        if not all_scores:
            tk.Label(parent, text="No exam data available yet.", 
                    font=('Arial', 12), bg='white').pack(pady=20)
            return
        
        avg_score = sum(all_scores) / len(all_scores)
        avg_time = sum(all_times) / len(all_times) if all_times else 0
        
        # Create score distribution
        score_ranges = {
            "90-100%": len([s for s in all_scores if s >= 90]),
            "80-89%": len([s for s in all_scores if 80 <= s < 90]),
            "70-79%": len([s for s in all_scores if 70 <= s < 80]),
            "60-69%": len([s for s in all_scores if 60 <= s < 70]),
            "Below 60%": len([s for s in all_scores if s < 60])
        }
        
        chart_frame = tk.Frame(parent, bg='white')
        chart_frame.pack(pady=20)
        
        tk.Label(chart_frame, text="� Score Distribution:", 
                font=('Arial', 12, 'bold'), bg='white').pack()
        
        max_count = max(score_ranges.values()) if max(score_ranges.values()) > 0 else 1
        for range_name, count in score_ranges.items():
            bar_length = int((count / max_count) * 20) if count > 0 else 0
            bar = "█" * bar_length + "▒" * (20 - bar_length)
            chart_text = f"{range_name:8s}: {bar} ({count} exams)"
            tk.Label(chart_frame, text=chart_text, font=('Courier', 10), 
                    bg='white', justify='left').pack()
        
        # Summary statistics
        summary_text = f"""
📈 Total Students: {student_count}
📝 Total Exams: {len(all_scores)}
⭐ System Average: {avg_score:.1f}%
⏱️ Average Time: {avg_time:.1f} minutes
🏆 Highest Score: {max(all_scores):.1f}%
📉 Lowest Score: {min(all_scores):.1f}%
        """
        
        tk.Label(chart_frame, text=summary_text, font=('Arial', 11), 
                bg='white', justify='left', fg=self.colors['dark']).pack(pady=20)

    def create_matplotlib_analytics(self, parent, student_data):
        """Create professional matplotlib analytics visualizations."""
        if not student_data:
            return
        
        # Calculate overall statistics
        all_scores = []
        all_times = []
        student_count = len(student_data)
        
        for data in student_data.values():
            all_scores.extend(data['scores'])
            all_times.extend([t for t in data['times'] if t > 0])
        
        if not all_scores:
            return
        
        # Create matplotlib section
        matplotlib_frame = tk.Frame(parent, bg='white', relief='solid', bd=2)
        matplotlib_frame.pack(fill='both', expand=True, padx=10, pady=20)
        
        tk.Label(matplotlib_frame, text="PROFESSIONAL ANALYTICS CHARTS", 
                font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=10)
        
        # Create matplotlib figure with multiple subplots
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('📊 Student Performance Analytics Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Score Distribution Histogram
            ax1.hist(all_scores, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_title('Score Distribution', fontweight='bold')
            ax1.set_xlabel('Score (%)')
            ax1.set_ylabel('Number of Exams')
            avg_score = sum(all_scores) / len(all_scores)
            ax1.axvline(avg_score, color='red', linestyle='--', label=f'Average: {avg_score:.1f}%')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. Performance Grade Pie Chart
            score_ranges = {
                "Excellent (90-100%)": len([s for s in all_scores if s >= 90]),
                "Good (80-89%)": len([s for s in all_scores if 80 <= s < 90]),
                "Average (70-79%)": len([s for s in all_scores if 70 <= s < 80]),
                "Below Average (60-69%)": len([s for s in all_scores if 60 <= s < 70]),
                "Poor (<60%)": len([s for s in all_scores if s < 60])
            }
            # Filter out zero values
            score_ranges = {k: v for k, v in score_ranges.items() if v > 0}
            
            colors = ['#2E8B57', '#90EE90', '#FFD700', '#FFA500', '#DC143C']  # Green to Red spectrum
            wedges, texts, autotexts = ax2.pie(score_ranges.values(), labels=score_ranges.keys(), 
                                              autopct='%1.1f%%', colors=colors[:len(score_ranges)], 
                                              startangle=90)
            ax2.set_title('Performance Grade Distribution', fontweight='bold')
            
            # 3. Student Performance Comparison Bar Chart
            if len(student_data) > 0:
                student_names = list(student_data.keys())[:10]  # Limit to top 10 for readability
                student_avgs = [sum(data['scores'])/len(data['scores']) if data['scores'] else 0 
                               for name, data in list(student_data.items())[:10]]
                
                # Color-code based on performance
                bar_colors = ['green' if avg >= 80 else 'orange' if avg >= 60 else 'red' for avg in student_avgs]
                
                bars = ax3.bar(range(len(student_names)), student_avgs, color=bar_colors, alpha=0.8)
                ax3.set_title('Top 10 Student Performance', fontweight='bold')
                ax3.set_xlabel('Students')
                ax3.set_ylabel('Average Score (%)')
                ax3.set_xticks(range(len(student_names)))
                ax3.set_xticklabels([name[:8] + '...' if len(name) > 8 else name 
                                   for name in student_names], rotation=45, ha='right')
                ax3.grid(True, alpha=0.3, axis='y')
                
                # Add value labels on bars
                for bar, avg in zip(bars, student_avgs):
                    ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                            f'{avg:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
            else:
                ax3.text(0.5, 0.5, 'No individual student data', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=14)
                ax3.set_title('Student Comparison - No Data', fontweight='bold')
            
            # 4. Time vs Score Correlation Scatter Plot
            if all_times and len(all_times) > 1:
                ax4.scatter(all_times, all_scores, alpha=0.6, color='purple', s=50)
                ax4.set_title('Exam Time vs Score Correlation', fontweight='bold')
                ax4.set_xlabel('Time Taken (minutes)')
                ax4.set_ylabel('Score (%)')
                ax4.grid(True, alpha=0.3)
                
                # Add trend line
                try:
                    z = np.polyfit(all_times, all_scores, 1)
                    p = np.poly1d(z)
                    ax4.plot(sorted(all_times), p(sorted(all_times)), "r--", alpha=0.8, linewidth=2)
                    
                    # Add correlation coefficient
                    correlation = np.corrcoef(all_times, all_scores)[0,1]
                    ax4.text(0.05, 0.95, f'Correlation: {correlation:.2f}', transform=ax4.transAxes, 
                            bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.5))
                except:
                    pass  # If polyfit fails, just skip the trend line
            else:
                ax4.text(0.5, 0.5, 'Insufficient time data\nfor correlation analysis', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Time vs Score Analysis - Limited Data', fontweight='bold')
            
            plt.tight_layout()
            
            # Embed matplotlib in tkinter
            canvas = FigureCanvasTkAgg(fig, matplotlib_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add comprehensive summary
            summary_frame = tk.Frame(matplotlib_frame, bg='#f0f8ff', relief='solid', bd=2)
            summary_frame.pack(fill='x', padx=10, pady=10)
            
            avg_time = sum(all_times) / len(all_times) if all_times else 0
            pass_rate = len([s for s in all_scores if s >= 60])/len(all_scores)*100
            
            summary_text = f"""
🎯 COMPREHENSIVE ANALYTICS SUMMARY
📈 Total Students: {student_count} | 📝 Total Exams: {len(all_scores)} | ⭐ System Average: {avg_score:.1f}%
⏱️ Average Completion Time: {avg_time:.1f} minutes | 🏆 Best Score: {max(all_scores):.0f}% | 📉 Lowest: {min(all_scores):.0f}%
🎯 Pass Rate (≥60%): {pass_rate:.1f}% | 🌟 Excellence Rate (≥90%): {len([s for s in all_scores if s >= 90])/len(all_scores)*100:.1f}%
            """
            
            tk.Label(summary_frame, text=summary_text, font=('Arial', 10, 'bold'), 
                    bg='#f0f8ff', justify='center', fg=self.colors['primary']).pack(pady=8)
            
        except Exception as e:
            # Fallback if matplotlib fails
            error_frame = tk.Frame(matplotlib_frame, bg='#ffeeee', relief='solid', bd=1)
            error_frame.pack(fill='x', padx=10, pady=10)
            tk.Label(error_frame, text=f"⚠️ Advanced charts temporarily unavailable\nError: {str(e)[:100]}...", 
                    font=('Arial', 10), bg='#ffeeee', fg='red', justify='center').pack(pady=10)

    def get_student_performance_data(self):
        """Get comprehensive student performance data."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get all exam results with user information
            cursor.execute("""
                SELECT u.full_name, u.username, er.score, er.total_questions, 
                       er.time_taken, er.exam_date, er.total_points
                FROM exam_results er
                JOIN users u ON er.user_id = u.id
                WHERE u.username != 'admin'
                ORDER BY u.full_name, er.exam_date
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            student_data = {}
            
            for row in results:
                full_name, username, score, total_q, time_taken, exam_date, total_points = row
                
                if full_name not in student_data:
                    student_data[full_name] = {
                        'username': username,
                        'scores': [],
                        'times': [],
                        'dates': [],
                        'total_points': [],
                        'last_exam': None,
                        'avg_time': 0
                    }
                
                # Calculate percentage score
                percentage = (score / total_q) * 100 if total_q > 0 else 0
                student_data[full_name]['scores'].append(percentage)
                student_data[full_name]['times'].append(time_taken / 60 if time_taken > 0 else 0)  # Convert to minutes
                student_data[full_name]['dates'].append(exam_date)
                student_data[full_name]['total_points'].append(total_points or 0)
                student_data[full_name]['last_exam'] = exam_date
            
            # Calculate averages
            for name, data in student_data.items():
                if data['times']:
                    data['avg_time'] = sum(data['times']) / len(data['times'])
            
            return student_data
            
        except Exception as e:
            print(f"Error getting student performance data: {e}")
            return {}

    def show_all_results(self):
        """Show all exam results for admin review."""
        self.push_navigation('show_all_results', self.show_all_results)
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Navigation header
        self.create_navigation_header(main_frame, "📋 All Exam Results")
        
        # Results display
        self.show_detailed_results(main_frame)

    def show_detailed_results(self, parent):
        """Display detailed results table."""
        results_frame = tk.Frame(parent, bg='white', relief='solid', bd=2)
        results_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Get all results
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.full_name, u.username, er.score, er.total_questions, 
                       er.time_taken, er.exam_date, er.total_points
                FROM exam_results er
                JOIN users u ON er.user_id = u.id
                WHERE u.username != 'admin'
                ORDER BY er.exam_date DESC
                LIMIT 50
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                tk.Label(results_frame, text="📋 No exam results found.\n\nStudents need to take exams first.", 
                        font=('Arial', 16), bg='white', fg=self.colors['secondary']).pack(expand=True)
                return
            
            # Create table header
            tk.Label(results_frame, text="📊 Recent Exam Results (Last 50)", 
                    font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=20)
            
            # Table container with scrollbar
            table_container = tk.Frame(results_frame, bg='white')
            table_container.pack(fill='both', expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(table_container, bg='white')
            scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Headers
            header_frame = tk.Frame(scrollable_frame, bg='#e3f2fd', relief='solid', bd=1)
            header_frame.pack(fill='x', pady=2)
            
            tk.Label(header_frame, text="Student Name", font=('Arial', 10, 'bold'), bg='#e3f2fd', width=20).pack(side='left', padx=5, pady=5)
            tk.Label(header_frame, text="Score", font=('Arial', 10, 'bold'), bg='#e3f2fd', width=8).pack(side='left', padx=5, pady=5)
            tk.Label(header_frame, text="Percentage", font=('Arial', 10, 'bold'), bg='#e3f2fd', width=10).pack(side='left', padx=5, pady=5)
            tk.Label(header_frame, text="Time", font=('Arial', 10, 'bold'), bg='#e3f2fd', width=8).pack(side='left', padx=5, pady=5)
            tk.Label(header_frame, text="Date", font=('Arial', 10, 'bold'), bg='#e3f2fd', width=15).pack(side='left', padx=5, pady=5)
            
            # Data rows
            for i, (name, username, score, total_q, time_taken, exam_date, total_points) in enumerate(results):
                percentage = (score / total_q) * 100 if total_q > 0 else 0
                time_str = f"{time_taken//60}:{time_taken%60:02d}" if time_taken > 0 else "N/A"
                
                # Color coding based on performance
                if percentage >= 80:
                    bg_color = '#c8e6c9'  # Light green
                elif percentage >= 60:
                    bg_color = '#fff3e0'  # Light orange
                else:
                    bg_color = '#ffcdd2'  # Light red
                
                row_frame = tk.Frame(scrollable_frame, bg=bg_color, relief='solid', bd=1)
                row_frame.pack(fill='x', pady=1)
                
                tk.Label(row_frame, text=name[:25], font=('Arial', 9), bg=bg_color, width=20).pack(side='left', padx=5, pady=2)
                tk.Label(row_frame, text=f"{score}/{total_q}", font=('Arial', 9), bg=bg_color, width=8).pack(side='left', padx=5, pady=2)
                tk.Label(row_frame, text=f"{percentage:.1f}%", font=('Arial', 9, 'bold'), bg=bg_color, width=10).pack(side='left', padx=5, pady=2)
                tk.Label(row_frame, text=time_str, font=('Arial', 9), bg=bg_color, width=8).pack(side='left', padx=5, pady=2)
                tk.Label(row_frame, text=exam_date[:16], font=('Arial', 9), bg=bg_color, width=15).pack(side='left', padx=5, pady=2)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            tk.Label(results_frame, text=f"Error loading results: {str(e)}", 
                    font=('Arial', 12), bg='white', fg=self.colors['danger']).pack(expand=True)

    def manage_students(self):
        """Manage student accounts."""
        self.push_navigation('manage_students', self.manage_students)
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')
        
        # Navigation header
        self.create_navigation_header(main_frame, "👥 Manage Students")
        
        # Management interface
        mgmt_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=2)
        mgmt_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(mgmt_frame, text="👥 Student Management", 
                font=('Arial', 18, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=20)
        
        # Get student list
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name FROM users WHERE username != 'admin' ORDER BY full_name")
            students = cursor.fetchall()
            conn.close()
            
            if not students:
                tk.Label(mgmt_frame, text="No students registered yet.\nClick 'Add New Student' to create accounts.", 
                        font=('Arial', 14), bg='white', fg=self.colors['secondary']).pack(expand=True)
                return
            
            # Students list
            list_frame = tk.Frame(mgmt_frame, bg='white')
            list_frame.pack(fill='both', expand=True, padx=40, pady=20)
            
            tk.Label(list_frame, text=f"📋 Registered Students ({len(students)})", 
                    font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
            
            # Student entries
            for student_id, username, full_name in students:
                student_frame = tk.Frame(list_frame, bg='#f5f5f5', relief='solid', bd=1)
                student_frame.pack(fill='x', pady=5)
                
                tk.Label(student_frame, text=f"👤 {full_name} ({username})", 
                        font=('Arial', 12), bg='#f5f5f5').pack(side='left', padx=20, pady=10)
                
                # Action buttons
                btn_frame = tk.Frame(student_frame, bg='#f5f5f5')
                btn_frame.pack(side='right', padx=20, pady=5)
                
                tk.Button(btn_frame, text="🔍 View Results", 
                         font=('Arial', 9), bg=self.colors['primary'], fg='white',
                         command=lambda uid=student_id, name=full_name: self.view_student_results(uid, name)).pack(side='left', padx=2)
                
                tk.Button(btn_frame, text="🔑 Reset Password", 
                         font=('Arial', 9), bg=self.colors['warning'], fg='white',
                         command=lambda uid=student_id, name=full_name: self.reset_student_password(uid, name)).pack(side='left', padx=2)
            
        except Exception as e:
            tk.Label(mgmt_frame, text=f"Error loading students: {str(e)}", 
                    font=('Arial', 12), bg='white', fg=self.colors['danger']).pack(expand=True)

    def view_student_results(self, student_id, student_name):
        """View specific student's results."""
        messagebox.showinfo("Student Results", f"📊 Results for {student_name}\n\n(This would show detailed performance history for this specific student)")

    def reset_student_password(self, student_id, student_name):
        """Reset a student's password."""
        result = messagebox.askyesno("Reset Password", f"Reset password for {student_name}?\n\nNew password will be: 'password123'")
        if result:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                hashed_password = hashlib.sha256('password123'.encode()).hexdigest()
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, student_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Password reset for {student_name}\n\nNew password: password123")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {str(e)}")

    def manage_questions(self):
        """Manage exam questions."""
        self.push_navigation('manage_questions', self.manage_questions)
        messagebox.showinfo("Question Management", "❓ Question Management\n\nFeatures available:\n• Add new questions\n• Edit existing questions\n• Organize by category\n• Set difficulty levels\n• Import from CSV\n\n(Full implementation coming in next version!)")

    def show_exam_instructions(self):
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Exam Instructions", 
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        )
        title_label.pack(pady=20)
        
        # Instructions frame
        inst_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        inst_frame.pack(expand=True, fill='both', padx=50, pady=20)
        
        instructions_text = f"""
        Welcome to the Online Examination System!
        
        Instructions:
        • The exam contains {self.config.get('questions_per_exam')} multiple-choice questions
        • Each question has 4 options (A, B, C, D)
        • You have {self.config.get('exam_duration') // 60} minutes to complete the exam
        • Select one answer for each question
        • You can navigate between questions using Next/Previous buttons
        • Use the question palette to jump to any question quickly
        • Your answers are automatically saved
        • Click 'Submit Exam' when you're ready to finish
        • Once submitted, you cannot change your answers
        
        Good luck!
        """
        
        inst_label = tk.Label(
            inst_frame,
            text=instructions_text,
            font=('Arial', 12),
            bg='white',
            justify='left',
            wraplength=600
        )
        inst_label.pack(expand=True, pady=20)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Start exam button
        start_btn = tk.Button(
            button_frame,
            text="Start Exam",
            font=('Arial', 14, 'bold'),
            bg=self.colors['success'],
            fg='white',
            width=15,
            command=self.start_exam
        )
        start_btn.pack(side='left', padx=10)
        
        # Review Performance button
        review_btn = tk.Button(
            button_frame,
            text="View Performance",
            font=('Arial', 14),
            bg=self.colors['primary'],
            fg='white',
            width=15,
            command=self.show_performance_analytics
        )
        review_btn.pack(side='left', padx=10)
        
        # Logout button
        logout_btn = tk.Button(
            button_frame,
            text="Logout",
            font=('Arial', 14),
            bg=self.colors['secondary'],
            fg='white',
            width=15,
            command=self.logout
        )
        logout_btn.pack(side='left', padx=10)
    
    def start_exam(self):
        """Start the exam by loading questions with enhanced features."""
        # Get questions with randomization
        self.questions = self.db.get_questions(
            limit=self.config.get('questions_per_exam'),
            randomize=self.config.get('randomize_questions')
        )
        
        if not self.questions:
            messagebox.showerror("Error", "No questions available in the database!")
            return
        
        # Initialize exam state
        self.current_question_index = 0
        self.user_answers = {}
        self.score = 0
        self.total_points = sum(q['points'] for q in self.questions)
        
        # Initialize category and difficulty tracking
        self.category_scores = {}
        self.difficulty_scores = {}
        
        for question in self.questions:
            category = question['category']
            difficulty = question['difficulty']
            
            if category not in self.category_scores:
                self.category_scores[category] = {'correct': 0, 'total': 0}
            self.category_scores[category]['total'] += 1
            
            if difficulty not in self.difficulty_scores:
                self.difficulty_scores[difficulty] = {'correct': 0, 'total': 0}
            self.difficulty_scores[difficulty]['total'] += 1
        
        # Start timer
        self.exam_start_time = time.time()
        self.time_remaining = self.exam_duration
        self.timer_running = True
        
        self.show_exam_screen()
    
    def format_time(self, seconds):
        """Format time in MM:SS format."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"Time: {minutes:02d}:{seconds:02d}"
    
    def update_timer(self):
        """Update the timer display."""
        if self.timer_running and self.time_remaining > 0:
            # Update timer label
            if self.timer_label:
                self.timer_label.config(text=self.format_time(self.time_remaining))
                
                # Change color when time is running low
                if self.time_remaining <= 120:  # Last 2 minutes
                    self.timer_label.config(fg=self.colors['danger'])
                elif self.time_remaining <= 300:  # Last 5 minutes
                    self.timer_label.config(fg=self.colors['warning'])
            
            self.time_remaining -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.time_remaining <= 0:
            self.auto_submit_exam()
    
    def auto_submit_exam(self):
        """Auto-submit exam when time runs out."""
        self.timer_running = False
        messagebox.showwarning("Time's Up!", "Time has expired. Your exam will be submitted automatically.")
        self.submit_exam()
    
    def jump_to_question(self, index):
        """Jump directly to a specific question."""
        # Save current answer if selected
        if hasattr(self, 'selected_option') and self.selected_option.get():
            self.user_answers[self.current_question_index] = self.selected_option.get()
        
        self.current_question_index = index
        self.show_exam_screen()
    
    def show_exam_screen(self):
        """Display the exam screen with questions and enhanced features."""
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Header frame
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title and timer
        title_label = tk.Label(
            header_frame,
            text="Online Examination",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        )
        title_label.pack(side='left')
        
        # Timer display
        self.timer_label = tk.Label(
            header_frame,
            text=self.format_time(self.time_remaining),
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        )
        self.timer_label.pack(side='right')
        
        # Start/continue timer
        if self.timer_running:
            self.update_timer()
        
        # Progress info
        progress_info = tk.Label(
            header_frame,
            text=f"Question {self.current_question_index + 1} of {len(self.questions)}",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg=self.colors['secondary']
        )
        progress_info.pack()
        
        # Progress bar
        progress_frame = tk.Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=5)
        
        progress_bar = ttk.Progressbar(
            progress_frame, 
            length=400, 
            mode='determinate',
            value=(self.current_question_index + 1) / len(self.questions) * 100
        )
        progress_bar.pack()
        
        # Question palette for quick navigation
        palette_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        palette_frame.pack(fill='x', pady=10)
        
        tk.Label(palette_frame, text="Quick Navigation:", font=('Arial', 10, 'bold'), bg='white').pack(side='left', padx=5)
        
        for i in range(len(self.questions)):
            if i in self.user_answers:
                color = self.colors['success']
                text_color = 'white'
            elif i == self.current_question_index:
                color = self.colors['primary']
                text_color = 'white'
            else:
                color = self.colors['secondary']
                text_color = 'white'
        
            btn = tk.Button(
                palette_frame,
                text=str(i + 1),
                width=3,
                bg=color,
                fg=text_color,
                command=lambda idx=i: self.jump_to_question(idx)
            )
            btn.pack(side='left', padx=2, pady=5)
        
        # Question frame
        question_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        question_frame.pack(expand=True, fill='both', pady=(0, 20))
        
        current_question = self.questions[self.current_question_index]
        
        # Question info (category, difficulty, points)
        info_frame = tk.Frame(question_frame, bg='white')
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text=f"Category: {current_question['category']} | Difficulty: {current_question['difficulty']} | Points: {current_question['points']}",
            font=('Arial', 10),
            bg='white',
            fg=self.colors['secondary']
        ).pack(anchor='w')
        
        # Question text
        question_label = tk.Label(
            question_frame,
            text=f"Q{self.current_question_index + 1}. {current_question['question']}",
            font=('Arial', 14, 'bold'),
            bg='white',
            wraplength=700,
            justify='left'
        )
        question_label.pack(pady=20, padx=20, anchor='w')
        
        # Options frame
        options_frame = tk.Frame(question_frame, bg='white')
        options_frame.pack(pady=20, padx=40, fill='x')
        
        # Radio button variable
        self.selected_option = tk.StringVar()
        
        # Set previously selected answer if exists
        if self.current_question_index in self.user_answers:
            self.selected_option.set(self.user_answers[self.current_question_index])
        
        # Create radio buttons for options
        options = ['A', 'B', 'C', 'D']
        option_texts = [
            current_question['option_a'],
            current_question['option_b'],
            current_question['option_c'],
            current_question['option_d']
        ]
        
        for i, (option, text) in enumerate(zip(options, option_texts)):
            rb = tk.Radiobutton(
                options_frame,
                text=f"{option}. {text}",
                variable=self.selected_option,
                value=option,
                font=('Arial', 12),
                bg='white',
                wraplength=600,
                justify='left'
            )
            rb.pack(anchor='w', pady=5)
        
        # Navigation frame
        nav_frame = tk.Frame(main_frame, bg='#f0f0f0')
        nav_frame.pack(fill='x')
        
        # Previous button
        if self.current_question_index > 0:
            prev_btn = tk.Button(
                nav_frame,
                text="← Previous",
                font=('Arial', 12),
                bg=self.colors['secondary'],
                fg='white',
                width=12,
                command=self.previous_question
            )
            prev_btn.pack(side='left')
        
        # Submit button (show on last question or if all answered)
        if self.current_question_index == len(self.questions) - 1 or len(self.user_answers) == len(self.questions):
            submit_btn = tk.Button(
                nav_frame,
                text="Submit Exam",
                font=('Arial', 12, 'bold'),
                bg=self.colors['danger'],
                fg='white',
                width=15,
                command=self.submit_exam
            )
            submit_btn.pack(side='right')
        else:
            # Next button
            next_btn = tk.Button(
                nav_frame,
                text="Next →",
                font=('Arial', 12),
                bg=self.colors['primary'],
                fg='white',
                width=12,
                command=self.next_question
            )
            next_btn.pack(side='right')
        
        # Save answer button
        save_btn = tk.Button(
            nav_frame,
            text="Save Answer",
            font=('Arial', 12),
            bg=self.colors['success'],
            fg='white',
            width=12,
            command=self.save_current_answer
        )
        save_btn.pack(side='right', padx=(0, 10))
    
    def save_current_answer(self):
        """Save the current answer."""
        if self.selected_option.get():
            self.user_answers[self.current_question_index] = self.selected_option.get()
            messagebox.showinfo("Saved", "Answer saved successfully!")
        else:
            messagebox.showwarning("Warning", "Please select an answer before saving!")
    
    def next_question(self):
        """Move to the next question."""
        # Save current answer if selected
        if hasattr(self, 'selected_option') and self.selected_option.get():
            self.user_answers[self.current_question_index] = self.selected_option.get()
        
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.show_exam_screen()
    
    def previous_question(self):
        """Move to the previous question."""
        # Save current answer if selected
        if hasattr(self, 'selected_option') and self.selected_option.get():
            self.user_answers[self.current_question_index] = self.selected_option.get()
        
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_exam_screen()
    
    def submit_exam(self):
        """Submit the exam and calculate results with enhanced analytics."""
        # Stop timer
        self.timer_running = False
        
        # Save current answer if selected
        if hasattr(self, 'selected_option') and self.selected_option.get():
            self.user_answers[self.current_question_index] = self.selected_option.get()
        
        # Check if all questions are answered
        unanswered = len(self.questions) - len(self.user_answers)
        if unanswered > 0:
            result = messagebox.askyesno(
                "Incomplete Exam",
                f"You have {unanswered} unanswered questions. Do you want to submit anyway?"
            )
            if not result:
                return
        
        # Calculate detailed scores
        self.score = 0
        points_earned = 0
        
        for i, question in enumerate(self.questions):
            if i in self.user_answers:
                user_answer = self.user_answers[i]
                correct_answer = question['correct_option']
                category = question['category']
                difficulty = question['difficulty']
                points = question['points']
                
                if user_answer == correct_answer:
                    self.score += 1
                    points_earned += points
                    self.category_scores[category]['correct'] += 1
                    self.difficulty_scores[difficulty]['correct'] += 1
        
        # Calculate time taken
        time_taken = self.exam_duration - self.time_remaining if self.exam_start_time else 0
        
        # Save result to database with enhanced data
        self.db.save_exam_result(
            self.current_user['id'],
            self.score,
            len(self.questions),
            points_earned,
            time_taken,
            self.category_scores,
            self.difficulty_scores
        )
        
        # Show results with option to review
        self.show_results_screen()
    
    def show_results_screen(self):
        """Display enhanced exam results."""
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Results frame
        results_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        results_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(
            results_frame,
            text="Exam Results",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg=self.colors['primary']
        )
        title_label.pack(pady=20)
        
        # Student info
        info_frame = tk.Frame(results_frame, bg='white')
        info_frame.pack(pady=10)
        
        tk.Label(
            info_frame,
            text=f"Student: {self.current_user['full_name']}",
            font=('Arial', 14),
            bg='white'
        ).pack()
        
        time_taken = self.exam_duration - self.time_remaining
        tk.Label(
            info_frame,
            text=f"Time Taken: {self.format_time(time_taken)}",
            font=('Arial', 12),
            bg='white',
            fg=self.colors['secondary']
        ).pack()
        
        # Score summary
        percentage = round((self.score / len(self.questions)) * 100, 2)
        points_earned = sum(q['points'] for i, q in enumerate(self.questions) if i in self.user_answers and self.user_answers[i] == q['correct_option'])
        
        # Color code based on performance
        if percentage >= 80:
            score_color = self.colors['success']
        elif percentage >= 60:
            score_color = self.colors['warning']
        else:
            score_color = self.colors['danger']
        
        score_text = f"Score: {self.score}/{len(self.questions)} ({percentage}%)"
        points_text = f"Points: {points_earned}/{self.total_points}"
        
        tk.Label(
            results_frame,
            text=score_text,
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=score_color
        ).pack(pady=10)
        
        tk.Label(
            results_frame,
            text=points_text,
            font=('Arial', 14),
            bg='white',
            fg=score_color
        ).pack(pady=5)
        
        # Performance breakdown
        breakdown_frame = tk.Frame(results_frame, bg='white')
        breakdown_frame.pack(pady=20, padx=40, fill='x')
        
        # Category performance
        tk.Label(
            breakdown_frame,
            text="Performance by Category:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))
        
        for category, scores in self.category_scores.items():
            if scores['total'] > 0:
                cat_percentage = round((scores['correct'] / scores['total']) * 100, 2)
                tk.Label(
                    breakdown_frame,
                    text=f"  {category}: {scores['correct']}/{scores['total']} ({cat_percentage}%)",
                    font=('Arial', 10),
                    bg='white'
                ).pack(anchor='w')
        
        # Difficulty performance
        tk.Label(
            breakdown_frame,
            text="Performance by Difficulty:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))
        
        for difficulty, scores in self.difficulty_scores.items():
            if scores['total'] > 0:
                diff_percentage = round((scores['correct'] / scores['total']) * 100, 2)
                tk.Label(
                    breakdown_frame,
                    text=f"  {difficulty}: {scores['correct']}/{scores['total']} ({diff_percentage}%)",
                    font=('Arial', 10),
                    bg='white'
                ).pack(anchor='w')
        
        # Performance message
        if percentage >= 80:
            message = "🎉 Excellent! Outstanding performance!"
        elif percentage >= 60:
            message = "👍 Good job! Keep up the good work!"
        else:
            message = "📚 Keep studying! You can do better next time!"
        
        tk.Label(
            results_frame,
            text=message,
            font=('Arial', 12),
            bg='white',
            fg=score_color
        ).pack(pady=15)
        
        # Buttons frame
        button_frame = tk.Frame(results_frame, bg='white')
        button_frame.pack(pady=20)
        
        # Review answers button
        if self.config.get('allow_review'):
            review_btn = tk.Button(
                button_frame,
                text="Review Answers",
                font=('Arial', 12),
                bg=self.colors['primary'],
                fg='white',
                width=15,
                command=self.show_review_screen
            )
            review_btn.pack(side='left', padx=10)
        
        # Take another exam button
        retake_btn = tk.Button(
            button_frame,
            text="Take Another Exam",
            font=('Arial', 12),
            bg=self.colors['success'],
            fg='white',
            width=18,
            command=self.show_exam_instructions
        )
        retake_btn.pack(side='left', padx=10)
        
        # Logout button
        logout_btn = tk.Button(
            button_frame,
            text="Logout",
            font=('Arial', 12),
            bg=self.colors['secondary'],
            fg='white',
            width=12,
            command=self.logout
        )
        logout_btn.pack(side='left', padx=10)
    
    def show_review_screen(self):
        """Show detailed review of answers after exam."""
        self.clear_window()
        
        # Main frame with scrollbar
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Answer Review",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Review each question
        for i, question in enumerate(self.questions):
            # Question frame
            q_frame = tk.Frame(scrollable_frame, bg='white', relief='raised', bd=1)
            q_frame.pack(fill='x', padx=10, pady=5)
            
            # Question header
            header_frame = tk.Frame(q_frame, bg='white')
            header_frame.pack(fill='x', padx=10, pady=5)
            
            # Question number and info
            q_info = f"Q{i+1}. [{question['category']} - {question['difficulty']} - {question['points']} pts]"
            tk.Label(header_frame, text=q_info, font=('Arial', 10, 'bold'), 
                    bg='white', fg=self.colors['secondary']).pack(anchor='w')
            
            # Question text
            q_text = question['question']
            tk.Label(q_frame, text=q_text, font=('Arial', 12, 'bold'), 
                    bg='white', wraplength=700, justify='left').pack(anchor='w', padx=10, pady=5)
            
            # Show all options with correct/incorrect marking
            options = ['A', 'B', 'C', 'D']
            option_texts = [question['option_a'], question['option_b'], 
                           question['option_c'], question['option_d']]
            
            user_answer = self.user_answers.get(i, None)
            correct_answer = question['correct_option']
            
            for opt, text in zip(options, option_texts):
                color = 'black'
                prefix = ""
                bg_color = 'white'
                
                if opt == correct_answer:
                    color = self.colors['success']
                    prefix = "✓ "
                    if opt == user_answer:
                        bg_color = '#e6ffed'  # Light green background
                elif opt == user_answer and opt != correct_answer:
                    color = self.colors['danger']
                    prefix = "✗ "
                    bg_color = '#ffebee'  # Light red background
                
                option_frame = tk.Frame(q_frame, bg=bg_color)
                option_frame.pack(fill='x', padx=20, pady=2)
                
                option_label = tk.Label(
                    option_frame, 
                    text=f"{prefix}{opt}. {text}",
                    font=('Arial', 10),
                    bg=bg_color,
                    fg=color,
                    wraplength=650,
                    justify='left'
                )
                option_label.pack(anchor='w', padx=5, pady=3)
            
            # Show explanation if available
            if question.get('explanation'):
                exp_frame = tk.Frame(q_frame, bg='#f8f9fa')
                exp_frame.pack(fill='x', padx=20, pady=5)
                
                tk.Label(exp_frame, text="Explanation:", font=('Arial', 10, 'bold'), 
                        bg='#f8f9fa').pack(anchor='w', padx=5)
                
                tk.Label(exp_frame, text=question['explanation'], font=('Arial', 9), 
                        bg='#f8f9fa', wraplength=650, justify='left').pack(anchor='w', padx=5, pady=2)
            
            # Show if question was answered correctly
            if i in self.user_answers:
                if user_answer == correct_answer:
                    result_text = "✓ Correct"
                    result_color = self.colors['success']
                else:
                    result_text = f"✗ Incorrect (Your answer: {user_answer}, Correct: {correct_answer})"
                    result_color = self.colors['danger']
            else:
                result_text = "⚪ Not answered"
                result_color = self.colors['secondary']
            
            tk.Label(q_frame, text=result_text, font=('Arial', 10, 'bold'), 
                    bg='white', fg=result_color).pack(anchor='w', padx=10, pady=5)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Back button
        back_btn = tk.Button(
            main_frame,
            text="← Back to Results",
            font=('Arial', 12),
            bg=self.colors['secondary'],
            fg='white',
            width=15,
            command=self.show_results_screen
        )
        back_btn.pack(pady=10)
    
    def show_performance_analytics(self):
        """Show detailed performance analytics."""
        analytics = self.db.get_detailed_analytics(self.current_user['id'])
        
        if not analytics:
            messagebox.showinfo("No Data", "No exam history found. Take an exam first!")
            return
        
        self.clear_window()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Performance Analytics",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Analytics frame
        analytics_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        analytics_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Summary statistics
        summary_frame = tk.Frame(analytics_frame, bg='white')
        summary_frame.pack(fill='x', padx=20, pady=15)
        
        tk.Label(summary_frame, text="Overall Performance Summary", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 10))
        
        stats_text = f"""
        Total Exams Taken: {analytics['total_exams']}
        Average Score: {analytics['average_score']:.1f} questions
        Average Percentage: {analytics['average_percentage']:.1f}%
        Best Score: {analytics['best_score']} questions
        """
        
        if analytics['time_analysis']['average_time'] > 0:
            avg_time = int(analytics['time_analysis']['average_time'])
            stats_text += f"Average Time: {self.format_time(avg_time)}\n"
            
            fastest_time = int(analytics['time_analysis']['fastest_time'])
            stats_text += f"Fastest Time: {self.format_time(fastest_time)}"
        
        tk.Label(summary_frame, text=stats_text, font=('Arial', 12), 
                bg='white', justify='left').pack(anchor='w')
        
        # Recent performance
        recent_frame = tk.Frame(analytics_frame, bg='white')
        recent_frame.pack(fill='x', padx=20, pady=15)
        
        tk.Label(recent_frame, text="Recent Exam Results", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 10))
        
        for exam in analytics['recent_performance'][:5]:  # Show last 5 exams
            exam_text = f"Date: {exam['date'][:10]} | Score: {exam['score']}/{exam['total']} ({exam['percentage']}%)"
            if exam.get('time_taken'):
                exam_text += f" | Time: {self.format_time(exam['time_taken'])}"
            
            tk.Label(recent_frame, text=exam_text, font=('Arial', 10), 
                    bg='white').pack(anchor='w', pady=2)
        
        # Back button
        back_btn = tk.Button(
            main_frame,
            text="← Back",
            font=('Arial', 12),
            bg=self.colors['secondary'],
            fg='white',
            width=15,
            command=self.show_exam_instructions
        )
        back_btn.pack(pady=10)
    
    def logout(self):
        """Logout and return to login screen."""
        # Stop timer if running
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Reset all state
        self.current_user = None
        self.questions = []
        self.user_answers = {}
        self.score = 0
        self.current_question_index = 0
        self.category_scores = {}
        self.difficulty_scores = {}
        
        self.show_login_screen()
    
    def run(self):
        """Start the application."""
        # Initialize sample data if database is empty
        try:
            if not self.db.get_questions(limit=1):
                print("Initializing database with sample data...")
                self.db.populate_sample_data()
                print("Sample data added successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
        
        # Start the main loop
        self.root.mainloop()

def main():
    """Main function to run the application."""
    print("Starting Online Examination System...")
    print("Loading configuration...")
    
    # Suppress warnings for cleaner output
    import warnings
    warnings.filterwarnings('ignore', message='.*Glyph.*')
    warnings.filterwarnings('ignore', category=UserWarning)
    
    app = OnlineExamSystem()
    print("Starting application...")
    app.run()

if __name__ == "__main__":
    main()
