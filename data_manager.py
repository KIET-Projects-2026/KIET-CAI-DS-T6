"""
Data Management Module for Student and Attendance Records
"""

import csv
import os
import pandas as pd
from datetime import datetime
import config

class DataManager:
    def __init__(self):
        self.students_csv = config.STUDENTS_CSV
        self.attendance_csv = config.ATTENDANCE_CSV
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        # Students CSV
        if not os.path.exists(self.students_csv):
            with open(self.students_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['roll_number', 'name', 'gender', 'email', 'phone', 'branch', 'qr_code_path', 'face_trained'])
        
        # Attendance CSV
        if not os.path.exists(self.attendance_csv):
            with open(self.attendance_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['roll_number', 'name', 'branch', 'date', 'time', 'timestamp'])
    
    def save_student(self, student_data):
        """
        Save student data to CSV
        Returns: (success: bool, message: str)
        """
        try:
            # Check if student already exists
            if self.get_student_by_roll(student_data['roll_number']):
                return False, "Student with this roll number already exists"
            
            with open(self.students_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    student_data['roll_number'],
                    student_data['name'],
                    student_data['gender'],
                    student_data['email'],
                    student_data['phone'],
                    student_data['branch'],
                    student_data.get('qr_code_path', ''),
                    student_data.get('face_trained', 'No')
                ])
            return True, "Student saved successfully"
        except Exception as e:
            return False, f"Error saving student: {str(e)}"
    
    def get_all_students(self):
        """Get all students from CSV"""
        try:
            if not os.path.exists(self.students_csv):
                return []
            
            df = pd.read_csv(self.students_csv)
            # Convert NaN values to empty strings for qr_code_path
            df['qr_code_path'] = df['qr_code_path'].fillna('').astype(str)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error reading students: {e}")
            return []
    
    def get_student_by_roll(self, roll_number):
        """Get student by roll number"""
        try:
            if not os.path.exists(self.students_csv):
                return None
            
            df = pd.read_csv(self.students_csv)
            student = df[df['roll_number'] == roll_number]
            if not student.empty:
                return student.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting student: {e}")
            return None
    
    def update_student_qr(self, roll_number, qr_path):
        """Update student's QR code path"""
        try:
            df = pd.read_csv(self.students_csv)
            df.loc[df['roll_number'] == roll_number, 'qr_code_path'] = qr_path
            df.to_csv(self.students_csv, index=False)
            return True
        except Exception as e:
            print(f"Error updating QR: {e}")
            return False
    
    def update_student_face_trained(self, roll_number, trained=True):
        """Update student's face training status"""
        try:
            df = pd.read_csv(self.students_csv)
            df.loc[df['roll_number'] == roll_number, 'face_trained'] = 'Yes' if trained else 'No'
            df.to_csv(self.students_csv, index=False)
            return True
        except Exception as e:
            print(f"Error updating face training status: {e}")
            return False
    
    def delete_student(self, roll_number):
        """Delete student from CSV, face encodings, and training images"""
        try:
            # Import here to avoid circular dependency
            from face_recognition_module import FaceRecognitionManager
            import shutil
            
            # Delete from students CSV
            df = pd.read_csv(self.students_csv)
            df = df[df['roll_number'] != roll_number]
            df.to_csv(self.students_csv, index=False)
            
            # Delete face encodings
            face_manager = FaceRecognitionManager()
            if roll_number in face_manager.known_face_rolls:
                # Find all indices for this student
                indices = [i for i, r in enumerate(face_manager.known_face_rolls) if r == roll_number]
                # Remove in reverse order to maintain indices
                for index in sorted(indices, reverse=True):
                    del face_manager.known_face_encodings[index]
                    del face_manager.known_face_names[index]
                    del face_manager.known_face_rolls[index]
                # Save updated encodings
                face_manager.save_encodings()
                print(f"Removed face encodings for {roll_number}")
            
            # Delete training images folder
            training_dir = os.path.join(config.TRAINING_IMAGES_DIR, roll_number)
            if os.path.exists(training_dir):
                shutil.rmtree(training_dir)
                print(f"Deleted training images for {roll_number}")
            
            # Delete QR code if exists
            qr_dir = config.QR_CODES_DIR
            if os.path.exists(qr_dir):
                for file in os.listdir(qr_dir):
                    if file.startswith(f"qr_{roll_number}_"):
                        qr_path = os.path.join(qr_dir, file)
                        os.remove(qr_path)
                        print(f"Deleted QR code for {roll_number}")
            
            return True, "Student and all associated data deleted successfully"
        except Exception as e:
            print(f"Error deleting student: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error deleting student: {str(e)}"
    
    def mark_attendance(self, roll_number, name, branch):
        """
        Mark attendance for a student
        Returns: (success: bool, message: str)
        """
        try:
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if already marked today
            if self.is_attendance_marked_today(roll_number):
                return False, "Attendance already marked for today"
            
            with open(self.attendance_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([roll_number, name, branch, date_str, time_str, timestamp])
            
            return True, "Attendance marked successfully"
        except Exception as e:
            return False, f"Error marking attendance: {str(e)}"
    
    def is_attendance_marked_today(self, roll_number):
        """Check if attendance is already marked for today"""
        try:
            if not os.path.exists(self.attendance_csv):
                return False
            
            df = pd.read_csv(self.attendance_csv)
            today = datetime.now().strftime('%Y-%m-%d')
            
            attendance_today = df[(df['roll_number'] == roll_number) & (df['date'] == today)]
            return not attendance_today.empty
        except Exception as e:
            print(f"Error checking attendance: {e}")
            return False
    
    def get_attendance_report(self, date=None, branch=None):
        """Get attendance report with optional filters"""
        try:
            if not os.path.exists(self.attendance_csv):
                return []
            
            df = pd.read_csv(self.attendance_csv)
            
            # Apply filters
            if date:
                df = df[df['date'] == date]
            if branch:
                df = df[df['branch'] == branch]
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error getting attendance report: {e}")
            return []
    
    def get_dashboard_stats(self, date=None):
        """Get dashboard statistics"""
        try:
            if not os.path.exists(self.attendance_csv):
                return {
                    'total_present': 0,
                    'branch_wise': {branch: 0 for branch in config.BRANCHES}
                }
            
            df = pd.read_csv(self.attendance_csv)
            
            # Filter by date (default to today)
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            df_today = df[df['date'] == date]
            
            # Calculate statistics
            total_present = len(df_today)
            branch_wise = df_today['branch'].value_counts().to_dict()
            
            # Ensure all branches are represented
            for branch in config.BRANCHES:
                if branch not in branch_wise:
                    branch_wise[branch] = 0
            
            return {
                'total_present': total_present,
                'branch_wise': branch_wise
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_present': 0,
                'branch_wise': {branch: 0 for branch in config.BRANCHES}
            }
    
    def delete_attendance(self, timestamp):
        """Delete attendance record by timestamp"""
        try:
            if not os.path.exists(self.attendance_csv):
                return False, "No attendance data available"
            
            df = pd.read_csv(self.attendance_csv)
            initial_count = len(df)
            
            # Remove the record with matching timestamp
            df = df[df['timestamp'] != timestamp]
            
            if len(df) == initial_count:
                return False, "Attendance record not found"
            
            df.to_csv(self.attendance_csv, index=False)
            return True, "Attendance record deleted successfully"
        except Exception as e:
            return False, f"Error deleting attendance: {str(e)}"
    
    def export_attendance_to_csv(self, filename='attendance_export.csv'):
        """Export attendance data to CSV file"""
        try:
            if not os.path.exists(self.attendance_csv):
                return False, "No attendance data available"
            
            df = pd.read_csv(self.attendance_csv)
            export_path = os.path.join(config.DATA_DIR, filename)
            df.to_csv(export_path, index=False)
            return True, export_path
        except Exception as e:
            return False, f"Error exporting data: {str(e)}"
