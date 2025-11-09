import os
import base64
from datetime import datetime
from flask import current_app
from pydub import AudioSegment

def save_audio_file(audio_data, application_id, question_id):
    """Save and compress audio file from base64 data"""
    try:
        # Decode base64 audio data
        if ',' in audio_data:
            # Remove data URL prefix if present
            audio_data = audio_data.split(',')[1]
        
        audio_bytes = base64.b64decode(audio_data)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = f"app_{application_id}_q_{question_id}_{timestamp}.webm"
        compressed_filename = f"app_{application_id}_q_{question_id}_{timestamp}.mp3"
        
        # Full path
        upload_folder = current_app.config['UPLOAD_FOLDER']
        original_path = os.path.join(upload_folder, 'interviews', original_filename)
        compressed_path = os.path.join(upload_folder, 'interviews', compressed_filename)
        
        # Save original file temporarily
        with open(original_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Compress audio using pydub (requires ffmpeg)
        try:
            # Load audio from WebM format
            audio = AudioSegment.from_file(original_path, format="webm")
            
            # Normalize audio (helps with consistent volume)
            audio = audio.normalize()
            
            # Export as MP3 with optimized settings for speech
            # These settings provide good quality for speech while reducing file size significantly
            # - Bitrate: 64kbps is optimal for speech (saves ~70-80% space vs original)
            # - Sample rate: 22050 Hz is sufficient for speech (reduces file size)
            # - Mono: Speech doesn't need stereo, saves space
            audio.export(
                compressed_path,
                format="mp3",
                bitrate="64k",  # 64kbps for speech - good balance of quality and size
                parameters=[
                    "-ar", "22050",  # Sample rate: 22.05kHz (sufficient for speech)
                    "-ac", "1",      # Mono channel (speech doesn't need stereo)
                    "-q:a", "2"      # Quality setting (0-9, lower is better quality)
                ]
            )
            
            # Verify compressed file was created and has size
            if os.path.exists(compressed_path) and os.path.getsize(compressed_path) > 0:
                # Remove original WebM file to save space
                try:
                    os.remove(original_path)
                except OSError:
                    pass  # Continue if deletion fails
                
                # Return relative path for compressed file
                return os.path.join('uploads', 'interviews', compressed_filename)
            else:
                # Compressed file not created properly, keep original
                print("Compressed file not created properly, using original")
                return os.path.join('uploads', 'interviews', original_filename)
            
        except Exception as compress_error:
            # If compression fails (e.g., ffmpeg not installed), keep original file
            print(f"Error compressing audio: {compress_error}")
            print("Falling back to original WebM file. Make sure ffmpeg is installed.")
            # Remove compressed file if it exists but is invalid
            try:
                if os.path.exists(compressed_path):
                    os.remove(compressed_path)
            except OSError:
                pass
            return os.path.join('uploads', 'interviews', original_filename)
        
    except Exception as e:
        print(f"Error saving audio file: {e}")
        return None

def process_audio_chunk(audio_chunk, sample_rate=16000):
    """Process audio chunk for streaming (if needed)"""
    # This function can be expanded for real-time audio processing
    # For now, it's a placeholder
    return audio_chunk

