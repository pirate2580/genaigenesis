import React, { useState, useRef } from 'react';

// CHANGED: Added the onTranscription prop to receive transcription text from the parent
interface AudioButtonProps {
  onTranscription: (transcription: string) => void;
  // callback function to notify that transcribe success
  onTranscriptionStart?: () => void;
}

const AudioButton: React.FC<AudioButtonProps> = ({ onTranscription, onTranscriptionStart }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunks = useRef<Blob[]>([]);

  const toggleRecording = async () => {
    if (!isRecording) {
      // Start recording
      setIsRecording(true);
      recordedChunks.current = [];
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) recordedChunks.current.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(recordedChunks.current, { type: 'audio/webm' });
          // CHANGED: Wrap the blob in a FormData object to match what the Flask API expects
          const formData = new FormData();
          formData.append('file', audioBlob, 'recording.webm');

          if (onTranscriptionStart) {
            onTranscriptionStart();
          }

          try {
            const response = await fetch('http://127.0.0.1:5000/transcribe', {
              method: 'POST',
              body: formData, // CHANGED: Using FormData instead of raw blob
            });

            if (!response.ok) {
              console.error("Transcription request failed");
              return;
            }

            const json = await response.json();
            // CHANGED: Call the callback with the transcription text
            onTranscription(json.transcription);
          } catch (error) {
            console.error('Error during transcription API call:', error);
          }
        };

        mediaRecorder.start();
      } catch (error) {
        console.error('Error starting recording:', error);
        setIsRecording(false);
      }
    } else {
      // Stop recording
      setIsRecording(false);
      mediaRecorderRef.current?.stop();
    }
  };

  return (
    <button onClick={toggleRecording}>
      {isRecording ? 'Stop & Transcribe' : 'Start Recording'}
    </button>
  );
};

export default AudioButton;
