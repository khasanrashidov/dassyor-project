import { ScrollArea } from "@/components/ui/scroll-area";
import Navbar from "@/components/landing/navbar";
import IdeaValidationForm from "@/components/landing/idea-validation-form";
import { motion } from "framer-motion";

export default function Validate() {
  return (
    <ScrollArea className="h-screen w-full">
      <Navbar />
      <main className="container mx-auto px-4 pt-24 pb-12 md:pt-32">
        <div className="max-w-3xl mx-auto">
          {/* Background Animation - Extended vertically */}
          <motion.div
            className="absolute left-0 right-0 -z-10"
            style={{
              top: 'calc(64px)', // Height of the navbar
              bottom: '200px', // Space above "How it works"
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5 }}
          >
            {/* Main flowing gradient */}
            <motion.div
              className="absolute w-full h-full"
              style={{
                background: 'radial-gradient(circle, rgba(59,130,246,0.015) 0%, transparent 50%, rgba(59,130,246,0.01) 100%)',
                filter: 'blur(50px)',
                willChange: 'transform',
              }}
              animate={{
                scale: [1, 1.01, 1],
                x: [-1, 1, -1],
                y: [-1, 1, -1],
              }}
              transition={{
                duration: 20, // Significantly slower
                repeat: Infinity,
                ease: [0.4, 0, 0.6, 1], // Smooth cubic-bezier curve
              }}
            />

            {/* Secondary flowing gradient */}
            <motion.div
              className="absolute w-full h-full"
              style={{
                background: 'radial-gradient(circle at 100% 100%, transparent 0%, rgba(59,130,246,0.01) 50%, transparent 100%)',
                filter: 'blur(60px)',
                willChange: 'transform',
              }}
              animate={{
                scale: [1.01, 1, 1.01],
                x: [1, -1, 1],
                y: [1, -1, 1],
              }}
              transition={{
                duration: 25, // Significantly slower
                repeat: Infinity,
                ease: [0.4, 0, 0.6, 1], // Smooth cubic-bezier curve
                delay: 0.5
              }}
            />

            {/* Third subtle layer for added depth */}
            <motion.div
              className="absolute w-full h-full"
              style={{
                background: 'radial-gradient(70% 70% at 50% 30%, rgba(59,130,246,0.008) 0%, transparent 100%)',
                filter: 'blur(70px)',
                willChange: 'transform',
              }}
              animate={{
                scale: [1, 1.02, 1],
                rotate: [-0.5, 0.5, -0.5], // Very subtle rotation
                x: [-2, 2, -2],
                y: [-2, 2, -2],
              }}
              transition={{
                duration: 30,
                repeat: Infinity,
                ease: [0.4, 0, 0.6, 1],
                delay: 1
              }}
            />
          </motion.div>

          <h1 className="text-4xl font-semibold mb-6 text-center">
            Idea validation tool
          </h1>
          <p className="text-xl text-gray-600 text-center mb-12">
            Dassyor AI scans millions of online discussions, forums, and web content to determine if there's demand for your business idea. This tool is free to use.
          </p>

          {/* Validation Form Section */}
          <div className="relative z-0 mb-24">
            <div className="relative bg-white/95 backdrop-blur-sm p-8 rounded-lg shadow-lg">
              <IdeaValidationForm />
            </div>
          </div>

          {/* How it works */}
          <section className="mb-24">
            <h2 className="text-2xl font-semibold mb-12 text-center">How it works</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-6 border-2 border-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-medium text-blue-600">1</span>
                </div>
                <h3 className="text-base font-medium mb-2">Describe Your Idea</h3>
                <p className="text-sm text-gray-600">Briefly explain your business idea.</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-6 border-2 border-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-medium text-blue-600">2</span>
                </div>
                <h3 className="text-base font-medium mb-2">Smart Search</h3>
                <p className="text-sm text-gray-600">Dassyor AI scans millions of online discussions, forums, and web content.</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-6 border-2 border-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-medium text-blue-600">3</span>
                </div>
                <h3 className="text-base font-medium mb-2">Get Analysis</h3>
                <p className="text-sm text-gray-600">See market demand, discussion trends, and key insights.</p>
              </div>
            </div>
          </section>

          {/* Footer */}
          <footer className="mt-24 pt-8 border-t text-sm text-gray-500">
            <div className="max-w-3xl mx-auto text-center">
              <p>© 2025 dassyor. All rights reserved.</p>
              <div className="mt-2 space-x-4">
                <a href="/terms" className="hover:text-gray-900">Terms of service</a>
                <a href="/privacy" className="hover:text-gray-900">Privacy policy</a>
              </div>
            </div>
          </footer>
        </div>
      </main>
    </ScrollArea>
  );
}