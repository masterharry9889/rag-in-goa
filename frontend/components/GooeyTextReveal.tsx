"use client";

import { motion } from "framer-motion";
import { ReactNode, useState } from "react";

export default function GooeyTextReveal({ 
  children, 
  delay = 0,
  duration = 1.5,
  className = ""
}: { 
  children: ReactNode,
  delay?: number,
  duration?: number,
  className?: string
}) {
  const [isComplete, setIsComplete] = useState(false);

  return (
    <div 
      className={`relative ${className}`} 
      style={{ filter: isComplete ? "none" : "url(#gooey-filter)" }}
    >
      <svg className="absolute w-0 h-0 pointer-events-none">
        <defs>
          <filter id="gooey-filter" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="
                1 0 0 0 0
                0 1 0 0 0
                0 0 1 0 0
                0 0 0 20 -8
              "
              result="gooey"
            />
            {/* Blend the original graphic with the gooey effect to ensure crisp edges at the end */}
            <feBlend in="SourceGraphic" in2="gooey" mode="normal" />
          </filter>
        </defs>
      </svg>

      <motion.div
        initial={{ opacity: 0, filter: "blur(16px)", scale: 0.95, y: 10 }}
        animate={{ opacity: 1, filter: "blur(0px)", scale: 1, y: 0 }}
        transition={{ duration, delay, ease: [0.16, 1, 0.3, 1] }} // Custom spring-like easing
        onAnimationComplete={() => setIsComplete(true)}
      >
        {children}
      </motion.div>
    </div>
  );
}
