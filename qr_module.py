"""
QR Code Generation and Scanning Module
"""

import qrcode
import cv2
import json
import os
import uuid
from pyzbar.pyzbar import decode
import config

class QRCodeManager:
    def __init__(self):
        self.qr_dir = config.QR_CODES_DIR
    
    def generate_qr_code(self, student_data):
        """
        Generate QR code for a student
        Returns: (success: bool, qr_path: str, message: str)
        """
        try:
            # Create unique identifier
            unique_id = str(uuid.uuid4())[:8]
            
            # Prepare QR data
            qr_data = {
                'roll_number': student_data['roll_number'],
                'name': student_data['name'],
                'branch': student_data['branch'],
                'unique_id': unique_id
            }
            
            # Convert to JSON string
            qr_content = json.dumps(qr_data)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code
            filename = f"qr_{student_data['roll_number']}_{unique_id}.png"
            qr_path = os.path.join(self.qr_dir, filename)
            img.save(qr_path)
            
            # Return relative path for web access
            relative_path = f"static/qr_codes/{filename}"
            return True, relative_path, "QR code generated successfully"
        
        except Exception as e:
            return False, "", f"Error generating QR code: {str(e)}"
    
    def scan_qr_code(self, frame):
        """
        Scan QR code from webcam frame and validate against database
        Returns: (success: bool, student_data: dict or None)
        """
        try:
            # Decode QR codes in the frame
            decoded_objects = decode(frame)
            
            if decoded_objects:
                for obj in decoded_objects:
                    # Get QR code data
                    qr_data = obj.data.decode('utf-8')
                    
                    try:
                        # Parse JSON data
                        student_data = json.loads(qr_data)
                        
                        # Validate required fields
                        if all(key in student_data for key in ['roll_number', 'name', 'branch']):
                            # SECURITY CHECK: Verify student exists in database
                            import pandas as pd
                            import config
                            
                            try:
                                df = pd.read_csv(config.STUDENTS_CSV)
                                student_exists = student_data['roll_number'] in df['roll_number'].values
                                
                                if not student_exists:
                                    print(f"[QR Security] Rejected QR code for deleted student: {student_data['roll_number']}")
                                    return False, None
                                
                                print(f"[QR Security] Validated student exists: {student_data['roll_number']}")
                                return True, student_data
                            except Exception as e:
                                print(f"[QR Security] Error validating student: {e}")
                                return False, None
                    except json.JSONDecodeError:
                        continue
            
            return False, None
        
        except Exception as e:
            print(f"Error scanning QR code: {e}")
            return False, None
    
    def draw_qr_box(self, frame, decoded_objects):
        """Draw bounding box around detected QR codes"""
        for obj in decoded_objects:
            points = obj.polygon
            if len(points) == 4:
                pts = [(point.x, point.y) for point in points]
                pts = [(int(x), int(y)) for x, y in pts]
                
                # Draw polygon
                for i in range(4):
                    cv2.line(frame, pts[i], pts[(i + 1) % 4], (0, 255, 0), 3)
        
        return frame
