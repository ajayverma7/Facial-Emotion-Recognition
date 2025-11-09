"""
Facial Emotion Recognition Module
Uses DeepFace library with pre-trained models for emotion detection
"""

import cv2
import numpy as np
from deepface import DeepFace
import base64
from PIL import Image
import io
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detector with DeepFace"""
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.model_name = 'VGG-Face'  # You can also use 'Facenet', 'OpenFace', 'DeepID'
        self.detector_backend = 'opencv'  # opencv, ssd, dlib, mtcnn, retinaface
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        logger.info("EmotionDetector initialized successfully")
    
    def detect_emotion_from_image(self, image_path):
        """
        Detect emotions from an image file
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Emotion analysis results
        """
        try:
            # Analyze emotions using DeepFace
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['emotion'],
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            
            # Handle both single face and multiple faces results
            if isinstance(result, list):
                result = result[0]  # Take first face if multiple detected
            
            emotions = result['emotion']
            dominant_emotion = result['dominant_emotion']
            
            # Get face region
            face_region = result.get('region', {})
            
            return {
                'success': True,
                'dominant_emotion': dominant_emotion,
                'emotions': emotions,
                'face_region': face_region,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting emotion from image: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def detect_emotion_from_frame(self, frame):
        """
        Detect emotions from a video frame (numpy array)
        
        Args:
            frame (numpy.ndarray): Video frame
            
        Returns:
            dict: Emotion analysis results with annotated frame
        """
        try:
            # Analyze emotions using DeepFace
            result = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            
            # Handle both single face and multiple faces results
            if isinstance(result, list):
                result = result[0]  # Take first face if multiple detected
            
            emotions = result['emotion']
            dominant_emotion = result['dominant_emotion']
            face_region = result.get('region', {})
            
            # Draw bounding box and emotion label on frame
            annotated_frame = self.draw_emotion_on_frame(frame, face_region, dominant_emotion, emotions)
            
            return {
                'success': True,
                'dominant_emotion': dominant_emotion,
                'emotions': emotions,
                'face_region': face_region,
                'annotated_frame': annotated_frame,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting emotion from frame: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'annotated_frame': frame,
                'timestamp': datetime.now().isoformat()
            }
    
    def draw_emotion_on_frame(self, frame, face_region, dominant_emotion, emotions):
        """
        Draw emotion information on the frame
        
        Args:
            frame (numpy.ndarray): Original frame
            face_region (dict): Face bounding box coordinates
            dominant_emotion (str): Dominant emotion
            emotions (dict): All emotion probabilities
            
        Returns:
            numpy.ndarray: Annotated frame
        """
        annotated_frame = frame.copy()
        
        if face_region:
            x, y, w, h = face_region.get('x', 0), face_region.get('y', 0), \
                        face_region.get('w', 0), face_region.get('h', 0)
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw dominant emotion label
            label = f"{dominant_emotion}: {emotions[dominant_emotion]:.1f}%"
            cv2.putText(annotated_frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Draw top 3 emotions
            sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (emotion, confidence) in enumerate(sorted_emotions):
                text = f"{emotion}: {confidence:.1f}%"
                cv2.putText(annotated_frame, text, (x, y + h + 25 + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return annotated_frame
    
    def base64_to_image(self, base64_string):
        """
        Convert base64 string to PIL Image
        
        Args:
            base64_string (str): Base64 encoded image
            
        Returns:
            PIL.Image: Decoded image
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            return image
            
        except Exception as e:
            logger.error(f"Error converting base64 to image: {str(e)}")
            return None
    
    def image_to_base64(self, image):
        """
        Convert PIL Image to base64 string
        
        Args:
            image (PIL.Image): Image to convert
            
        Returns:
            str: Base64 encoded image
        """
        try:
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            return None
    
    def preload_models(self):
        """
        Preload DeepFace models to improve performance
        """
        try:
            logger.info("Preloading DeepFace models...")
            # Create a dummy image to trigger model loading
            dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
            DeepFace.analyze(dummy_img, actions=['emotion'], 
                           detector_backend=self.detector_backend, 
                           enforce_detection=False)
            logger.info("Models preloaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not preload models: {str(e)}")

# Create global instance
emotion_detector = EmotionDetector()
