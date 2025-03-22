import React, { useState, useRef } from 'react';

const AudioButton: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunks = useRef<Blob[]>([]);

  // const startRecording = async () => {
  //   recordedChunks.current = [];
  //   try {
  //     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  //     const mediaRecorder = new MediaRecorder(stream);
  //     mediaRecorderRef.current = mediaRecorder;

      

  //     // Gather the audio data as it becomes available.
  //     mediaRecorder.ondataavailable = (event) => {
  //       if (event.data.size > 0) {
  //         recordedChunks.current.push(event.data);
  //       }
  //     };

  //     // This will be called when recording stops.
  //     mediaRecorder.onstop = async () => {
  //       const audioBlob = new Blob(recordedChunks.current, { type: 'audio/webm' });
  //       try {
  //         await fetch('http://127.0.0.1:5000/transcribe', {
  //           method: 'POST',
  //           body: audioBlob,
  //         });
  //         console.log('Transcription API call made.');
  //       } catch (error) {
  //         console.error('Error during transcription API call:', error);
  //       }
  //     };

  //     mediaRecorder.start();
  //   } catch (error) {
  //     console.error('Error starting recording:', error);
  //     setIsRecording(false);
  //   }
  // };
  const startRecording = async () => {
    recordedChunks.current = [];
  
    // 1. Try to get the audio stream from the user's device.
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("User media stream obtained.");
    } catch (error) {
      console.error("Error obtaining user media (audio):", error);
      setIsRecording(false);
      return;
    }
  
    // 2. Try to create the MediaRecorder instance.
    let mediaRecorder;
    try {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      console.log("MediaRecorder created successfully.");
    } catch (error) {
      console.error("Error creating MediaRecorder:", error);
      setIsRecording(false);
      return;
    }
  
    // 3. Set up the data gathering event.
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.current.push(event.data);
      }
    };
  
    // 4. Set up the stop event to send the audio to the transcription API.
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(recordedChunks.current, { type: 'audio/webm' });
      try {
        await fetch('http://127.0.0.1:5000/transcribe', {
          method: 'POST',
          body: audioBlob,
        });
        console.log("Transcription API call made.");
      } catch (error) {
        console.error("Error during transcription API call:", error);
      }
    };
  
    // 5. Try to start the MediaRecorder.
    try {
      mediaRecorder.start();
      console.log("Recording started.");
    } catch (error) {
      console.error("Error starting MediaRecorder:", error);
      setIsRecording(false);
      return;
    }
  };
  

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording();
      setIsRecording(false);
    } else {
      setIsRecording(true);
      await startRecording();
    }
  };

  return (
    <button onClick={toggleRecording}>
      {isRecording ? 'Stop Recording' : 'Start Recording'}
    </button>
  );
};

export default AudioButton;
