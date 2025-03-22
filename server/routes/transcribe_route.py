from flask import Blueprint, jsonify, request

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/whisper_transcribe/')))

from transcribe import start_recording, stop_recording, transcribe_audio

transcribe_blueprint = Blueprint("transcribe", __name__)

@transcribe_blueprint.route("/start_recording", methods=["POST"])
def api_start_recording():
  start_recording()
  return jsonify({"status": "Recording started"})


@transcribe_blueprint.route("/stop_recording", methods=["POST"])
def api_stop_recording():
    filename = stop_recording()
    if not filename:
        return jsonify({"error": "No audio recorded"}), 400

    transcription = transcribe_audio(filename)
    return jsonify({"transcription": transcription})