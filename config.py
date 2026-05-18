"""
Configuration file for Face Recognition Attendance System
"""

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Faculty credentials
FACULTY_CREDENTIALS = {
    'username': 'Faculty',
    'password': 'Faculty123'
}

# Branch list
BRANCHES = ['CAI', 'CSM', 'CSD', 'CSC', 'AIDS']

# Gender options
GENDERS = ['Male', 'Female', 'Other']

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
QR_CODES_DIR = os.path.join(STATIC_DIR, 'qr_codes')
TRAINING_IMAGES_DIR = os.path.join(DATA_DIR, 'training_images')

# Data files
STUDENTS_CSV = os.path.join(DATA_DIR, 'students.csv')
ATTENDANCE_CSV = os.path.join(DATA_DIR, 'attendance.csv')
FACE_ENCODINGS_FILE = os.path.join(DATA_DIR, 'face_encodings.pkl')

# Face recognition parameters
FACE_RECOGNITION_TOLERANCE = 0.6
IMAGES_PER_STUDENT = 3

# Blink detection parameters
EYE_AR_THRESHOLD = 0.25
EYE_AR_CONSEC_FRAMES = 2

# Flask configuration
SECRET_KEY = 'your-secret-key-change-in-production'
DEBUG = True

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QR_CODES_DIR, exist_ok=True)
os.makedirs(TRAINING_IMAGES_DIR, exist_ok=True)
