"""
JSON Database Module for Emotion Recognition System
Handles storage and retrieval of emotion detection results
"""

import json
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDatabase:
    def __init__(self, db_path='data/emotions.json'):
        """
        Initialize the JSON database
        
        Args:
            db_path (str): Path to the JSON database file
        """
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create database file and directory if they don't exist"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create database file if it doesn't exist
            if not os.path.exists(self.db_path):
                initial_data = {
                    'emotions': [],
                    'statistics': {
                        'total_detections': 0,
                        'emotion_counts': {
                            'happy': 0,
                            'sad': 0,
                            'angry': 0,
                            'surprise': 0,
                            'neutral': 0,
                            'disgust': 0,
                            'fear': 0
                        },
                        'created_at': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
                }
                self.save_data(initial_data)
                logger.info(f"Created new database at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise
    
    def load_data(self) -> Dict:
        """
        Load data from JSON database
        
        Returns:
            dict: Database contents
        """
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {str(e)}")
            return {'emotions': [], 'statistics': {}}
    
    def save_data(self, data: Dict):
        """
        Save data to JSON database
        
        Args:
            data (dict): Data to save
        """
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")
            raise
    
    def add_emotion_record(self, emotion_data: Dict) -> bool:
        """
        Add a new emotion detection record
        
        Args:
            emotion_data (dict): Emotion detection results
            
        Returns:
            bool: Success status
        """
        try:
            data = self.load_data()
            
            # Create emotion record
            record = {
                'id': len(data['emotions']) + 1,
                'timestamp': datetime.now().isoformat(),
                'dominant_emotion': emotion_data.get('dominant_emotion', 'unknown'),
                'emotions': emotion_data.get('emotions', {}),
                'confidence': emotion_data.get('emotions', {}).get(
                    emotion_data.get('dominant_emotion', 'neutral'), 0
                ),
                'source': emotion_data.get('source', 'unknown'),  # 'webcam' or 'upload'
                'face_detected': emotion_data.get('success', False),
                'face_region': emotion_data.get('face_region', {}),
                'image_path': emotion_data.get('image_path', None)
            }
            
            # Add record to emotions list
            data['emotions'].append(record)
            
            # Update statistics
            if emotion_data.get('success', False):
                dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')
                data['statistics']['total_detections'] += 1
                
                if dominant_emotion in data['statistics']['emotion_counts']:
                    data['statistics']['emotion_counts'][dominant_emotion] += 1
                
                data['statistics']['last_updated'] = datetime.now().isoformat()
            
            # Save updated data
            self.save_data(data)
            logger.info(f"Added emotion record with ID: {record['id']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding emotion record: {str(e)}")
            return False
    
    def get_recent_emotions(self, limit: int = 10) -> List[Dict]:
        """
        Get recent emotion records
        
        Args:
            limit (int): Number of records to retrieve
            
        Returns:
            list: Recent emotion records
        """
        try:
            data = self.load_data()
            emotions = data.get('emotions', [])
            
            # Return most recent records
            return emotions[-limit:] if len(emotions) > limit else emotions
            
        except Exception as e:
            logger.error(f"Error getting recent emotions: {str(e)}")
            return []
    
    def get_emotion_statistics(self) -> Dict:
        """
        Get emotion detection statistics
        
        Returns:
            dict: Statistics data
        """
        try:
            data = self.load_data()
            stats = data.get('statistics', {})
            
            # Calculate percentages
            total = stats.get('total_detections', 0)
            if total > 0:
                emotion_percentages = {}
                for emotion, count in stats.get('emotion_counts', {}).items():
                    emotion_percentages[emotion] = round((count / total) * 100, 2)
                
                stats['emotion_percentages'] = emotion_percentages
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def get_emotions_by_date(self, date_str: str) -> List[Dict]:
        """
        Get emotions detected on a specific date
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            list: Emotion records for the specified date
        """
        try:
            data = self.load_data()
            emotions = data.get('emotions', [])
            
            filtered_emotions = []
            for emotion in emotions:
                emotion_date = emotion.get('timestamp', '').split('T')[0]
                if emotion_date == date_str:
                    filtered_emotions.append(emotion)
            
            return filtered_emotions
            
        except Exception as e:
            logger.error(f"Error getting emotions by date: {str(e)}")
            return []
    
    def search_emotions(self, emotion_type: str) -> List[Dict]:
        """
        Search for emotions of a specific type
        
        Args:
            emotion_type (str): Type of emotion to search for
            
        Returns:
            list: Matching emotion records
        """
        try:
            data = self.load_data()
            emotions = data.get('emotions', [])
            
            filtered_emotions = []
            for emotion in emotions:
                if emotion.get('dominant_emotion', '').lower() == emotion_type.lower():
                    filtered_emotions.append(emotion)
            
            return filtered_emotions
            
        except Exception as e:
            logger.error(f"Error searching emotions: {str(e)}")
            return []
    
    def clear_database(self) -> bool:
        """
        Clear all emotion records (keep statistics structure)
        
        Returns:
            bool: Success status
        """
        try:
            initial_data = {
                'emotions': [],
                'statistics': {
                    'total_detections': 0,
                    'emotion_counts': {
                        'happy': 0,
                        'sad': 0,
                        'angry': 0,
                        'surprise': 0,
                        'neutral': 0,
                        'disgust': 0,
                        'fear': 0
                    },
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            self.save_data(initial_data)
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            return False
    
    def export_to_csv(self, output_path: str = 'data/emotions_export.csv') -> bool:
        """
        Export emotion data to CSV format
        
        Args:
            output_path (str): Path for CSV export
            
        Returns:
            bool: Success status
        """
        try:
            import pandas as pd
            
            data = self.load_data()
            emotions = data.get('emotions', [])
            
            if not emotions:
                logger.warning("No emotion data to export")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(emotions)
            
            # Flatten emotions dictionary into separate columns
            if 'emotions' in df.columns:
                emotions_df = pd.json_normalize(df['emotions'])
                emotions_df.columns = [f'emotion_{col}' for col in emotions_df.columns]
                df = pd.concat([df.drop('emotions', axis=1), emotions_df], axis=1)
            
            # Save to CSV
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Exported {len(emotions)} records to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False

# Create global database instance
emotion_db = EmotionDatabase()
