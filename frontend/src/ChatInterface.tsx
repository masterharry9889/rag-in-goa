import React from 'react';
import { Bot, User } from 'lucide-react';

export interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  citations?: Array<{
    id: string;
    text: string;
    score: number;
    metadata: any;
  }>;
}

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, isLoading }) => {
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="chat-container" ref={scrollRef}>
      {messages.length === 0 && (
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: 'auto', marginBottom: 'auto' }}>
          <Bot size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
          <p>नमस्ते! मैं कैसे सहायता कर सकता हूँ?</p>
          <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Send a text or voice message to start.</p>
        </div>
      )}

      {messages.map((msg) => (
        <div key={msg.id} className={`message ${msg.role}`}>
          <div className="message-bubble">
            {msg.content}
          </div>
          
          {msg.citations && msg.citations.length > 0 && (
            <div className="citations">
              {msg.citations.map((cite, idx) => (
                <div key={idx} className="citation-badge">
                  Source: {cite.metadata?.passage_id || cite.id.substring(0, 8)}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="message agent">
          <div className="message-bubble" style={{ padding: '0.5rem 1rem' }}>
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
