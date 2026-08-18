import React, { useState, useRef } from 'react';
import { Mic, Square, Send } from 'lucide-react';

interface InputAreaProps {
  onSendText: (text: string) => void;
  onSendAudio: (blob: Blob) => void;
  isLoading: boolean;
}

export const InputArea: React.FC<InputAreaProps> = ({ onSendText, onSendAudio, isLoading }) => {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleTextSubmit = () => {
    if (text.trim() && !isLoading) {
      onSendText(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleTextSubmit();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        onSendAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop()); // release mic
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Microphone access is required to use voice input.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="input-wrapper">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={isRecording ? "Recording voice..." : "Type a message or press mic..."}
        disabled={isRecording || isLoading}
        rows={1}
      />
      <div className="actions">
        {isRecording ? (
          <button className="mic recording" onClick={stopRecording} disabled={isLoading}>
            <Square size={20} />
          </button>
        ) : (
          <button className="mic" onClick={startRecording} disabled={isLoading || text.trim().length > 0}>
            <Mic size={20} />
          </button>
        )}
        <button 
          className="primary" 
          onClick={handleTextSubmit} 
          disabled={isLoading || isRecording || text.trim().length === 0}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};
