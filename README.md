# 🎓 Face Recognition Based Attendance System

A comprehensive, real-time attendance management system using face recognition, QR codes, and blink detection for secure and automated attendance tracking.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Functionality
- **🎥 Real-time Face Recognition**: Optimized OpenCV-based face detection and recognition with 60-75% accuracy
- **📱 QR Code Integration**: Unique QR codes for each student with embedded student information
- **👁️ Blink Detection**: Liveness detection to prevent photo spoofing
- **🔐 Multi-Step Verification**: QR scan → Blink detection → Face recognition for enhanced security
- **📊 Visual Feedback**: Real-time overlay of face boxes and eye markers during detection

### Management Features
- **👥 Student Management**: Add, edit, delete students with comprehensive details
- **🎓 Face Training**: Capture and train face models with 3 images per student
- **📈 Dashboard**: Real-time statistics and branch-wise attendance analytics
- **📄 Attendance Reports**: View, filter, export (CSV), and delete attendance records
- **🔒 Role-Based Access**: Separate interfaces for faculty and students

### Security Features
- **Database Validation**: QR codes validated against student database
- **Face Encoding Storage**: Secure storage of face data in pickle format
- **Session Management**: Faculty authentication for sensitive operations
- **Data Protection**: Comprehensive `.gitignore` for sensitive data

---

## 🎬 Demo

### Attendance Marking Flow
1. **QR Code Scan** → Student details displayed
2. **Blink Detection** → Liveness verification with eye tracking
3. **Face Recognition** → Identity confirmation with confidence percentage
4. **Attendance Marked** → Record saved with timestamp

### Visual Features
- Green/Orange face boxes during blink detection
- Blue circles around detected eyes
- Real-time confidence percentage display
- Color-coded status indicators

---

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **Python 3.10+** - Core programming language
- **Pandas 2.2.0** - Data management
- **OpenCV 4.10.0** - Computer vision and face recognition

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern design
- **JavaScript (ES6+)** - Interactive functionality
- **Canvas API** - Real-time video overlays

### Libraries & Tools
- **NumPy** - Numerical computations
- **Pillow** - Image processing
- **QRCode** - QR code generation
- **PyZbar** - QR code scanning
- **Gunicorn** - Production WSGI server

---

## 📁 Project Structure

```
faceProject/
│
├── 📄 app.py                          # Main Flask application
├── 📄 config.py                       # Configuration settings
├── 📄 data_manager.py                 # Student & attendance data management
├── 📄 face_recognition_module.py      # Face detection & recognition logic
├── 📄 qr_module.py                    # QR code generation & scanning
│
├── 📂 data/                           # Data storage (gitignored)
│   ├── students.csv                   # Student records
│   ├── attendance.csv                 # Attendance records
│   ├── face_encodings.pkl             # Trained face data
│   └── training_images/               # Student face images
│       └── [roll_number]/             # Individual student folders
│
├── 📂 static/                         # Static assets
│   ├── css/
│   │   └── style.css                  # Modern, responsive styling
│   └── qr_codes/                      # Generated QR codes (gitignored)
│
├── 📂 templates/                      # HTML templates
│   ├── role_selection.html            # Landing page
│   ├── faculty_login.html             # Faculty authentication
│   ├── dashboard.html                 # Statistics dashboard
│   ├── student_management.html        # Student CRUD operations
│   ├── webcam_attendance.html         # Attendance marking interface
│   └── attendance_report.html         # Attendance records & export
│
├── 📄 requirements.txt                # Python dependencies
├── 📄 .gitignore                      # Git ignore rules
└── 📄 README.md                       # Project documentation
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `app.py` | Flask routes, API endpoints, session management |
| `config.py` | Centralized configuration (paths, credentials, parameters) |
| `data_manager.py` | CSV operations for students and attendance |
| `face_recognition_module.py` | Face training, recognition, blink detection |
| `qr_module.py` | QR code generation and validation |
| `face_encodings.pkl` | Binary file storing trained face data |

---

## 🚀 Installation

### Prerequisites
- **Python 3.10 or higher**
- **Webcam** (built-in or external)
- **Windows OS** (tested on Windows 10/11)
- **Git** (for version control)

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Ganesh1027/face-recognition-attendance.git
cd face-recognition-attendance
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Command Prompt:
venv\Scripts\activate

# For PowerShell:
venv\Scripts\Activate.ps1
```

