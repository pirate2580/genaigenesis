import sounddevice as sd
import numpy as np
import wave
# import server.services.whisper.transcribe as transcribe

recording = False
audio_data = []


# finds the correct num. of input channels for audio device
def get_default_input_channels():
    """Detect the maximum supported input channels for the default microphone."""
    try:
        device_info = sd.query_devices(kind='input')
        return min(device_info['max_input_channels'], 2)  # Limit to 2 for stereo max
    except Exception as e:
        print(f"Error detecting input channels: {e}")
        return 1  # Fallback to mono if detection fails
    
# Start continuous audio recording
def start_recording():
    print("Hi")
    global recording, audio_data
    if not recording:
        recording = True
        audio_data = []
        sd.default.samplerate = 44100
        sd.default.channels = get_default_input_channels()

        def _record():
            while recording:
                buffer = sd.rec(int(44100 * 1), dtype='int16')
                sd.wait()
                audio_data.append(buffer)
                print("hello")
        
        import threading
        threading.Thread(target=_record).start()

# Stop recording and save audio to file
def stop_recording(filename="output.wav"):
    global recording, audio_data
    recording = False

    if not audio_data:
        print("No audio data captured.")
        return None

    try:
        audio_array = np.concatenate(audio_data)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(get_default_input_channels())
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(44100)
            wf.writeframes(audio_array.tobytes())

        print(f"Recording saved as {filename}")
        return filename
    except Exception as e:
        print(f"Error saving audio file: {e}")
        return None

# Transcription Logic
def transcribe_audio(filename="output.wav"):
    """
    Transcribes the given audio file using Whisper.
    """
    try:
        model = transcribe.load_model("base")  # You can change to "small", "medium", "large"
        result = model.transcribe(filename)
        return result.get("text", "")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

# # Function to record audio from your device
# def record_audio(filename="output.wav", duration=10, samplerate=44100):
#     channels = get_default_input_channels()
#     print(f"Recording with {channels} channel(s)...")
    
#     try:
#         audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
#         sd.wait()  # Wait until recording is finished
        
#         # Save the audio file
#         with wave.open(filename, 'wb') as wf:
#             wf.setnchannels(channels)
#             wf.setsampwidth(2)  # 16-bit PCM
#             wf.setframerate(samplerate)
#             wf.writeframes(audio_data.tobytes())

#         print(f"Recording saved as {filename}")
#     except Exception as e:
#         print(f"Error recording audio: {e}")

# # Function that uses Whisper to transcribe wav audio to text
# def transcribe_audio(filename="output.wav"):
#     """
#     Transcribes the given audio file using Whisper.
#     Requires the openai-whisper library and FFmpeg.
#     """
#     try:
#         # print("Loading Whisper model...")
#         model = transcribe.load_model("base")  # You can change to "small", "medium", "large" as needed
#         # print("Transcribing audio...")
#         result = model.transcribe(filename)
#         transcription = result.get("text", "")
#         # print("Transcription:")
#         # print(transcription)
#         return transcription
#     except Exception as e:
#         print(f"Error during transcription: {e}")
#         return ""


# # if __name__ == "__main__":
# #     duration = int(input("Enter recording duration in seconds: "))
# #     record_audio(duration=duration)
# #     transcribe_audio("output.wav")
