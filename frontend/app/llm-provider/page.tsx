"use client";

import { useState, useEffect } from 'react';
import { Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LLMProviderPage() {
  const [keys, setKeys] = useState({
    OPENAI_API_KEY: '',
    ANTHROPIC_API_KEY: '',
    GROQ_API_KEY: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    fetchConfig();
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      if (res.ok) {
        const data = await res.json();
        setKeys({
          OPENAI_API_KEY: data.OPENAI_API_KEY || '',
          ANTHROPIC_API_KEY: data.ANTHROPIC_API_KEY || '',
          GROQ_API_KEY: data.GROQ_API_KEY || ''
        });
      }
    } catch (error) {
      console.error('Failed to fetch config', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keys })
      });
      if (res.ok) {
        setMessage('LLM Provider keys saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Failed to save settings.');
      }
    } catch (error) {
      setMessage('An error occurred while saving.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (keyToDelete: string) => {
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch(`/api/config/${keyToDelete}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setMessage(`${keyToDelete.replace(/_/g, ' ')} deleted successfully!`);
        setKeys(prev => ({ ...prev, [keyToDelete]: '' }));
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Failed to delete setting.');
      }
    } catch (error) {
      setMessage('An error occurred while deleting.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#0f1115] text-gray-100 flex flex-col pt-32 pb-32 relative overflow-hidden selection:bg-brand-main/30">
      {/* Dynamic background responding to mouse */}
      <motion.div 
        className="absolute top-0 left-0 w-[600px] h-[600px] rounded-full blur-[150px] -z-10 pointer-events-none bg-brand-dark/20"
        animate={{
          x: mousePos.x - 300,
          y: mousePos.y - 300,
        }}
        transition={{ type: "tween", ease: "backOut", duration: 1 }}
      />
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-brand-main/10 rounded-full blur-[150px] -z-10 pointer-events-none"></div>

      <section className="flex-1 px-6 relative z-10">
        <div className="max-w-3xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-12 text-center"
          >
            <h1 className="text-4xl md:text-6xl font-extrabold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 drop-shadow-sm">
              LLM <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand-main drop-shadow-[0_0_15px_rgba(187,220,18,0.2)]">Providers</span>
            </h1>
            <p className="text-gray-400 text-lg font-light">Configure your API keys for Large Language Models securely.</p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="bg-[#181b21]/80 backdrop-blur-xl border border-[#272b36] rounded-3xl p-8 md:p-12 shadow-2xl relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-brand-dark/30 to-transparent opacity-50 rounded-bl-full -z-10"></div>
            
            <div className="space-y-8">
              {Object.keys(keys).map((key, idx) => (
                <motion.div 
                  key={key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + idx * 0.1 }}
                >
                  <label className="block text-sm font-semibold text-gray-300 mb-3 tracking-wide uppercase">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <div className="flex gap-3">
                    <input
                      type="password"
                      value={keys[key as keyof typeof keys]}
                      onChange={(e) => setKeys({ ...keys, [key]: e.target.value })}
                      className="flex-1 bg-[#0f1115] border border-[#272b36] rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-main focus:border-transparent transition-all shadow-inner"
                      placeholder={`Enter ${key}`}
                    />
                    <button
                      onClick={() => handleDelete(key)}
                      disabled={loading || !keys[key as keyof typeof keys]}
                      className="p-4 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:text-red-300 rounded-xl border border-red-500/20 transition-all disabled:opacity-50 disabled:hover:bg-red-500/10 flex items-center justify-center hover:scale-105 active:scale-95"
                      title="Delete Key"
                    >
                      <Trash2 size={22} />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            {message && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`mt-8 p-5 rounded-xl text-sm font-medium backdrop-blur-md ${message.includes('success') ? 'bg-brand-dark/20 text-brand-accent border border-brand-main/30' : 'bg-red-500/20 text-red-300 border border-red-500/30'}`}
              >
                {message}
              </motion.div>
            )}

            <div className="mt-12 pt-8 border-t border-[#272b36] flex justify-end">
              <button
                onClick={handleSave}
                disabled={loading}
                className="px-8 py-4 bg-brand-main hover:bg-brand-light text-white font-bold rounded-xl transition-all duration-300 disabled:opacity-50 shadow-[0_0_20px_rgba(73,154,19,0.3)] hover:shadow-[0_0_30px_rgba(142,202,60,0.5)] hover:-translate-y-1"
              >
                {loading ? 'Saving Changes...' : 'Save Settings'}
              </button>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
}
