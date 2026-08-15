import './globals.css';
import { Inter } from 'next/font/google';
import VoiceRecorder from '@/components/VoiceRecorder';
import AnswerCard from '@/components/AnswerCard';
import LatencyBadge from '@/components/LatencyBadge';

const inter = Inter({ subsets: ['latin'] });

export default function Home() {
  const [transcript, setTranscript] = useState('');
  const [answer, setAnswer] = useState('');
  const [latency, setLatency] = useState(0);

  const handleVoiceResult = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
      const response = await fetch('/api/voice-query', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setTranscript(data.transcript || '');
      setAnswer(data.answer || '');
      setLatency(data.latency_ms || 0);
    } catch (err) {
      console.error('Error:', err);
      setAnswer('Error processing your request.');
    }
  };

  return (
    <main className={inter.className}>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-center mb-4">Voice-Enabled RAG System</h1>
          <p className="text-gray-300 text-center max-w-2xl mx-auto">
            Ask questions with your voice and get answers powered by retrieval-augmented generation.
          </p>
        </header>
        
        <div className="max-w-4xl mx-auto space-y-6">
          <VoiceRecorder onVoiceResult={handleVoiceResult} />
          <AnswerCard transcript={transcript} answer={answer} />
          <div className="flex justify-center">
            <LatencyBadge latency={latency} />
          </div>
        </div>
      </main>
    </main>
  );
}