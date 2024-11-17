from flask import Flask, render_template, request, jsonify
from model import translate_to_bsl
from faster_whisper import WhisperModel
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Whisper model globally
whisper_model = WhisperModel("small", device="cpu")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Get BSL translation
        bsl_translation = translate_to_bsl(text)
        
        # Here you would call your video generation function
        # For now, we'll return a placeholder
        video_path = "/static/placeholder.mp4"
        
        return jsonify({
            'translation': bsl_translation,
            'video_path': video_path
        })
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe-audio', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'temp_audio.wav')
        
        # Save the audio file temporarily
        audio_file.save(temp_path)
        print(f"Saved audio file to: {temp_path}")
        
        # Transcribe the audio using Whisper
        segments, _ = whisper_model.transcribe(temp_path)
        transcribed_text = " ".join([segment.text for segment in segments])
        
        # Clean up
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        return jsonify({'text': transcribed_text})
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)