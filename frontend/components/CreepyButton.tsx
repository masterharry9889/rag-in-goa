"use client";

import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";

export default function CreepyButton({ onClick }: { onClick: () => void }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="relative group inline-block">
      {/* Eyes container - positioned absolutely behind the button, bottom right */}
      <div className="absolute right-4 -bottom-4 flex gap-2 z-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-75">
        <Eye mousePos={mousePos} />
        <Eye mousePos={mousePos} />
      </div>

      {/* Button */}
      <button 
        onClick={onClick}
        className="relative z-10 flex items-center justify-center bg-brand-dark border border-brand-main/50 hover:bg-brand-main rounded-2xl px-12 py-5 shadow-[0_0_40px_rgba(39,111,39,0.4)] hover:shadow-[0_0_60px_rgba(73,154,19,0.6)] transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] group-hover:-translate-y-3 group-hover:-rotate-2 cursor-pointer overflow-hidden backdrop-blur-sm"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-brand-light/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out"></div>
        <span className="text-2xl font-extrabold text-brand-accent group-hover:text-white tracking-[0.2em] uppercase drop-shadow-md transition-colors duration-300">
          Wake Up AI
        </span>
      </button>
    </div>
  );
}

function Eye({ mousePos }: { mousePos: { x: number; y: number } }) {
  const eyeRef = useRef<HTMLDivElement>(null);
  const [pupilPos, setPupilPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!eyeRef.current) return;
    const rect = eyeRef.current.getBoundingClientRect();
    const eyeCenterX = rect.left + rect.width / 2;
    const eyeCenterY = rect.top + rect.height / 2;
    
    const angle = Math.atan2(mousePos.y - eyeCenterY, mousePos.x - eyeCenterX);
    // Constrain pupil inside the eye
    const distance = Math.min(
      Math.hypot(mousePos.x - eyeCenterX, mousePos.y - eyeCenterY) / 10,
      6 // Max radius travel distance for smaller eyes
    );

    setPupilPos({
      x: Math.cos(angle) * distance,
      y: Math.sin(angle) * distance
    });
  }, [mousePos]);

  return (
    <div 
      ref={eyeRef}
      className="w-7 h-7 bg-white rounded-full flex items-center justify-center shadow-inner overflow-hidden relative border-2 border-gray-900"
    >
      <motion.div 
        className="w-3 h-3 bg-gray-950 rounded-full"
        animate={{ x: pupilPos.x, y: pupilPos.y }}
        transition={{ type: "tween", ease: "linear", duration: 0.05 }}
      />
    </div>
  );
}
