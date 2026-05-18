"""
Flask Application - Face Recognition Attendance System
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import config
from data_manager import DataManager
from qr_module import QRCodeManager
from face_recognition_module import FaceRecognitionManager
import cv2
import base64
import numpy as np

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Initialize managers
data_manager = DataManager()
qr_manager = QRCodeManager()
face_manager = FaceRecognitionManager()

# Helper function to check faculty authentication
def is_faculty_authenticated():
    return session.get('authenticated') == True and session.get('role') == 'faculty'

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page - Role selection"""
    return render_template('role_selection.html')

@app.route('/student')
def student_access():
    """Student access - redirect to main page"""
    session['role'] = 'student'
    session['authenticated'] = True
    return redirect(url_for('dashboard'))

@app.route('/faculty-login', methods=['GET', 'POST'])
def faculty_login():
    """Faculty login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == config.FACULTY_CREDENTIALS['username'] and 
            password == config.FACULTY_CREDENTIALS['password']):
            session['authenticated'] = True
            session['role'] = 'faculty'
            return redirect(url_for('dashboard'))
        else:
            return render_template('faculty_login.html', error="Invalid credentials")
    
    return render_template('faculty_login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    
    role = session.get('role')
    stats = data_manager.get_dashboard_stats()
    
    return render_template('dashboard.html', 
                         role=role, 
                         stats=stats,
                         branches=config.BRANCHES)

@app.route('/student-management')
def student_management():
    """Student management page (Faculty only)"""
    if not is_faculty_authenticated():
        return redirect(url_for('index'))
    
    students = data_manager.get_all_students()
    return render_template('student_management.html', 
                         students=students,
                         branches=config.BRANCHES,
                         genders=config.GENDERS)

@app.route('/webcam-attendance')
def webcam_attendance():
    """Webcam attendance page (Faculty only)"""
    if not is_faculty_authenticated():
        return redirect(url_for('index'))
    
    return render_template('webcam_attendance.html')

@app.route('/attendance-report')
def attendance_report():
    """Attendance report page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    
    role = session.get('role')
    attendance_data = data_manager.get_attendance_report()
    
    return render_template('attendance_report.html', 
                         role=role,
                         attendance_data=attendance_data,
                         branches=config.BRANCHES)

# ==================== API ENDPOINTS ====================

@app.route('/api/save-student', methods=['POST'])
def api_save_student():
    """API endpoint to save student data"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        student_data = {
            'roll_number': request.form.get('roll_number'),
            'name': request.form.get('name'),
            'gender': request.form.get('gender'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'branch': request.form.get('branch'),
            'qr_code_path': '',
            'face_trained': 'No'
        }
        
        success, message = data_manager.save_student(student_data)
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/get-students', methods=['GET'])
def api_get_students():
    """API endpoint to get all students"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    students = data_manager.get_all_students()
    return jsonify({'success': True, 'students': students})

