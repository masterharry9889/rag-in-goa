"use client";

import { useState, useEffect } from 'react';
import { Trash2, ChevronDown, CheckCircle2, Edit2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const PROVIDERS = ['OPENAI', 'ANTHROPIC', 'GROQ'];

export default function LLMProviderPage() {
  const [config, setConfig] = useState<Record<string, string>>({});
  const [selectedProvider, setSelectedProvider] = useState(PROVIDERS[0]);
  const [formState, setFormState] = useState({ key: '', model: '' });
  
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
        const loadedConfig = data || {};
        setConfig(loadedConfig);
        setFormState({
          key: loadedConfig[`${selectedProvider}_API_KEY`] || '',
          model: loadedConfig[`${selectedProvider}_MODEL`] || ''
        });
      }
    } catch (error) {
      console.error('Failed to fetch config', error);
    }
  };

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProvider = e.target.value;
    setSelectedProvider(newProvider);
    setFormState({
      key: config[`${newProvider}_API_KEY`] || '',
      model: config[`${newProvider}_MODEL`] || ''
    });
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage('');
    
    const payload = {
      keys: {
        [`${selectedProvider}_API_KEY`]: formState.key,
        [`${selectedProvider}_MODEL`]: formState.model
      }
    };

    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setMessage(`${selectedProvider} settings saved successfully!`);
        
        const newConfig = {
          ...config,
          [`${selectedProvider}_API_KEY`]: formState.key,
          [`${selectedProvider}_MODEL`]: formState.model
        };
        setConfig(newConfig);
        
        // Reset the form
        setFormState({ key: '', model: '' });
        
        // Switch to the next unconfigured provider if available
        const nextProvider = PROVIDERS.find(p => !newConfig[`${p}_API_KEY`]);
        if (nextProvider) {
          setSelectedProvider(nextProvider);
        }

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

  const handleDelete = async (provider: string) => {
    setLoading(true);
    try {
      await fetch(`/api/config/${provider}_API_KEY`, { method: 'DELETE' });
      await fetch(`/api/config/${provider}_MODEL`, { method: 'DELETE' });
      
      setConfig(prev => {
        const next = { ...prev };
        delete next[`${provider}_API_KEY`];
        delete next[`${provider}_MODEL`];
        return next;
      });
      
      if (selectedProvider === provider) {
        setFormState({ key: '', model: '' });
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (provider: string) => {
    setSelectedProvider(provider);
    setFormState({
      key: config[`${provider}_API_KEY`] || '',
      model: config[`${provider}_MODEL`] || ''
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const configuredProviders = PROVIDERS.filter(p => !!config[`${p}_API_KEY`]);

  return (
    <main className="min-h-screen bg-[#0f1115] text-gray-100 flex flex-col pt-32 pb-32 relative overflow-hidden selection:bg-brand-main/30">
      {/* Dynamic background responding to mouse */}
      <motion.div 
        className="absolute top-0 left-0 w-[600px] h-[600px] rounded-full blur-[150px] -z-10 pointer-events-none bg-brand-dark/20"
        animate={{ x: mousePos.x - 300, y: mousePos.y - 300 }}
        transition={{ type: "tween", ease: "backOut", duration: 1 }}
      />
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-brand-main/10 rounded-full blur-[150px] -z-10 pointer-events-none"></div>

      <section className="flex-1 px-6 relative z-10">
        <div className="max-w-5xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-16 text-center"
          >
            <h1 className="text-4xl md:text-6xl font-extrabold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 drop-shadow-sm">
              LLM <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand-main drop-shadow-[0_0_15px_rgba(187,220,18,0.2)]">Providers</span>
            </h1>
            <p className="text-gray-400 text-lg font-light">Configure your API keys and models for Large Language Models securely.</p>
          </motion.div>

          <div className="grid lg:grid-cols-12 gap-12 items-start">
            
            {/* Form Section */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="lg:col-span-5 bg-[#181b21]/80 backdrop-blur-xl border border-[#272b36] rounded-3xl p-8 shadow-2xl relative overflow-hidden h-fit sticky top-8"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-brand-dark/30 to-transparent opacity-50 rounded-bl-full -z-10"></div>
              
              <h2 className="text-2xl font-bold mb-8 text-white">
                {configuredProviders.includes(selectedProvider) ? 'Edit Provider' : 'Add Provider'}
              </h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-3 tracking-wide uppercase">Select Provider</label>
                  <div className="relative">
                    <select
                      value={selectedProvider}
                      onChange={handleProviderChange}
                      className="w-full appearance-none bg-[#0f1115] border border-[#272b36] rounded-xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-main focus:border-transparent transition-all shadow-inner cursor-pointer"
                    >
                      {PROVIDERS.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-gray-400">
                      <ChevronDown size={20} />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-3 tracking-wide uppercase">API Key</label>
                  <input
                    type="password"
                    value={formState.key}
                    onChange={(e) => setFormState({ ...formState, key: e.target.value })}
                    className="w-full bg-[#0f1115] border border-[#272b36] rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-main focus:border-transparent transition-all shadow-inner"
                    placeholder="Enter API Key"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-3 tracking-wide uppercase">Model Name</label>
                  <input
                    type="text"
                    value={formState.model}
                    onChange={(e) => setFormState({ ...formState, model: e.target.value })}
                    className="w-full bg-[#0f1115] border border-[#272b36] rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-main focus:border-transparent transition-all shadow-inner"
                    placeholder="e.g. gpt-4o, claude-3-5-sonnet"
                  />
                </div>

                {message && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-4 rounded-xl text-sm font-medium backdrop-blur-md ${message.includes('success') ? 'bg-brand-dark/20 text-brand-accent border border-brand-main/30' : 'bg-red-500/20 text-red-300 border border-red-500/30'}`}
                  >
                    {message}
                  </motion.div>
                )}

                <button
                  onClick={handleSave}
                  disabled={loading || !formState.key}
                  className="w-full mt-4 py-4 bg-brand-main hover:bg-brand-light text-white font-bold rounded-xl transition-all duration-300 disabled:opacity-50 shadow-[0_0_20px_rgba(73,154,19,0.3)] hover:shadow-[0_0_30px_rgba(142,202,60,0.5)] active:scale-95"
                >
                  {loading ? 'Saving...' : 'Save Configuration'}
                </button>
              </div>
            </motion.div>

            {/* Saved Providers Staggered Grid */}
            <div className="lg:col-span-7">
              <h2 className="text-2xl font-bold mb-8 text-gray-400 pl-4 border-l-4 border-brand-main">Configured Providers</h2>
              
              {configuredProviders.length === 0 ? (
                <div className="p-8 rounded-3xl border border-dashed border-[#272b36] text-center text-gray-500 font-light">
                  No providers configured yet.
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 gap-6 items-start">
                  <AnimatePresence>
                    {configuredProviders.map((provider, idx) => (
                      <motion.div
                        key={provider}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ duration: 0.4 }}
                        className={`bg-[#181b21] border border-[#272b36] rounded-3xl p-6 relative group overflow-hidden ${idx % 2 !== 0 ? 'sm:mt-12' : ''}`}
                      >
                        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-brand-main to-brand-accent"></div>
                        
                        <div className="flex justify-between items-start mb-6">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-brand-main/20 flex items-center justify-center text-brand-light border border-brand-main/30">
                              <CheckCircle2 size={20} />
                            </div>
                            <h3 className="font-bold text-lg text-white tracking-wide">{provider}</h3>
                          </div>
                          
                          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEdit(provider)}
                              className="p-2.5 bg-brand-main/10 text-brand-light hover:bg-brand-main/20 rounded-xl border border-transparent hover:border-brand-main/20 transition-all active:scale-95"
                              title="Edit Provider"
                            >
                              <Edit2 size={16} />
                            </button>
                            <button
                              onClick={() => handleDelete(provider)}
                              className="p-2.5 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:text-red-300 rounded-xl border border-transparent hover:border-red-500/20 transition-all active:scale-95"
                              title="Remove Provider"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </div>
                        
                        <div className="space-y-4">
                          <div>
                            <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-1">Model Name</p>
                            <p className="text-gray-300 font-medium bg-[#0f1115] px-3 py-2 rounded-lg border border-[#272b36] inline-block">
                              {config[`${provider}_MODEL`] || 'Default'}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-1">API Key</p>
                            <p className="text-gray-400 font-mono bg-[#0f1115] px-3 py-2 rounded-lg border border-[#272b36] truncate">
                              ••••••••••••••••
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>

          </div>
        </div>
      </section>
    </main>
  );
}
