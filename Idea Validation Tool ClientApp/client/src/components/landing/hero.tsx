import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Lightbulb } from 'lucide-react';

// Example startup ideas for the preview
const startupIdeas = [
  {
    name: "E-commerce Platform for Local Artisans",
    marketPotential: "85%",
    competition: "Medium",
    stage: "Validation"
  },
  {
    name: "AI-Powered Personal Finance Assistant",
    marketPotential: "92%",
    competition: "High",
    stage: "Development"
  },
  {
    name: "Sustainable Food Delivery Service",
    marketPotential: "78%",
    competition: "Low",
    stage: "Planning"
  }
];

const AIRecommendations = {
  "Validation": [
    "Conduct market research with local artisans",
    "Analyze competitor pricing models",
    "Test MVP with small user group"
  ],
  "Development": [
    "Focus on UI/UX simplicity",
    "Implement robust security features",
    "Plan marketing strategy"
  ],
  "Planning": [
    "Map delivery zones",
    "Partner with local restaurants",
    "Calculate unit economics"
  ]
};

export default function Hero() {
  const [_, setLocation] = useLocation();
  const [currentIdeaIndex, setCurrentIdeaIndex] = useState(0);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const currentIdea = startupIdeas[currentIdeaIndex];
  const recommendations = AIRecommendations[currentIdea.stage as keyof typeof AIRecommendations];

  // Auto-cycle through ideas
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIdeaIndex((prev) => (prev + 1) % startupIdeas.length);
      setShowAnalysis(false);
      setAnalysisProgress(0);
    }, 8000); // Change idea every 8 seconds

    return () => clearInterval(timer);
  }, []);

  // Trigger analysis animation when idea changes
  useEffect(() => {
    if (!showAnalysis) {
      const timer = setTimeout(() => {
        setShowAnalysis(true);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [currentIdeaIndex, showAnalysis]);

  // Progress bar animation
  useEffect(() => {
    if (showAnalysis) {
      const timer = setInterval(() => {
        setAnalysisProgress((prev) => {
          if (prev >= 100) {
            clearInterval(timer);
            return 100;
          }
          return prev + 2;
        });
      }, 50);

      return () => clearInterval(timer);
    }
  }, [showAnalysis]);

  const scrollToNewsletter = () => {
    const newsletterSection = document.getElementById('newsletter');
    if (newsletterSection) {
      newsletterSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="container mx-auto px-4 pt-20 pb-16 md:pt-32 md:pb-20">
      <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
        {/* Hero Text */}
        <motion.div 
          className="flex-1 text-center lg:text-left"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-block px-3 py-1 mb-4 text-sm font-medium rounded-full bg-blue-50 text-blue-600">
            Coming Soon
          </span>
          <h1 className="text-3xl md:text-4xl lg:text-6xl font-bold leading-tight text-gray-900">
            Your AI Co-Founder for 
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> Startup Success</span>
          </h1>
          <p className="mt-6 text-base md:text-lg text-gray-600">
            Launch your startup faster and smarter with dassyor's AI guidance. Get early access to our AI-powered platform and minimize first-time founder mistakes.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
            <Button 
              size="lg" 
              className="text-base md:text-lg bg-blue-600 hover:bg-blue-700 text-white px-6 md:px-8"
              onClick={scrollToNewsletter}
            >
              Join Waitlist
            </Button>
            <Button 
              size="lg"
              variant="outline"
              className="text-base md:text-lg bg-white hover:bg-gray-50/80 text-gray-700 border border-gray-200 hover:border-gray-300 transition-colors duration-200 flex items-center gap-3 px-8 py-3 relative group shadow-sm"
              onClick={() => setLocation("/validate")}
            >
              <div className="text-blue-600 transition-all duration-300 group-hover:scale-110 relative">
                <motion.div
                  initial={{ rotate: 0 }}
                  animate={{ rotate: [0, -10, 10, -5, 5, 0] }}
                  transition={{
                    duration: 0.6,
                    ease: "easeInOut",
                    times: [0, 0.2, 0.4, 0.6, 0.8, 1],
                    repeat: Infinity,
                    repeatType: "reverse"
                  }}
                  className="group-hover:animate-bounce"
                >
                  <Lightbulb className="w-5 h-5" />
                </motion.div>
                <div className="absolute inset-0 bg-blue-400/20 blur-lg rounded-full scale-0 group-hover:scale-150 transition-transform duration-300" />
              </div>
              Validate Your Idea
            </Button>
          </div>
        </motion.div>

        {/* Startup Idea Preview */}
        <motion.div 
          className="flex-1 w-full lg:w-auto"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg blur-3xl opacity-50" />
            <AnimatePresence mode="wait">
              <motion.div
                key={currentIdeaIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="relative bg-white p-4 md:p-8 rounded-lg border shadow-lg"
              >
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 bg-blue-500 rounded-full animate-pulse" />
                    <p className="text-sm font-medium text-gray-600">
                      AI Analysis {showAnalysis ? "in Progress..." : "Starting..."}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-900 line-clamp-2">
                      Startup Idea: {currentIdea.name}
                    </p>
                    <div className="h-2 w-full bg-gray-100 rounded">
                      <motion.div 
                        className="h-full bg-blue-500 rounded"
                        initial={{ width: "0%" }}
                        animate={{ width: `${analysisProgress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>

                    <motion.div 
                      className="grid grid-cols-2 gap-2 md:gap-4 mt-4"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: showAnalysis ? 1 : 0 }}
                      transition={{ duration: 0.5, delay: 0.2 }}
                    >
                      <div className="bg-blue-50 p-2 md:p-3 rounded">
                        <p className="text-xs font-medium text-gray-600">Market Potential</p>
                        <p className="text-base md:text-lg font-semibold text-blue-600">
                          {currentIdea.marketPotential}
                        </p>
                      </div>
                      <div className="bg-blue-50 p-2 md:p-3 rounded">
                        <p className="text-xs font-medium text-gray-600">Competition</p>
                        <p className="text-base md:text-lg font-semibold text-blue-600">
                          {currentIdea.competition}
                        </p>
                      </div>
                    </motion.div>
                  </div>

                  <motion.div 
                    className="pt-4 border-t"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: showAnalysis ? 1 : 0 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                  >
                    <p className="text-xs text-gray-500 mb-2">AI Recommendations:</p>
                    {recommendations.map((rec, index) => (
                      <motion.div
                        key={index}
                        className="h-2 bg-gray-100 rounded mt-2"
                        style={{ width: ["100%", "80%", "60%"][index] }}
                        initial={{ opacity: 0.3 }}
                        animate={{ opacity: 1 }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          repeatType: "reverse",
                          delay: index * 0.2
                        }}
                      />
                    ))}
                  </motion.div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </section>
  );
}