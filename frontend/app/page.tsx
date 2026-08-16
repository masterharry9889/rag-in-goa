"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import CreepyButton from '@/components/CreepyButton';
import GooeyTextReveal from '@/components/GooeyTextReveal';

export default function Home() {
  const [hasEntered, setHasEntered] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    setIsMounted(true);
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    
    if (hasEntered) {
      window.addEventListener("mousemove", handleMouseMove);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [hasEntered]);

  const handleEnter = () => {
    setHasEntered(true);
  };

  if (!isMounted) return null;

  return (
    <>
      <AnimatePresence>
        {!hasEntered && (
          <motion.div 
            key="splash"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, filter: "blur(20px)" }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
            className="fixed inset-0 z-[100] bg-gray-950 flex flex-col items-center justify-center overflow-hidden"
          >
            {/* Eerie ambient background */}
            <motion.div 
              animate={{ 
                scale: [1, 1.2, 1],
                opacity: [0.2, 0.4, 0.2],
              }}
              transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80vw] h-[80vw] max-w-[800px] max-h-[800px] bg-brand-dark rounded-full blur-[120px] pointer-events-none"
            />
            
            <CreepyButton onClick={handleEnter} />
            
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2, duration: 2 }}
              className="mt-12 text-brand-light/50 tracking-[0.3em] text-sm uppercase font-semibold"
            >
              Do you dare to proceed?
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>

      {hasEntered && (
        <main className="min-h-screen bg-[#0f1115] text-gray-100 flex flex-col pb-32 overflow-hidden relative selection:bg-brand-main/30">
          
          {/* Dynamic background responding to mouse */}
          <motion.div 
            className="absolute top-0 left-0 w-[600px] h-[600px] rounded-full blur-[150px] -z-10 pointer-events-none bg-brand-main/10"
            animate={{
              x: mousePos.x - 300,
              y: mousePos.y - 300,
            }}
            transition={{ type: "tween", ease: "backOut", duration: 1 }}
          />
          <div className="absolute top-1/4 right-1/4 w-[800px] h-[800px] bg-brand-dark/10 rounded-full blur-[150px] -z-10 pointer-events-none"></div>

          {/* Hero Section */}
          <section className="pt-32 pb-24 px-6 relative flex-1 flex flex-col justify-center items-center">
            <div className="max-w-4xl mx-auto text-center z-10">
              
              <GooeyTextReveal delay={0.2} duration={2}>
                <div className="inline-block px-5 py-2 mb-8 rounded-full border border-brand-main/30 bg-brand-dark/20 backdrop-blur-md text-brand-accent text-sm font-semibold tracking-widest uppercase shadow-[0_0_20px_rgba(73,154,19,0.15)]">
                  Next Generation AI
                </div>
              </GooeyTextReveal>

              <GooeyTextReveal delay={0.4} duration={2}>
                <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-100 to-gray-400 drop-shadow-sm">
                  Voice-Enabled <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-light to-brand-main drop-shadow-[0_0_25px_rgba(187,220,18,0.25)]">RAG</span>
                </h1>
              </GooeyTextReveal>

              <GooeyTextReveal delay={0.6} duration={1.8}>
                <p className="text-xl md:text-2xl text-gray-400 mb-12 leading-relaxed max-w-2xl mx-auto font-light">
                  Experience lightning-fast retrieval-augmented generation. 
                  Just speak your question, and our AI pipeline handles speech-to-text, context retrieval, and generation in <strong className="text-brand-accent font-medium">milliseconds</strong>.
                </p>
              </GooeyTextReveal>

              <GooeyTextReveal delay={0.8} duration={1.5}>
                <Link href="/voice">
                  <button className="px-10 py-5 rounded-full bg-brand-main text-white font-bold text-lg hover:bg-brand-light transition-all duration-300 shadow-[0_0_30px_rgba(73,154,19,0.3)] hover:shadow-[0_0_50px_rgba(142,202,60,0.5)] hover:-translate-y-1 ring-1 ring-white/10">
                    Try it now
                  </button>
                </Link>
              </GooeyTextReveal>

            </div>
          </section>

          {/* Features */}
          <section className="py-24 px-6 relative z-10">
            <div className="max-w-7xl mx-auto">
              <GooeyTextReveal delay={1} duration={1.5}>
                <h2 className="text-3xl md:text-4xl font-bold text-center mb-20 text-white tracking-tight">Pipeline Architecture</h2>
              </GooeyTextReveal>
              
              <div className="grid md:grid-cols-3 gap-8">
                {[
                  {
                    title: "Speech to Text",
                    desc: "Powered by Sarvam or ElevenLabs, instantly converting spoken queries into text with extreme accuracy and low latency.",
                    icon: (
                      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    ),
                    color: "text-brand-light",
                    bg: "bg-brand-light/10",
                    delay: 1.2
                  },
                  {
                    title: "Vector Search",
                    desc: "Lightning-fast semantic retrieval using ChromaDB, quickly surfacing the most relevant context for your query.",
                    icon: (
                      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                      </svg>
                    ),
                    color: "text-brand-accent",
                    bg: "bg-brand-accent/10",
                    delay: 1.4
                  },
                  {
                    title: "LLM Generation",
                    desc: "Intelligent synthesis using state-of-the-art models to produce an accurate, contextualized final answer.",
                    icon: (
                      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    ),
                    color: "text-brand-main",
                    bg: "bg-brand-main/10",
                    delay: 1.6
                  }
                ].map((feature, idx) => (
                  <GooeyTextReveal key={idx} delay={feature.delay} duration={1.5}>
                    <div className="group p-10 rounded-3xl bg-[#181b21]/80 backdrop-blur-xl border border-[#272b36] shadow-xl hover:bg-[#1f232b] transition-all duration-500 h-full flex flex-col relative overflow-hidden">
                      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-brand-dark/20 to-transparent opacity-0 rounded-bl-full -z-10 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700"></div>
                      <div className={`w-16 h-16 rounded-2xl ${feature.bg} flex items-center justify-center ${feature.color} mb-8 shadow-inner ring-1 ring-white/5`}>
                        {feature.icon}
                      </div>
                      <h3 className="text-2xl font-bold mb-4 text-white group-hover:text-brand-light transition-colors duration-300">{feature.title}</h3>
                      <p className="text-gray-400 leading-relaxed font-light">{feature.desc}</p>
                    </div>
                  </GooeyTextReveal>
                ))}
              </div>
            </div>
          </section>
        </main>
      )}
    </>
  );
}