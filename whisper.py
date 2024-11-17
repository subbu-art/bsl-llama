from faster_whisper import WhisperModel

def transcribe_audio(audio_file_path, model_size="small"):
    """
    Transcribe audio file to text using Faster Whisper.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        model_size (str): Size of the Whisper model to use ('tiny', 'base', 'small', 'medium', 'large')
        
    Returns:
        str: The transcribed text
    """
    # Load the model
    model = WhisperModel(model_size)
    
    # Transcribe the audio
    segments, _ = model.transcribe(audio_file_path)
    
    
    # Combine all segments into a single text
    full_text = " ".join([segment.text for segment in segments])
    
    return full_text

# Example usage
'''audio_path = "Recording.wav"
text = transcribe_audio(audio_path)
print(text)'''
