import { useState } from 'react';
import { ChatInterface } from './ChatInterface';
import type { Message } from './ChatInterface';
import { InputArea } from './InputArea';
import { BotMessageSquare } from 'lucide-react';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Helper to generate IDs
  const generateId = () => Math.random().toString(36).substring(2, 9);

  // Speak text via browser Web Speech API
  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // cancel any ongoing speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'hi-IN'; // Hint for Hindi
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSendText = async (text: string) => {
    const userMsg: Message = { id: generateId(), role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/text/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) throw new Error("API Error");
      
      const data = await response.json();
      const agentMsg: Message = { 
        id: generateId(), 
        role: 'agent', 
        content: data.answer,
        citations: data.citations
      };
      
      setMessages((prev) => [...prev, agentMsg]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { id: generateId(), role: 'agent', content: "Sorry, there was an error processing your request." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendAudio = async (blob: Blob) => {
    const userMsg: Message = { id: generateId(), role: 'user', content: "🎤 [Voice Message]" };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const formData = new FormData();
    // FastAPI expects file parameter for UploadFile
    formData.append('file', blob, 'recording.webm');

    try {
      const response = await fetch(`${API_BASE_URL}/voice/query`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("API Error");
      
      const data = await response.json();
      const agentMsg: Message = { 
        id: generateId(), 
        role: 'agent', 
        content: data.answer,
        citations: data.citations
      };
      
      setMessages((prev) => [...prev, agentMsg]);
      
      // Since input was voice, reply in voice
      speakText(data.answer);

    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { id: generateId(), role: 'agent', content: "Sorry, there was an error processing your voice request." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <header>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <BotMessageSquare size={24} color="var(--accent-color)" />
          <h1>rag-in-goa</h1>
        </div>
        <p>Voice-Enabled Assistant for MSMARCO-XI (Hindi)</p>
      </header>

      <ChatInterface messages={messages} isLoading={isLoading} />
      
      <InputArea 
        onSendText={handleSendText} 
        onSendAudio={handleSendAudio} 
        isLoading={isLoading} 
      />
    </>
  );
}

export default App;
