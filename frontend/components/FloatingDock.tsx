"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Mic, Cpu, Radio } from "lucide-react";
import { useState } from "react";

const dockItems = [
  { id: "home", label: "Home", icon: Home, href: "/" },
  { id: "voice", label: "Voice.AI", icon: Mic, href: "/voice" },
  { id: "llm", label: "LLM Provider", icon: Cpu, href: "/llm-provider" },
  { id: "stt", label: "STT Provider", icon: Radio, href: "/stt-provider" },
];

export default function FloatingDock() {
  const pathname = usePathname();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
      <motion.div 
        className="flex items-center gap-2 px-3 py-2 bg-[#181b21]/80 backdrop-blur-xl border border-[#272b36] rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.5)] ring-1 ring-white/5"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
      >
        {dockItems.map((item, index) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          // Calculate distance from hovered item to create the magnification effect
          let scale = 1;
          if (hoveredIndex !== null) {
            const distance = Math.abs(hoveredIndex - index);
            if (distance === 0) scale = 1.3;
            else if (distance === 1) scale = 1.15;
            else if (distance === 2) scale = 1.05;
          }

          return (
            <Link key={item.id} href={item.href}>
              <motion.div
                className="relative group flex items-center justify-center p-3 rounded-xl transition-colors cursor-pointer"
                onHoverStart={() => setHoveredIndex(index)}
                onHoverEnd={() => setHoveredIndex(null)}
                animate={{ scale }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
                style={{
                  backgroundColor: isActive ? 'rgba(73, 154, 19, 0.2)' : 'transparent',
                }}
              >
                {/* Tooltip */}
                <motion.div 
                  className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-opacity bg-brand-dark text-brand-light text-xs font-bold tracking-wider uppercase px-3 py-1.5 rounded-lg border border-brand-main/50 whitespace-nowrap pointer-events-none shadow-[0_0_15px_rgba(73,154,19,0.3)]"
                  initial={{ y: 5 }}
                  whileHover={{ y: 0 }}
                >
                  {item.label}
                </motion.div>

                <Icon 
                  size={22} 
                  className={isActive ? "text-brand-accent drop-shadow-[0_0_8px_rgba(187,220,18,0.5)]" : "text-gray-400 group-hover:text-brand-light"} 
                />
                
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute -bottom-1.5 w-1.5 h-1.5 bg-brand-accent rounded-full shadow-[0_0_10px_rgba(187,220,18,0.8)]"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </motion.div>
    </div>
  );
}
