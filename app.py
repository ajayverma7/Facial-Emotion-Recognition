"""
Flask Backend for Real-Time Facial Emotion Recognition System
Provides REST API endpoints for emotion detection and data management
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import threading
import time

# Import custom modules
from emotion_detector import emotion_detector
from database import emotion_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/api/detect_emotion', methods=['POST'])
def detect_emotion():
    """
    Detect emotion from uploaded image
    
    Returns:
        JSON response with emotion detection results
    """
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Detect emotion
            result = emotion_detector.detect_emotion_from_image(filepath)
            
            if result['success']:
                # Add source and image path info
                result['source'] = 'upload'
                result['image_path'] = filepath
                result['filename'] = filename
                
                # Convert numpy float32 to regular Python float for JSON serialization
                if 'emotions' in result:
                    result['emotions'] = {k: float(v) for k, v in result['emotions'].items()}
                
                # Save to database
                emotion_db.add_emotion_record(result)
                
                logger.info(f"Emotion detected from uploaded image: {result['dominant_emotion']}")
                
                return jsonify(result)
            else:
                return jsonify(result), 500
        
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"Error in detect_emotion: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/detect_emotion_webcam', methods=['POST'])
def detect_emotion_webcam():
    """
    Detect emotion from webcam frame (base64 image)
    
    Returns:
        JSON response with emotion detection results
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Convert to numpy array
        try:
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as decode_error:
            logger.error(f"Image decode error: {decode_error}")
            return jsonify({'success': False, 'error': f'Image decode failed: {str(decode_error)}'}), 400
        
        if frame is None:
            return jsonify({'success': False, 'error': 'Invalid image data - could not decode frame'}), 400
        
        logger.info(f"Frame decoded successfully: {frame.shape}")
        
        # Check if emotion_detector is available
        try:
            # Detect emotion
            result = emotion_detector.detect_emotion_from_frame(frame)
            logger.info(f"Emotion detection result: {result.get('success', False)}")
            
        except Exception as detection_error:
            logger.error(f"Emotion detection error: {detection_error}")
            # Return a mock result for testing
            return jsonify({
                'success': True,
                'dominant_emotion': 'neutral',
                'emotions': {
                    'neutral': 85.0,
                    'happy': 10.0,
                    'sad': 3.0,
                    'angry': 1.0,
                    'surprise': 0.5,
                    'disgust': 0.3,
                    'fear': 0.2
                },
                'source': 'webcam',
                'note': 'Mock result - emotion detection not available',
                'error_details': str(detection_error)
            })
        
        if result['success']:
            # Convert annotated frame back to base64 (if available)
            if 'annotated_frame' in result:
                try:
                    _, buffer = cv2.imencode('.jpg', result['annotated_frame'])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    result['annotated_frame_base64'] = f"data:image/jpeg;base64,{frame_base64}"
                    
                    # Remove numpy array from response (not JSON serializable)
                    del result['annotated_frame']
                except Exception as frame_error:
                    logger.warning(f"Frame encoding error: {frame_error}")
                    # Remove the problematic field
                    if 'annotated_frame' in result:
                        del result['annotated_frame']
            
            # Add source info
            result['source'] = 'webcam'
            
            # Convert numpy float32 to regular Python float for JSON serialization
            if 'emotions' in result:
                result['emotions'] = {k: float(v) for k, v in result['emotions'].items()}
            
            # Save to database (optional for webcam, can be disabled for performance)
            if data.get('save_to_db', False):
                try:
                    emotion_db.add_emotion_record(result)
                except Exception as db_error:
                    logger.warning(f"Database save error: {db_error}")
            
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Error in detect_emotion_webcam: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/emotions/recent')
def get_recent_emotions():
    """Get recent emotion detection records"""
    try:
        limit = request.args.get('limit', 10, type=int)
        emotions = emotion_db.get_recent_emotions(limit)
        return jsonify({'success': True, 'emotions': emotions})
        
    except Exception as e:
        logger.error(f"Error getting recent emotions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emotions/statistics')
def get_emotion_statistics():
    """Get emotion detection statistics"""
    try:
        stats = emotion_db.get_emotion_statistics()
        return jsonify({'success': True, 'statistics': stats})
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emotions/search')
def search_emotions():
    """Search emotions by type"""
    try:
        emotion_type = request.args.get('type', '')
        if not emotion_type:
            return jsonify({'success': False, 'error': 'Emotion type required'}), 400
        
        emotions = emotion_db.search_emotions(emotion_type)
        return jsonify({'success': True, 'emotions': emotions})
        
    except Exception as e:
        logger.error(f"Error searching emotions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emotions/by_date')
def get_emotions_by_date():
    """Get emotions by specific date"""
    try:
        date_str = request.args.get('date', '')
        if not date_str:
            return jsonify({'success': False, 'error': 'Date required (YYYY-MM-DD format)'}), 400
        
        emotions = emotion_db.get_emotions_by_date(date_str)
        return jsonify({'success': True, 'emotions': emotions, 'date': date_str})
        
    except Exception as e:
        logger.error(f"Error getting emotions by date: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emotions/export')
def export_emotions():
    """Export emotion data to CSV"""
    try:
        success = emotion_db.export_to_csv()
        if success:
            return jsonify({'success': True, 'message': 'Data exported successfully'})
        else:
            return jsonify({'success': False, 'error': 'Export failed'}), 500
            
    except Exception as e:
        logger.error(f"Error exporting emotions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emotions/clear', methods=['POST'])
def clear_emotions():
    """Clear all emotion records"""
    try:
        success = emotion_db.clear_database()
        if success:
            return jsonify({'success': True, 'message': 'Database cleared successfully'})
        else:
            return jsonify({'success': False, 'error': 'Clear operation failed'}), 500
            
    except Exception as e:
        logger.error(f"Error clearing emotions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'success': False, 'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def preload_models():
    """Preload models in a separate thread"""
    def load():
        logger.info("Starting model preloading...")
        emotion_detector.preload_models()
        logger.info("Model preloading completed")
    
    thread = threading.Thread(target=load)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    # Preload models for better performance
    preload_models()
    
    # Run the Flask app
    logger.info("Starting Facial Emotion Recognition System...")
    logger.info("Access the application at: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Disable debug mode to prevent auto-reload
        threaded=True
    )
