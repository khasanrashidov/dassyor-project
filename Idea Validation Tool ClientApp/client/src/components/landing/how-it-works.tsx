import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  {
    number: "01",
    title: "Submit Your Idea",
    description: "Share your startup concept with our AI platform",
    image: "/images/digital-nomad.png" // Digital nomad with laptop and tech elements
  },
  {
    number: "02",
    title: "Validate Your Idea",
    description: "Validate your idea with real-world data.",
    image: "/images/shared-goals.png" // Shared goals visualization with checkmarks
  },
  {
    number: "03",
    title: "Build & Launch",
    description: "Follow guided steps to build and launch your MVP",
    image: "/images/programming.png" // Developer working on computer screens
  }
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-muted py-16 md:py-24 scroll-mt-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8 md:mb-12">
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold mb-3 md:mb-4">
            How <span className="text-blue-600">dassyor</span> Works
          </h2>
          <p className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto px-4">
            A simple three-step process to turn your idea into reality
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="overflow-hidden h-full group card-hover-effect">
                <div className="relative overflow-hidden bg-white">
                  <motion.img
                    src={step.image}
                    alt={step.title}
                    className="w-full h-40 md:h-48 object-contain p-2 transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
                <CardContent className="p-4 md:p-6 relative">
                  <motion.span
                    className="text-4xl md:text-5xl font-bold text-primary/20 transition-all duration-300 group-hover:text-primary/30"
                    whileHover={{ scale: 1.1 }}
                  >
                    {step.number}
                  </motion.span>
                  <h3 className="text-lg md:text-xl font-semibold mt-2 mb-2 transition-colors duration-300 group-hover:text-primary">
                    {step.title}
                  </h3>
                  <p className="text-sm md:text-base text-muted-foreground">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}