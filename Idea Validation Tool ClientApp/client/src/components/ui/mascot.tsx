import { motion } from "framer-motion";

export function Mascot({ className = "", size = 120 }: { className?: string; size?: number }) {
  return (
    <div className={className} style={{ width: size, height: size }}>
      <motion.svg
        viewBox="0 0 100 100"
        className="w-full h-full"
        initial="hidden"
        animate="visible"
      >
        {/* Rocket body */}
        <motion.path
          d="M50 20 L65 50 L50 80 L35 50 Z"
          fill="#4338ca"
          stroke="#312e81"
          strokeWidth="2"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ 
            scale: [0.8, 1, 0.8],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Rocket window */}
        <motion.circle
          cx="50"
          cy="45"
          r="8"
          fill="#ffffff"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        />
        
        {/* Rocket flames */}
        <motion.path
          d="M45 80 L50 95 L55 80"
          stroke="#ef4444"
          strokeWidth="3"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ 
            pathLength: 1,
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </motion.svg>
    </div>
  );
}

export function LoadingMascot() {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <Mascot />
      <p className="text-sm text-muted-foreground animate-pulse">
        Loading...
      </p>
    </div>
  );
}
