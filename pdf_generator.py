"""
PDF Report Generator for Online Examination System
Generates detailed PDF reports of exam results.
"""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available. PDF export functionality will be disabled.")
    print("Install with: pip install reportlab")

from datetime import datetime
from typing import Dict, List
import os

class PDFReportGenerator:
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE
        if not self.available:
            return
        
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb'),
            alignment=1  # Center alignment
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=colors.HexColor('#1e293b')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10
        )
    
    def is_available(self):
        """Check if PDF generation is available."""
        return self.available
    
    def generate_exam_report(self, user_data: Dict, exam_data: Dict, 
                           questions: List[Dict], user_answers: Dict,
                           category_scores: Dict, difficulty_scores: Dict,
                           filename: str = None) -> str:
        """Generate a comprehensive PDF report of exam results."""
        if not self.available:
            raise Exception("ReportLab is not available. Cannot generate PDF.")
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exam_report_{user_data['username']}_{timestamp}.pdf"
        
        # Ensure the filename has .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Create the PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("Online Examination System<br/>Exam Results Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Student Information
        story.append(Paragraph("Student Information", self.heading_style))
        student_info = f"""
        <b>Name:</b> {user_data['full_name']}<br/>
        <b>Username:</b> {user_data['username']}<br/>
        <b>Exam Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Total Questions:</b> {exam_data['total_questions']}<br/>
        <b>Time Taken:</b> {self._format_time(exam_data.get('time_taken', 0))}
        """
        story.append(Paragraph(student_info, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Exam Summary
        story.append(Paragraph("Exam Summary", self.heading_style))
        
        percentage = round((exam_data['score'] / exam_data['total_questions']) * 100, 2)
        points_earned = exam_data.get('points_earned', 0)
        total_points = exam_data.get('total_points', exam_data['total_questions'])
        
        # Determine grade/performance level
        if percentage >= 90:
            grade = "A+"
            performance = "Excellent"
        elif percentage >= 80:
            grade = "A"
            performance = "Very Good"
        elif percentage >= 70:
            grade = "B"
            performance = "Good"
        elif percentage >= 60:
            grade = "C"
            performance = "Satisfactory"
        else:
            grade = "D"
            performance = "Needs Improvement"
        
        summary_info = f"""
        <b>Score:</b> {exam_data['score']} out of {exam_data['total_questions']} correct<br/>
        <b>Percentage:</b> {percentage}%<br/>
        <b>Points Earned:</b> {points_earned} out of {total_points}<br/>
        <b>Grade:</b> {grade}<br/>
        <b>Performance Level:</b> {performance}
        """
        story.append(Paragraph(summary_info, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Performance by Category
        if category_scores:
            story.append(Paragraph("Performance by Category", self.heading_style))
            
            cat_data = [['Category', 'Correct', 'Total', 'Percentage']]
            for category, scores in category_scores.items():
                if scores['total'] > 0:
                    cat_percentage = round((scores['correct'] / scores['total']) * 100, 2)
                    cat_data.append([
                        category,
                        str(scores['correct']),
                        str(scores['total']),
                        f"{cat_percentage}%"
                    ])
            
            if len(cat_data) > 1:
                cat_table = Table(cat_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(cat_table)
                story.append(Spacer(1, 20))
        
        # Performance by Difficulty
        if difficulty_scores:
            story.append(Paragraph("Performance by Difficulty Level", self.heading_style))
            
            diff_data = [['Difficulty', 'Correct', 'Total', 'Percentage']]
            for difficulty, scores in difficulty_scores.items():
                if scores['total'] > 0:
                    diff_percentage = round((scores['correct'] / scores['total']) * 100, 2)
                    diff_data.append([
                        difficulty,
                        str(scores['correct']),
                        str(scores['total']),
                        f"{diff_percentage}%"
                    ])
            
            if len(diff_data) > 1:
                diff_table = Table(diff_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
                diff_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9f0')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(diff_table)
                story.append(Spacer(1, 20))
        
        # Detailed Question Review
        story.append(Paragraph("Detailed Answer Review", self.heading_style))
        
        for i, question in enumerate(questions):
            # Question header
            q_header = f"Question {i+1} [{question['category']} - {question['difficulty']} - {question['points']} points]"
            story.append(Paragraph(q_header, ParagraphStyle(
                'QuestionHeader',
                parent=self.normal_style,
                fontSize=12,
                textColor=colors.HexColor('#64748b'),
                fontName='Helvetica-Bold'
            )))
            
            # Question text
            q_text = f"<b>{question['question']}</b>"
            story.append(Paragraph(q_text, self.normal_style))
            
            # Options with marking
            options = ['A', 'B', 'C', 'D']
            option_texts = [
                question['option_a'], question['option_b'],
                question['option_c'], question['option_d']
            ]
            
            user_answer = user_answers.get(i, None)
            correct_answer = question['correct_option']
            
            for opt, text in zip(options, option_texts):
                if opt == correct_answer:
                    if opt == user_answer:
                        # Correct answer, user selected
                        option_text = f"<b>{opt}. {text}</b> ✓ <i>(Your answer - Correct!)</i>"
                        color = colors.HexColor('#16a34a')
                    else:
                        # Correct answer, user didn't select
                        option_text = f"<b>{opt}. {text}</b> ✓ <i>(Correct answer)</i>"
                        color = colors.HexColor('#16a34a')
                elif opt == user_answer:
                    # User's incorrect answer
                    option_text = f"{opt}. {text} ✗ <i>(Your answer - Incorrect)</i>"
                    color = colors.HexColor('#dc2626')
                else:
                    # Regular option
                    option_text = f"{opt}. {text}"
                    color = colors.black
                
                story.append(Paragraph(option_text, ParagraphStyle(
                    'OptionStyle',
                    parent=self.normal_style,
                    fontSize=10,
                    leftIndent=20,
                    textColor=color
                )))
            
            # Explanation if available
            if question.get('explanation'):
                exp_text = f"<i><b>Explanation:</b> {question['explanation']}</i>"
                story.append(Paragraph(exp_text, ParagraphStyle(
                    'ExplanationStyle',
                    parent=self.normal_style,
                    fontSize=9,
                    leftIndent=20,
                    textColor=colors.HexColor('#64748b'),
                    backColor=colors.HexColor('#f8f9fa')
                )))
            
            story.append(Spacer(1, 15))
        
        # Recommendations
        story.append(Paragraph("Recommendations for Improvement", self.heading_style))
        
        recommendations = []
        
        # Category-based recommendations
        if category_scores:
            weak_categories = [cat for cat, scores in category_scores.items() 
                             if scores['total'] > 0 and (scores['correct'] / scores['total']) < 0.7]
            if weak_categories:
                recommendations.append(f"Focus on improving in: {', '.join(weak_categories)}")
        
        # Difficulty-based recommendations
        if difficulty_scores:
            for difficulty, scores in difficulty_scores.items():
                if scores['total'] > 0:
                    perf = scores['correct'] / scores['total']
                    if perf < 0.6:
                        recommendations.append(f"Strengthen {difficulty.lower()} level concepts")
        
        # Time-based recommendations
        if exam_data.get('time_taken', 0) > 0:
            time_percentage = (exam_data['time_taken'] / 600) * 100  # Assuming 10 min exam
            if time_percentage < 50:
                recommendations.append("Consider taking more time to review answers")
            elif time_percentage > 90:
                recommendations.append("Work on time management and question comprehension speed")
        
        # General recommendations based on score
        if percentage < 60:
            recommendations.append("Review fundamental concepts and practice more questions")
        elif percentage < 80:
            recommendations.append("Focus on areas of weakness and practice advanced problems")
        else:
            recommendations.append("Excellent performance! Continue practicing to maintain proficiency")
        
        if not recommendations:
            recommendations = ["Keep up the good work and continue practicing!"]
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.normal_style))
        
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"<i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i><br/><i>Online Examination System - Enhanced Version</i>"
        story.append(Paragraph(footer_text, ParagraphStyle(
            'FooterStyle',
            parent=self.normal_style,
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=1  # Center alignment
        )))
        
        # Build the PDF
        doc.build(story)
        
        return filename
    
    def _format_time(self, seconds: int) -> str:
        """Format time in MM:SS format."""
        if seconds <= 0:
            return "Not recorded"
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def generate_simple_report(self, user_data: Dict, exam_data: Dict, filename: str = None) -> str:
        """Generate a simple PDF report with basic information."""
        if not self.available:
            raise Exception("ReportLab is not available. Cannot generate PDF.")
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exam_summary_{user_data['username']}_{timestamp}.pdf"
        
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 80, "Exam Results Summary")
        
        # Student info
        c.setFont("Helvetica", 14)
        y_position = height - 140
        
        info_items = [
            f"Student Name: {user_data['full_name']}",
            f"Username: {user_data['username']}",
            f"Date: {datetime.now().strftime('%B %d, %Y')}",
            f"Score: {exam_data['score']} out of {exam_data['total_questions']}",
            f"Percentage: {round((exam_data['score'] / exam_data['total_questions']) * 100, 2)}%"
        ]
        
        for item in info_items:
            c.drawString(50, y_position, item)
            y_position -= 25
        
        # Performance message
        percentage = round((exam_data['score'] / exam_data['total_questions']) * 100, 2)
        if percentage >= 80:
            message = "Excellent performance! Keep up the great work!"
        elif percentage >= 60:
            message = "Good job! Continue practicing to improve further."
        else:
            message = "Keep studying and practicing. You can do better!"
        
        c.setFont("Helvetica-Oblique", 12)
        c.drawString(50, y_position - 30, message)
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, f"Generated by Online Examination System on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        c.save()
        return filename