@app.route('/api/delete-student', methods=['POST'])
def api_delete_student():
    """API endpoint to delete student"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    roll_number = request.form.get('roll_number')
    success, message = data_manager.delete_student(roll_number)
    return jsonify({'success': success, 'message': message})

@app.route('/api/train-face', methods=['POST'])
def api_train_face():
    """API endpoint to start face training session"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        
        # Get student data
        student = data_manager.get_student_by_roll(roll_number)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        # Store training session info in session
        session['training_roll'] = roll_number
        session['training_name'] = name
        session['training_images'] = []
        
        return jsonify({
            'success': True, 
            'message': 'Training session started. Capture images from webcam.',
            'roll_number': roll_number,
            'name': name
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/capture-training-image', methods=['POST'])
def api_capture_training_image():
    """API endpoint to capture a training image from webcam"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Get frame data from request
        frame_data = request.json.get('frame')
        
        # Decode base64 image
        img_data = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Validate frame
        if frame is None:
            return jsonify({'success': False, 'message': 'Failed to decode image'})
        
        if len(frame.shape) < 2:
            return jsonify({'success': False, 'message': 'Invalid image dimensions'})
        
        # Ensure frame is in correct format (8-bit BGR)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        
        print(f"✓ Frame decoded successfully: shape={frame.shape}, dtype={frame.dtype}")
        
        # NOTE: We skip face detection here due to face_recognition library issues
        # Face detection will be done during training when reading from saved files
        # This is a workaround for the "Unsupported image type" error
        
        # Get training session info
        roll_number = session.get('training_roll')
        name = session.get('training_name')
        
        if not roll_number:
            return jsonify({'success': False, 'message': 'No active training session'})
        
        # Create student directory
        student_dir = os.path.join(config.TRAINING_IMAGES_DIR, roll_number)
        os.makedirs(student_dir, exist_ok=True)
        
        # Get current count
        training_images = session.get('training_images', [])
        count = len(training_images)
        
        # Save image with verification
        image_path = os.path.join(student_dir, f"{roll_number}_{count + 1}.jpg")
        
        # Write the image
        write_success = cv2.imwrite(image_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        if not write_success:
            print(f"✗ ERROR: Failed to write image to {image_path}")
            return jsonify({'success': False, 'message': 'Failed to save image to disk'})
        
        # Verify the image was saved and can be read
        if not os.path.exists(image_path):
            print(f"✗ ERROR: Image file does not exist after write: {image_path}")
            return jsonify({'success': False, 'message': 'Image file was not created'})
        
        # Try to read it back to verify it's valid
        test_read = cv2.imread(image_path)
        if test_read is None:
            print(f"✗ ERROR: Cannot read back saved image: {image_path}")
            os.remove(image_path)  # Remove the corrupt file
            return jsonify({'success': False, 'message': 'Saved image is corrupted'})
        
        print(f"✓ SUCCESS: Image saved and verified: {image_path} (size: {os.path.getsize(image_path)} bytes)")
        
        # Add to session
        training_images.append(image_path)
        session['training_images'] = training_images
        
        return jsonify({
            'success': True,
            'message': f'Image {count + 1} captured successfully',
            'count': count + 1,
            'total': config.IMAGES_PER_STUDENT
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/complete-training', methods=['POST'])
def api_complete_training():
    """API endpoint to complete face training"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        roll_number = session.get('training_roll')
        name = session.get('training_name')
        image_paths = session.get('training_images', [])
        
        if not roll_number or not image_paths:
            return jsonify({'success': False, 'message': 'No training data found'})
        
        # Train face model
        success, message = face_manager.train_face_model(roll_number, name, image_paths)
        
        if success:
            # Update student record
            data_manager.update_student_face_trained(roll_number, True)
        
        # Clear training session
        session.pop('training_roll', None)
        session.pop('training_name', None)
        session.pop('training_images', None)
        
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/generate-qr', methods=['POST'])
def api_generate_qr():
    """API endpoint to generate QR code"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        roll_number = request.form.get('roll_number')
        
        # Get student data
        student = data_manager.get_student_by_roll(roll_number)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        # Generate QR code
        success, qr_path, message = qr_manager.generate_qr_code(student)
        
        if success:
            # Update student record
            data_manager.update_student_qr(roll_number, qr_path)
        
        return jsonify({'success': success, 'message': message, 'qr_path': qr_path})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/process-frame', methods=['POST'])
def api_process_frame():
    """API endpoint to process webcam frame for attendance"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Get frame data from request
        frame_data = request.json.get('frame')
        mode = request.json.get('mode', 'qr')  # qr, blink, or face
        
        # Decode base64 image
        img_data = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Validate frame
        if frame is None:
            return jsonify({'success': False, 'message': 'Failed to decode image'})
        
        if len(frame.shape) < 2:
            return jsonify({'success': False, 'message': 'Invalid image dimensions'})
        
        # Ensure frame is in correct format (8-bit BGR)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        
        if mode == 'qr':
            # Scan QR code
            success, student_data = qr_manager.scan_qr_code(frame)
            if success:
                return jsonify({
                    'success': True,
                    'mode': 'qr',
                    'student': student_data
                })
            else:
                return jsonify({'success': False, 'message': 'No QR code detected'})
        
        elif mode == 'blink':
            # Detect blink and return coordinates for visualization
            blink_detected, ear_left, ear_right, detection_data = face_manager.detect_blink_with_coords(frame)
            return jsonify({
                'success': True,
                'mode': 'blink',
                'blink_detected': blink_detected,
                'ear_left': ear_left,
                'ear_right': ear_right,
                'detection_data': detection_data
            })
        
        elif mode == 'face':
            # Recognize face
            print(f"[API] Calling recognize_face...")
            success, student_data, face_location = face_manager.recognize_face(frame)
            print(f"[API] recognize_face returned: success={success}, student_data={student_data}, face_location={face_location}")
            
            if success:
                print(f"[API] Returning success response with student: {student_data}")
                return jsonify({
                    'success': True,
                    'mode': 'face',
                    'student': student_data,
                    'face_location': face_location
                })
            else:
                print(f"[API] Returning failure response")
                return jsonify({'success': False, 'message': 'No face recognized'})
        
        return jsonify({'success': False, 'message': 'Invalid mode'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/mark-attendance', methods=['POST'])
def api_mark_attendance():
    """API endpoint to mark attendance"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        branch = request.form.get('branch')
        
        success, message = data_manager.mark_attendance(roll_number, name, branch)
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/delete-attendance', methods=['POST'])
def api_delete_attendance():
    """API endpoint to delete attendance record"""
    if not is_faculty_authenticated():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        timestamp = data.get('timestamp')
        
        if not timestamp:
            return jsonify({'success': False, 'message': 'Timestamp is required'})
        
        success, message = data_manager.delete_attendance(timestamp)
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/get-dashboard-stats', methods=['GET'])
def api_get_dashboard_stats():
    """API endpoint to get dashboard statistics"""
    if not session.get('authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    date = request.args.get('date')
    stats = data_manager.get_dashboard_stats(date)
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/get-attendance-report', methods=['GET'])
def api_get_attendance_report():
    """API endpoint to get attendance report"""
    if not session.get('authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    date = request.args.get('date')
    branch = request.args.get('branch')
    
    attendance_data = data_manager.get_attendance_report(date, branch)
    return jsonify({'success': True, 'data': attendance_data})

@app.route('/api/export-attendance', methods=['GET'])
def api_export_attendance():
    """API endpoint to export attendance data"""
    if not session.get('authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        success, result = data_manager.export_attendance_to_csv()
        if success:
            return send_file(result, as_attachment=True, download_name='attendance_export.csv')
        else:
            return jsonify({'success': False, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
