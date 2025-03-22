from flask import Blueprint, jsonify, request

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/whisper_transcribe/')))

# from transcribe import start_recording, stop_recording, transcribe_audio
from transcribe import transcribe_audio

transcribe_blueprint = Blueprint("transcribe", __name__)

# @transcribe_blueprint.route("/start_recording", methods=["POST"])
# def api_start_recording():
#   print("audio recording")
#   start_recording()
#   return jsonify({"status": "Recording started"})


@transcribe_blueprint.route("/", methods=["POST"])
def api_stop_recording():
    # filename = stop_recording()
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 401
    

    transcription = transcribe_audio(file)
    return jsonify({"transcription": transcription})