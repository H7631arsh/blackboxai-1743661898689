import os
import logging
from datetime import datetime
import uuid
from typing import Optional, Dict, Any
import json
from pathlib import Path

def setup_logging(log_dir: str = "logs") -> None:
    """Configure logging for the application"""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")),
            logging.StreamHandler()
        ]
    )

def generate_unique_filename(extension: str = "wav") -> str:
    """Generate a unique filename with the given extension"""
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{extension}"

def save_uploaded_file(file, upload_folder: str) -> Optional[str]:
    """Save an uploaded file to the specified folder"""
    try:
        os.makedirs(upload_folder, exist_ok=True)
        filename = generate_unique_filename()
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filepath
    except Exception as e:
        logging.error(f"Error saving file: {str(e)}")
        return None

def clean_temp_files(filepath: str) -> None:
    """Clean up temporary files"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        logging.error(f"Error cleaning temp files: {str(e)}")

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    default_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": True
        },
        "model": {
            "sample_rate": 16000,
            "max_duration": 30.0
        }
    }
    
    try:
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return default_config
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        return default_config

def validate_audio_file(filepath: str) -> bool:
    """Basic validation for audio files"""
    try:
        # Check if file exists and has valid audio extension
        valid_extensions = {'.wav', '.mp3', '.ogg', '.flac'}
        return (
            os.path.exists(filepath) and 
            os.path.splitext(filepath)[1].lower() in valid_extensions
        )
    except Exception as e:
        logging.error(f"Error validating audio file: {str(e)}")
        return False