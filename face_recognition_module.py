"""
Face Recognition and Blink Detection Module
"""

import cv2
# import face_recognition  # Removed to avoid dlib dependency
import numpy as np
import pickle
import os
from scipy.spatial import distance as dist
import config

class FaceRecognitionManager:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_rolls = []
        self.encodings_file = config.FACE_ENCODINGS_FILE
        self.training_dir = config.TRAINING_IMAGES_DIR
        self.load_encodings()
        
        # Facial landmarks for blink detection
        self.LEFT_EYE_INDICES = list(range(36, 42))
        self.RIGHT_EYE_INDICES = list(range(42, 48))
    
    def load_encodings(self):
        """Load face encodings from pickle file"""
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                    self.known_face_rolls = data['rolls']
                print(f"Loaded {len(self.known_face_encodings)} face encodings")
            except Exception as e:
                print(f"Error loading encodings: {e}")
    
    def save_encodings(self):
        """Save face encodings to pickle file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names,
                'rolls': self.known_face_rolls
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            print("Face encodings saved successfully")
            return True
        except Exception as e:
            print(f"Error saving encodings: {e}")
            return False
    
    def capture_training_images(self, roll_number, name):
        """
        Capture training images for a student
        Returns: (success: bool, message: str, image_paths: list)
        """
        try:
            # Create student directory
            student_dir = os.path.join(self.training_dir, roll_number)
            os.makedirs(student_dir, exist_ok=True)
            
            # Initialize webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Could not open webcam", []
            
            captured_images = []
            image_paths = []
            count = 0
            
            print(f"Capturing {config.IMAGES_PER_STUDENT} images for {name}...")
            print("Press SPACE to capture image, ESC to cancel")
            
            while count < config.IMAGES_PER_STUDENT:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Display frame with instructions
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Captured: {count}/{config.IMAGES_PER_STUDENT}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(display_frame, "Press SPACE to capture", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Capture Training Images', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                # Capture image on SPACE
                if key == ord(' '):
                    # Validate frame
                    if frame is None or len(frame.shape) < 2:
                        print("Invalid frame captured")
                        continue
                    
                    # Ensured frame is in correct format (8-bit BGR)
                    if frame.dtype != np.uint8:
                        frame = frame.astype(np.uint8)
                    
                    # Convert to grayscale for face detection
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces using Haar Cascade
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    face_cascade = cv2.CascadeClassifier(cascade_path)
                    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
                    
                    if len(faces) > 0:
                        # Save the image
                        image_path = os.path.join(student_dir, f"{roll_number}_{count + 1}.jpg")
                        cv2.imwrite(image_path, frame)
                        captured_images.append(frame)
                        image_paths.append(image_path)
                        count += 1
                        print(f"Captured image {count}/{config.IMAGES_PER_STUDENT}")
                    else:
                        print("No face detected! Please position your face in the frame and try again.")
                
                # Cancel on ESC
                elif key == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return False, "Capture cancelled", []
            
            cap.release()
            cv2.destroyAllWindows()
            
            return True, f"Successfully captured {count} images", image_paths
        
        except Exception as e:
            return False, f"Error capturing images: {str(e)}", []
    
    def train_face_model(self, roll_number, name, image_paths=None):
        """
        Train face recognition model for a student using OpenCV
        Returns: (success: bool, message: str)
        """
        try:
            print(f"\n=== Starting face training for {name} ({roll_number}) ===")
            
            # If no image paths provided, get from student directory
            if image_paths is None:
                student_dir = os.path.join(self.training_dir, roll_number)
                if not os.path.exists(student_dir):
                    print(f"ERROR: Training directory does not exist: {student_dir}")
                    return False, "No training images found"
                
                image_paths = [os.path.join(student_dir, f) for f in os.listdir(student_dir) 
                              if f.endswith(('.jpg', '.jpeg', '.png'))]
                print(f"Found {len(image_paths)} images in directory: {student_dir}")
            else:
                print(f"Using {len(image_paths)} provided image paths")
            
            if not image_paths:
                print("ERROR: No image paths to process")
                return False, "No training images found"
            
            # Log all image paths
            for i, path in enumerate(image_paths, 1):
                print(f"  Image {i}: {path}")
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"    - Exists: Yes, Size: {size} bytes")
                else:
                    print(f"    - Exists: NO!")
            
            # Remove existing encodings for this student
            if roll_number in self.known_face_rolls:
                indices = [i for i, r in enumerate(self.known_face_rolls) if r == roll_number]
                print(f"Removing {len(indices)} existing encodings for this student")
                for index in sorted(indices, reverse=True):
                    del self.known_face_encodings[index]
                    del self.known_face_names[index]
                    del self.known_face_rolls[index]
            
            # Load Haar Cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Generate encodings from images using OpenCV
            encodings_added = 0
            for idx, image_path in enumerate(image_paths, 1):
                try:
                    print(f"\n--- Processing image {idx}/{len(image_paths)}: {os.path.basename(image_path)} ---")
                    
                    # Load image
                    print(f"  Loading image...")
                    image = cv2.imread(image_path)
                    if image is None:
                        print(f"  ERROR: Could not load image")
                        continue
                    
                    print(f"  Loaded successfully: shape={image.shape}, dtype={image.dtype}")
                    
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces using Haar Cascade
                    print(f"  Detecting faces with Haar Cascade...")
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    if len(faces) > 0:
                        print(f"  ✓ Found {len(faces)} face(s)")
                        # Use the first detected face
                        (x, y, w, h) = faces[0]
                        
                        # Extract face region
                        face_roi = gray[y:y+h, x:x+w]
                        
                        # Resize to larger size for better accuracy
                        face_roi = cv2.resize(face_roi, (200, 200))
                        
                        # Flatten to create encoding
                        encoding = face_roi.flatten()
                        
                        # Add to known faces
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(name)
                        self.known_face_rolls.append(roll_number)
                        encodings_added += 1
                        print(f"  ✓ Successfully encoded face (encoding #{encodings_added})")
                    else:
                        print(f"  WARNING: No face detected in image")
                
                except Exception as e:
                    print(f"  ERROR: Exception while processing image: {type(e).__name__}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\n=== Training Summary ===")
            print(f"Total images processed: {len(image_paths)}")
            print(f"Encodings added: {encodings_added}")
            
            if encodings_added > 0:
                # Save encodings
                print(f"Saving encodings to file...")
                self.save_encodings()
                return True, f"Face model trained successfully with {encodings_added} encodings"
            else:
                print(f"ERROR: No faces were successfully encoded")
                return False, "No faces detected in training images"
        
        except Exception as e:
            print(f"FATAL ERROR in train_face_model: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error training model: {str(e)}"
    
    def recognize_face(self, frame):
        """
        Recognize face in frame using OpenCV
        Returns: (success: bool, student_data: dict or None, face_location: tuple or None)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load Haar Cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            print(f"[Face Recognition] Detected {len(faces)} face(s)")
            
            if len(faces) == 0:
                return False, None, None
            
            # Process first detected face
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            encoding = face_roi.flatten()
            
            # Compare with known faces
            print(f"[Face Recognition] Known encodings: {len(self.known_face_encodings)}")
            
            if len(self.known_face_encodings) == 0:
                print("[Face Recognition] No trained faces in database!")
                return False, None, None
            
            min_distance = float('inf')
            best_match_index = -1
            
            for i, known_encoding in enumerate(self.known_face_encodings):
                distance = np.linalg.norm(encoding - known_encoding)
                print(f"[Face Recognition] Distance to {self.known_face_names[i]}: {distance:.2f}")
                if distance < min_distance:
                    min_distance = distance
                    best_match_index = i
            
            # Optimized threshold for 200x200 images
            # Larger images = larger distances, so threshold is higher
            threshold = 60000  # Adjusted for 200x200 images
            print(f"[Face Recognition] Best match: {self.known_face_names[best_match_index]} (distance: {min_distance:.2f}, threshold: {threshold})")
            
            if min_distance < threshold:
                # Calculate confidence (higher percentage = better match)
                confidence_percent = float(max(0, min(1.0, (threshold - min_distance) / threshold)))
                
                student_data = {
                    'roll_number': self.known_face_rolls[best_match_index],
                    'name': self.known_face_names[best_match_index],
                    'confidence': confidence_percent
                }
                print(f"[Face Recognition] ✓ MATCH FOUND: {student_data['name']} (confidence: {student_data['confidence']:.2%})")
                # Convert NumPy types to Python native types for JSON serialization
                face_location_tuple = (int(y), int(x+w), int(y+h), int(x))
                return True, student_data, face_location_tuple
            else:
                print(f"[Face Recognition] ✗ No match - distance {min_distance:.2f} exceeds threshold {threshold}")
            
            return False, None, None
        
        except Exception as e:
            print(f"Error recognizing face: {e}")
            import traceback
            traceback.print_exc()
            return False, None, None
    
    def eye_aspect_ratio(self, eye):
        """Calculate Eye Aspect Ratio (EAR)"""
        # Compute the euclidean distances between the vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        
        # Compute the euclidean distance between the horizontal eye landmarks
        C = dist.euclidean(eye[0], eye[3])
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, frame):
        """
        Detect blink in frame using OpenCV eye detection
        Returns: (blink_detected: bool, ear_left: float, ear_right: float)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load Haar Cascades
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return False, 0, 0
            
            # Get first face
            (x, y, w, h) = faces[0]
            roi_gray = gray[y:y+h, x:x+w]
            
            # Detect eyes in face region
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
            
            # Simple blink detection: if less than 2 eyes detected, consider it a blink
            # This is a simplified approach - in production you'd track eye state over time
            if len(eyes) < 2:
                # Possible blink detected
                return True, 0.2, 0.2  # Return low EAR values to indicate blink
            else:
                # Eyes open
                return False, 0.3, 0.3  # Return normal EAR values
        
        except Exception as e:
            print(f"Error detecting blink: {e}")
            return False, 0, 0
    
    def detect_blink_with_coords(self, frame):
        """
        Detect blink and return coordinates for visualization
        Returns: (blink_detected: bool, ear_left: float, ear_right: float, detection_data: dict)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load Haar Cascades
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            # Detect faces with relaxed parameters for speed
            faces = face_cascade.detectMultiScale(gray, 1.2, 4)
            
            detection_data = {'face': None, 'eyes': []}
            
            if len(faces) == 0:
                return False, 0, 0, detection_data
            
            # Get first face
            (x, y, w, h) = faces[0]
            detection_data['face'] = {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}
            
            roi_gray = gray[y:y+h, x:x+w]
            
            # VERY lenient eye detection - easier to miss eyes during blink
            # Increased scaleFactor and reduced minNeighbors for less strict detection
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.2, 2, minSize=(25, 25))
            
            # Store eye coordinates (relative to face)
            for (ex, ey, ew, eh) in eyes:
                detection_data['eyes'].append({
                    'x': int(x + ex),  # Convert to absolute coordinates
                    'y': int(y + ey),
                    'w': int(ew),
                    'h': int(eh)
                })
            
            print(f"[Blink Detection] Detected {len(eyes)} eyes")
            
            # Blink detected if fewer than 2 eyes are visible
            if len(eyes) < 2:
                print("[Blink Detection] ✓ BLINK DETECTED!")
                return True, 0.2, 0.2, detection_data
            else:
                return False, 0.3, 0.3, detection_data
        
        except Exception as e:
            print(f"Error detecting blink with coords: {e}")
            return False, 0, 0, {'face': None, 'eyes': []}
    
    def draw_face_box(self, frame, face_location, label=""):
        """Draw bounding box around detected face"""
        top, right, bottom, left = face_location
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Draw label
        if label:
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
