import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { insertNewsletterSchema } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { useConfetti } from "@/hooks/use-confetti";
import { apiRequest } from "@/lib/queryClient";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export default function Newsletter() {
  const { toast } = useToast();
  const { fire: fireConfetti } = useConfetti();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    telegramUsername: ""
  });

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: { name: string; email: string; telegramUsername?: string }) => {
      await apiRequest("POST", "/api/newsletter", data);
    },
    onSuccess: () => {
      toast({
        title: "You're on the list!",
        description: "We'll notify you as soon as dassyor is ready.",
      });
      fireConfetti();
      setFormData({ name: "", email: "", telegramUsername: "" });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to join waitlist. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name && formData.email) {
      mutate(formData);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <section id="newsletter" className="bg-white border-t">
      <div className="container mx-auto px-4 py-16 md:py-20">
        <motion.div 
          className="max-w-xl mx-auto text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <div className="inline-flex items-center gap-2 bg-primary/5 text-primary px-4 py-1.5 rounded-full mb-6">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-medium">Coming Soon</span>
          </div>

          <h2 className="text-2xl md:text-3xl font-semibold mb-3">
            Be the first to experience <span className="text-blue-600">dassyor</span>
          </h2>

          <p className="text-base md:text-lg text-muted-foreground mb-8">
            Join our waitlist to get early access and exclusive benefits when we launch
          </p>

          <form onSubmit={handleSubmit} className="space-y-3 max-w-sm mx-auto">
            <Input
              type="text"
              name="name"
              placeholder="Your name"
              value={formData.name}
              onChange={handleChange}
              required
              className="h-11"
            />
            <Input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
              className="h-11"
            />
            <Input
              type="text"
              name="telegramUsername"
              placeholder="Telegram username (optional)"
              value={formData.telegramUsername}
              onChange={handleChange}
              className="h-11"
            />
            <Button 
              type="submit"
              disabled={isPending}
              className="w-full h-11 px-6 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isPending ? "Joining..." : "Join Waitlist"}
            </Button>
          </form>

          <p className="text-xs text-muted-foreground mt-4">
            By joining, you agree to our{" "}
            <a 
              href="/terms"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-primary"
            >
              Terms of Service
            </a>{" "}
            and{" "}
            <a 
              href="/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-primary"
            >
              Privacy Policy
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  );
}