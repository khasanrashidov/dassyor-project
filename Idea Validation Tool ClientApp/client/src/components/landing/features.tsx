import { motion, useInView } from "framer-motion";
import { Bot, Rocket, Brain, Clock, Shield, Users } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useRef } from "react";

const features = [
  {
    icon: Bot,
    title: "AI Co-Founder",
    description: "Get strategic guidance and feedback from your AI-powered virtual co-founder",
    progress: 95
  },
  {
    icon: Rocket,
    title: "Quick MVP Launch",
    description: "Transform your idea into a working MVP in record time",
    progress: 90
  },
  {
    icon: Brain,
    title: "Smart Insights",
    description: "Data-driven recommendations to optimize your startup journey",
    progress: 85
  },
  {
    icon: Clock,
    title: "Time Efficiency",
    description: "Save months of planning with AI-accelerated development",
    progress: 88
  },
  {
    icon: Shield,
    title: "Risk Mitigation",
    description: "Identify and address potential pitfalls before they become problems",
    progress: 92
  },
  {
    icon: Users,
    title: "Founder Community",
    description: "Connect with other founders and share experiences",
    progress: 87
  }
];

function ProgressBar({ progress, isInView }: { progress: number; isInView: boolean }) {
  return (
    <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
      <motion.div
        className="h-full bg-primary"
        initial={{ width: 0 }}
        animate={{ width: isInView ? `${progress}%` : 0 }}
        transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
      />
    </div>
  );
}

export default function Features() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <section id="features" className="container mx-auto px-4 py-12 md:py-16 lg:py-24 scroll-mt-16" ref={ref}>
      <div className="text-center mb-8 md:mb-12">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold mb-3 md:mb-4">
          Supercharge Your Startup Journey
        </h2>
        <p className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto px-4">
          Our AI-powered platform provides everything you need to turn your startup idea into reality
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            viewport={{ once: true }}
          >
            <Card className="h-full card-hover-effect group">
              <CardHeader>
                <feature.icon className="h-6 w-6 md:h-8 md:w-8 text-primary mb-2 transition-transform duration-300 group-hover:scale-110" />
                <CardTitle className="text-lg md:text-xl transition-colors duration-300 group-hover:text-primary">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm md:text-base text-muted-foreground mb-4">
                  {feature.description}
                </p>
                <ProgressBar progress={feature.progress} isInView={isInView} />
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
}