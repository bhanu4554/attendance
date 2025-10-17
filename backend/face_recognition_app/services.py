# Temporarily commented out for basic setup
# import face_recognition
import cv2
import numpy as np
from PIL import Image
import os
import time
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import FaceEncoding, FaceRecognitionLog

User = get_user_model()


class FaceRecognitionService:
    """Service class for face recognition operations - temporarily disabled"""
    
    def __init__(self):
        self.tolerance = getattr(settings, 'FACE_RECOGNITION_TOLERANCE', 0.6)
        self.model = getattr(settings, 'FACE_RECOGNITION_MODEL', 'hog')
    
    def encode_face_from_image(self, image_path_or_array):
        """
        Extract face encoding from an image
        Args:
            image_path_or_array: Path to image file or numpy array
        Returns:
            tuple: (encoding_array, success_boolean, error_message)
        """
        try:
            start_time = time.time()
            
            # Load image
            if isinstance(image_path_or_array, str):
                image = face_recognition.load_image_file(image_path_or_array)
            else:
                image = image_path_or_array
            
            # Find face locations
            face_locations = face_recognition.face_locations(
                image, model=self.model
            )
            
            processing_time = time.time() - start_time
            
            if len(face_locations) == 0:
                return None, False, "No face detected in the image", processing_time
            
            if len(face_locations) > 1:
                return None, False, "Multiple faces detected. Please use an image with only one face", processing_time
            
            # Extract face encoding
            face_encodings = face_recognition.face_encodings(
                image, face_locations, model='large'
            )
            
            if len(face_encodings) == 0:
                return None, False, "Could not encode the face", processing_time
            
            processing_time = time.time() - start_time
            return face_encodings[0], True, None, processing_time
            
        except Exception as e:
            return None, False, str(e), time.time() - start_time
    
    def recognize_face(self, image_path_or_array, location=None):
        """
        Recognize a face from an image
        Args:
            image_path_or_array: Path to image file or numpy array
            location: Optional location string for logging
        Returns:
            dict: Recognition result with user, confidence, success status
        """
        start_time = time.time()
        
        try:
            # Extract face encoding from input image
            encoding, success, error, proc_time = self.encode_face_from_image(
                image_path_or_array
            )
            
            if not success:
                self._log_recognition_attempt(
                    None, 'no_face' if 'No face' in error else 'failed',
                    None, location, error, proc_time
                )
                return {
                    'success': False,
                    'error': error,
                    'user': None,
                    'confidence': None
                }
            
            # Get all stored face encodings
            stored_encodings = FaceEncoding.objects.filter(is_active=True)
            
            if not stored_encodings.exists():
                self._log_recognition_attempt(
                    None, 'unknown_person', None, location,
                    "No registered users found", proc_time
                )
                return {
                    'success': False,
                    'error': 'No registered users found',
                    'user': None,
                    'confidence': None
                }
            
            # Compare with stored encodings
            best_match = None
            best_distance = float('inf')
            
            for stored in stored_encodings:
                stored_encoding = np.array(stored.get_encoding())
                
                # Calculate face distance
                distance = face_recognition.face_distance(
                    [stored_encoding], encoding
                )[0]
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = stored
            
            # Check if best match is within tolerance
            confidence = 1 - best_distance
            processing_time = time.time() - start_time
            
            if best_distance <= self.tolerance:
                self._log_recognition_attempt(
                    best_match.user, 'success', confidence,
                    location, None, processing_time
                )
                return {
                    'success': True,
                    'user': best_match.user,
                    'confidence': confidence,
                    'error': None
                }
            else:
                self._log_recognition_attempt(
                    None, 'unknown_person', confidence,
                    location, "Face not recognized", processing_time
                )
                return {
                    'success': False,
                    'error': 'Face not recognized',
                    'user': None,
                    'confidence': confidence
                }
        
        except Exception as e:
            processing_time = time.time() - start_time
            self._log_recognition_attempt(
                None, 'failed', None, location, str(e), processing_time
            )
            return {
                'success': False,
                'error': str(e),
                'user': None,
                'confidence': None
            }
    
    def register_user_face(self, user, image_path_or_array):
        """
        Register a user's face encoding
        Args:
            user: User instance
            image_path_or_array: Path to image file or numpy array
        Returns:
            tuple: (success_boolean, error_message)
        """
        try:
            # Extract face encoding
            encoding, success, error, proc_time = self.encode_face_from_image(
                image_path_or_array
            )
            
            if not success:
                return False, error
            
            # Save or update face encoding
            face_encoding, created = FaceEncoding.objects.get_or_create(
                user=user,
                defaults={
                    'confidence_threshold': self.tolerance,
                    'is_active': True
                }
            )
            
            face_encoding.set_encoding(encoding)
            face_encoding.save()
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def _log_recognition_attempt(self, user, status, confidence, location, error, processing_time):
        """Log face recognition attempt"""
        FaceRecognitionLog.objects.create(
            user=user,
            status=status,
            confidence_score=confidence,
            location=location,
            error_message=error,
            processing_time=processing_time
        )
    
    def preprocess_image(self, image_file):
        """
        Preprocess uploaded image for face recognition
        Args:
            image_file: Django uploaded file
        Returns:
            numpy array of the processed image
        """
        try:
            # Convert to PIL Image
            pil_image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(pil_image)
            
            # Optional: Resize if image is too large
            height, width = image_array.shape[:2]
            if width > 1920 or height > 1080:
                # Calculate new dimensions maintaining aspect ratio
                aspect_ratio = width / height
                if width > height:
                    new_width = 1920
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = 1080
                    new_width = int(new_height * aspect_ratio)
                
                # Resize using cv2
                image_array = cv2.resize(image_array, (new_width, new_height))
            
            return image_array
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def get_face_landmarks(self, image_path_or_array):
        """
        Get face landmarks for debugging/visualization
        Args:
            image_path_or_array: Path to image file or numpy array
        Returns:
            dict: Face landmarks data
        """
        try:
            if isinstance(image_path_or_array, str):
                image = face_recognition.load_image_file(image_path_or_array)
            else:
                image = image_path_or_array
            
            face_landmarks_list = face_recognition.face_landmarks(image)
            
            return {
                'success': True,
                'landmarks': face_landmarks_list,
                'faces_found': len(face_landmarks_list)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'landmarks': [],
                'faces_found': 0
            }