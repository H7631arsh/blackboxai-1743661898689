from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from backend.utils import setup_logging, save_uploaded_file, clean_temp_files, validate_audio_file
from backend.model.classifier import AudioContentClassifier

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', '').split(','))

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16)) * 1024 * 1024
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Setup logging
setup_logging(os.getenv('LOG_DIR', 'logs'))

# Initialize classifier
classifier = AudioContentClassifier()

def analyze_audio(audio_path: str) -> dict:
    """Analyze audio content using the classifier"""
    if not validate_audio_file(audio_path):
        raise ValueError("Invalid audio file")
    
    try:
        return classifier.predict(audio_path)
    except Exception as e:
        app.logger.error(f"Audio analysis failed: {str(e)}")
        raise

@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint for audio content analysis"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded file
    filepath = save_uploaded_file(audio_file, app.config['UPLOAD_FOLDER'])
    if not filepath:
        return jsonify({'error': 'Failed to save audio file'}), 500

    try:
        # Analyze the audio
        result = analyze_audio(filepath)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        # Clean up temporary files
        clean_temp_files(filepath)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'model_loaded': classifier.model is not None
    })

if __name__ == '__main__':
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', 8000))
    debug = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
    
    app.logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
