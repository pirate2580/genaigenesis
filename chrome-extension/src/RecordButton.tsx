import React, { useState, useRef } from 'react';

const AudioButton: React.FC = () => {
  // bool to check if audio is recording
  const [isRecording, setIsRecording] = useState<boolean>(false);
  // pointer to store the audio recording for mediaRecorder
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  // blob thats sent to backend
  const recordedChunks = useRef<Blob[]>([]);

  // toggle function to toggle the recording
  const toggleRecording = async () => {
    if (!isRecording) {
      // Start recording
      setIsRecording(true);
      
      // new recording
      recordedChunks.current = [];
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event: BlobEvent) => {
          if (event.data.size > 0) {
            recordedChunks.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          // Create a blob from the recorded chunks
          const audioBlob = new Blob(recordedChunks.current, { type: 'audio/webm' });
          // Make a dummy API request to your backend
          try {
            const response = await fetch('http://127.0.0.1:5000/transcribe', {
              method: 'POST',
              body: audioBlob,
            });
            console.log('Dummy API call completed:', response);
          } catch (error) {
            console.error('Error during dummy API call:', error);
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
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
    }
  };

  return (
    <button onClick={toggleRecording}>
      {isRecording ? 'Stop Recording' : 'Start Recording'}
    </button>
  );
};

export default AudioButton;
