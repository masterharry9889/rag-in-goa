"use client";

import { useState, useEffect } from 'react';
import VoiceRecorder from '@/components/VoiceRecorder';
import AnswerCard from '@/components/AnswerCard';
import LatencyBadge from '@/components/LatencyBadge';
import { motion } from 'framer-motion';

export default function VoicePage() {
  const [transcript, setTranscript] = useState('');
  const [answer, setAnswer] = useState('');
  const [latency, setLatency] = useState(0);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const handleVoiceResult = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
      setTranscript('Processing audio...');
      setAnswer('');
      setLatency(0);
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
      setAnswer('Error processing your request. Make sure your API keys are configured correctly.');
      setTranscript('');
    }
  };

  return (
    <main className="min-h-screen bg-[#0f1115] text-gray-100 flex flex-col pt-32 pb-32 relative overflow-hidden selection:bg-brand-main/30">
      {/* Dynamic background responding to mouse */}
      <motion.div 
        className="absolute top-0 left-0 w-[600px] h-[600px] rounded-full blur-[150px] -z-10 pointer-events-none bg-brand-light/10"
        animate={{
          x: mousePos.x - 300,
          y: mousePos.y - 300,
        }}
        transition={{ type: "tween", ease: "backOut", duration: 1 }}
      />
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-brand-dark/20 rounded-full blur-[150px] -z-10 pointer-events-none"></div>

      <div className="max-w-3xl mx-auto w-full px-6 relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-12 text-center"
        >
          <div className="inline-block px-5 py-2 mb-6 rounded-full border border-brand-main/30 bg-brand-dark/20 backdrop-blur-md text-brand-accent text-xs font-bold tracking-widest uppercase shadow-[0_0_20px_rgba(73,154,19,0.15)]">
            Live Demo
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 drop-shadow-sm">
            Voice.<span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand-main drop-shadow-[0_0_15px_rgba(187,220,18,0.2)]">AI</span>
          </h1>
          <p className="text-gray-400 text-lg font-light max-w-xl mx-auto">Ask your question aloud, and our RAG pipeline will instantly generate an answer.</p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="bg-[#181b21]/80 backdrop-blur-xl border border-[#272b36] rounded-3xl p-8 md:p-12 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-brand-main/10 to-transparent opacity-50 rounded-bl-full -z-10"></div>
          
          <div className="flex flex-col space-y-10">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-3 text-white">Try it out</h2>
              <p className="text-gray-400 text-sm font-light">Click the microphone below and speak clearly.</p>
            </div>
            
            <div className="max-w-md mx-auto w-full relative">
              <VoiceRecorder onVoiceResult={handleVoiceResult} />
            </div>

            <div className="w-full">
              <AnswerCard transcript={transcript} answer={answer} />
            </div>

            {latency > 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center pt-6 border-t border-[#272b36]"
              >
                <LatencyBadge latency={latency} />
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </main>
  );
}