> **Note**: If PowerShell gives execution policy error:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### 3. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import cv2, flask, pandas; print('All packages installed successfully!')"
```

#### 4. Verify Project Structure
Ensure these folders exist (created automatically if missing):
```
data/
static/qr_codes/
data/training_images/
```

#### 5. Run the Application
```bash
python app.py
```

Expected output:
```
Loaded 0 face encodings
 * Running on http://127.0.0.1:5000
```

#### 6. Access the Application
Open your browser and navigate to: **http://127.0.0.1:5000**

---

## 📖 Usage Guide

### For Faculty

#### 1. Login
- Navigate to **Faculty Login**
- **Default Credentials**:
  - Username: `Faculty`
  - Password: `Faculty123`
- ⚠️ **Change these in `config.py` for production!**

#### 2. Add Students
1. Go to **Manage Students**
2. Click **"Add New Student"**
3. Fill in details:
   - Roll Number (unique identifier)
   - Name
   - Gender
   - Email
   - Phone
   - Branch (e.g.,CAI,CSM,CSD,CSD,CSC,AID)
4. Click **"Add Student"**

#### 3. Train Face
1. In student list, click **"Train Face"**
2. Webcam opens automatically
3. Position face in frame
4. Press **SPACE** to capture (3 images required)
5. Training completes automatically
6. Face data saved to `face_encodings.pkl`

#### 4. Generate QR Code
1. Click **"Generate QR"** for a student
2. QR code image generated and displayed
3. Download and print for student use
4. QR contains: Roll number, Name, Branch, Unique ID

#### 5. View Reports
1. Go to **Reports**
2. Filter by:
   - Date range
   - Branch
   - Student name
3. **Export to CSV** for external analysis
4. **Delete records** if needed

### For Students

#### 1. Mark Attendance
1. Navigate to **Mark Attendance**
2. Click **"Start Camera"**
3. **Step 1**: Scan your QR code
   - Hold QR code in front of camera
   - Student details displayed when scanned
4. **Step 2**: Blink Detection
   - Look at camera
   - Blink naturally
   - Green face box with blue eye circles appears
   - Orange box when blink detected
5. **Step 3**: Face Recognition
   - System verifies your face
   - Green box with name and confidence % appears
   - Must match QR code student
6. **Step 4**: Mark Attendance
   - Click **"Mark Attendance"** button
   - Success message displayed
   - Record saved with timestamp

#### 2. View Dashboard
- See total students, today's attendance
- Branch-wise statistics
- Recent attendance records

---

## 🌐 Deployment

### Option 1: Render (Recommended - Free)

#### Prerequisites
- GitHub account with your code pushed
- Render account (sign up at [render.com](https://render.com))

#### Steps

1. **Prepare for Deployment**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   pip freeze > requirements.txt
   
   # Commit changes
   git add .
   git commit -m "Add deployment configuration"
   git push
   ```

