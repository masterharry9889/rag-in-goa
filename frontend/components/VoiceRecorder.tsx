import { useState, useRef } from 'react';

const VoiceRecorder = ({ onVoiceResult }: { onVoiceResult: (blob: Blob) => void }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks: Blob[] = [];

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
    <div className="space-y-4 flex flex-col items-center">
      {isRecording && (
        <div className="absolute inset-0 bg-red-500/10 rounded-full blur-2xl animate-pulse pointer-events-none"></div>
      )}
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isRecording ? false : !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia}
        className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl ${
          isRecording
            ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-[0_0_40px_rgba(239,68,68,0.6)]'
            : 'bg-brand-main hover:bg-brand-light text-white hover:scale-105 hover:shadow-[0_0_30px_rgba(73,154,19,0.5)] border-4 border-brand-dark'
        }`}
        title={isRecording ? 'Stop Recording' : 'Start Recording'}
      >
        <svg 
          className="w-10 h-10" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          {isRecording ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          )}
        </svg>
      </button>
      <div className="text-sm font-medium tracking-wide">
        {isRecording ? (
          <span className="text-red-400 animate-pulse">Recording... Click to stop</span>
        ) : (
          <span className="text-brand-light">Click to Start</span>
        )}
      </div>
    </div>
  );
};

export default VoiceRecorder;