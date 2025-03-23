import os
import whisper
import ffmpeg

# Removed unused imports (sounddevice, numpy, wave) as they are not needed for file processing.

def convert_webm_to_wav(input_file, output_file):
    """
    Converts a .webm file to .wav using ffmpeg for improved Whisper compatibility.
    """
    try:
        ffmpeg.input(input_file).output(output_file, format='wav').run(quiet=True, overwrite_output=True)
        return output_file
    except Exception as e:  # CHANGED: Catching a general Exception instead of ffmpeg.Error
        print(f"Error during conversion: {e}")
        return None

# CHANGED: Updated transcribe_audio to handle a file-like object from Flask.
def transcribe_audio(file):
    """
    Transcribes the given audio file using Whisper.
    """
    try:
        # CHANGED: Save the incoming file to a temporary .webm file.
        input_filename = "temp_recording.webm"
        output_filename = "temp_recording.wav"
        file.save(input_filename)

        # Convert the saved .webm file to .wav for Whisper compatibility.
        convert_webm_to_wav(input_filename, output_filename)

        # Load the Whisper model and transcribe the .wav file.
        model = whisper.load_model("base")  # You can change to "small", "medium", "large"
        result = model.transcribe(output_filename)

        # CHANGED: Clean up temporary files after transcription.
        os.remove(input_filename)
        os.remove(output_filename)

        return result.get("text", "")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""