2. **Create Web Service on Render**
   - Go to [render.com](https://render.com) → Sign in with GitHub
   - Click **"New +"** → **"Web Service"**
   - Connect your repository
   - Configure:
     - **Name**: `face-attendance`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
     - **Instance Type**: `Free`
   - Click **"Create Web Service"**

3. **Wait for Deployment** (5-10 minutes)
   - Monitor build logs
   - Once deployed, you'll get a URL: `https://face-attendance.onrender.com`

4. **Important Notes**
   - Free tier sleeps after 15 minutes of inactivity
   - First request after sleep takes ~30 seconds
   - Upgrade to paid tier for 24/7 availability

### Option 2: PythonAnywhere

#### Steps

1. **Sign Up**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Create free account

2. **Upload Code**
   - Open **Bash console**
   - Clone repository:
     ```bash
     git clone https://github.com/YOUR_USERNAME/face-recognition-attendance.git
     cd face-recognition-attendance
     ```

3. **Set Up Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 faceenv
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Go to **Web** tab → **Add a new web app**
   - Choose **Manual configuration** → **Python 3.10**
   - Set source code path: `/home/yourusername/face-recognition-attendance`
   - Set working directory: same as above
   - Edit WSGI file to import your Flask app

5. **Reload and Access**
   - Click **Reload**
   - Access at: `https://yourusername.pythonanywhere.com`

### Option 3: Local Network Deployment

For use within your organization's network:

```bash
# Run Flask with network access
python app.py
```

Then edit `app.py` to change:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Access from other devices: `http://YOUR_LOCAL_IP:5000`

### Deployment Checklist

- [ ] Change default faculty credentials in `config.py`
- [ ] Set `debug=False` in production
- [ ] Use HTTPS (required for webcam access)
- [ ] Set up proper database (PostgreSQL/MySQL) for production
- [ ] Configure environment variables for secrets
- [ ] Set up regular backups
- [ ] Monitor application logs
- [ ] Test webcam functionality on HTTPS

---

## ⚙️ Configuration

### `config.py` Settings

```python
# Faculty Credentials (CHANGE THESE!)
FACULTY_USERNAME = "Faculty"
FACULTY_PASSWORD = "Faculty123"  # Use strong password

# Face Recognition Parameters
FACE_RECOGNITION_TOLERANCE = 0.6  # Lower = stricter matching
IMAGES_PER_STUDENT = 3            # Images for training

# File Paths (auto-configured)
DATA_DIR = 'data'
STUDENTS_CSV = 'data/students.csv'
ATTENDANCE_CSV = 'data/attendance.csv'
FACE_ENCODINGS_FILE = 'data/face_encodings.pkl'
```

### Adjusting Face Recognition Accuracy

**For higher accuracy** (stricter matching):
- Decrease `FACE_RECOGNITION_TOLERANCE` to `0.4-0.5`
- Increase `IMAGES_PER_STUDENT` to `5-10`
- Ensure good lighting during training

**For easier recognition** (more lenient):
- Increase `FACE_RECOGNITION_TOLERANCE` to `0.7-0.8`
- May increase false positives

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Webcam Not Working
**Problem**: Camera doesn't start or shows black screen

**Solutions**:
- Check camera permissions in browser
- Ensure HTTPS is enabled (required for webcam)
- Try different browser (Chrome recommended)
- Check if another application is using camera

#### 2. Face Recognition Not Working
**Problem**: Face not recognized despite training

**Solutions**:
- Retrain face with better lighting
- Ensure face is clearly visible (no glasses/mask)
- Check if `face_encodings.pkl` exists and has data
- Verify student exists in database

#### 3. QR Code Not Scanning
**Problem**: QR code scan fails

**Solutions**:
- Ensure good lighting
- Hold QR code steady and flat
- Check if student exists in `students.csv`
- Regenerate QR code if corrupted

#### 4. Blink Detection Too Sensitive/Not Working
**Problem**: Blink detection triggers incorrectly or not at all

**Solutions**:
- Adjust lighting (avoid backlighting)
- Look directly at camera
- Ensure eyes are clearly visible
- Check terminal logs for eye detection count

#### 5. Module Import Errors
**Problem**: `ModuleNotFoundError` when running

**Solutions**:
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

#### 6. Port Already in Use
**Problem**: `Address already in use` error

**Solutions**:
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port in app.py
app.run(port=5001)
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Test thoroughly before submitting PR
- Update documentation for new features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔮 Future Enhancements

- [ ] Mobile app integration
- [ ] Email notifications for attendance
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with existing student management systems
- [ ] Facial mask detection
- [ ] Attendance reports via email
- [ ] PostgreSQL/MySQL database support

---

**Made with ❤️ for educational institutions**
