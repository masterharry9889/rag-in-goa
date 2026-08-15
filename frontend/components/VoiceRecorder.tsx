import { useState, useRef } from 'react';

const VoiceRecorder = ({ onVoiceResult }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks);
        // We'll just call the onVoiceResult callback with the blob.
        onVoiceResult(audioBlob);
      });

      setIsRecording(true);
      mediaRecorder.start();
    } catch (err) {
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    // Stop the stream tracks to release the microphone
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsRecording(false);
    mediaRecorderRef.current = null;
  };

  return (
    <div className="space-y-4">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isRecording ? false : !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia}
        className={`w-full py-3 px-4 rounded-lg ${
          isRecording
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-gray-700 hover:bg-gray-600 text-white'
        }`}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      {!isRecording && transcript && (
        <div className="bg-gray-800 p-4 rounded-lg">
          <p className="font-medium">Transcript:</p>
          <p className="mt-2 text-gray-300">{transcript}</p>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;