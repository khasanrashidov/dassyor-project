import Navbar from "@/components/landing/navbar";
import Hero from "@/components/landing/hero";
import Features from "@/components/landing/features";
import HowItWorks from "@/components/landing/how-it-works";
import Newsletter from "@/components/landing/newsletter";
import Footer from "@/components/landing/contact";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function Home() {
  return (
    <ScrollArea className="h-screen w-full">
      <Navbar />
      <main className="flex flex-col items-center">
        <Hero />
        <Features />
        <HowItWorks />
        <Newsletter />
        <Footer />
      </main>
    </ScrollArea>
  );
}