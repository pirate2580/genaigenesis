from flask import Blueprint, jsonify, request
import os
import sys

# Ensure the correct path to the transcribe.py module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/whisper_transcribe/')))

from transcribe import transcribe_audio

transcribe_blueprint = Blueprint("transcribe", __name__)

# This endpoint now receives the audio file sent from the frontend via FormData.
@transcribe_blueprint.route("/", methods=["POST"])
def api_stop_recording():
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 401

    # Call the updated transcribe_audio function with the file object.
    transcription = transcribe_audio(file)
    return jsonify({"transcription": transcription})
