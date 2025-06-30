import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const testimonials = [
  {
    quote: "dassyor helped me validate and launch my startup in just weeks instead of months.",
    author: "Sarah Chen",
    role: "Founder, TechStart",
    avatar: "SC"
  },
  {
    quote: "The AI guidance was like having an experienced co-founder by my side 24/7.",
    author: "Mike Johnson",
    role: "CEO, DataFlow",
    avatar: "MJ"
  },
  {
    quote: "Revolutionary platform for first-time founders. Saved me from so many potential mistakes.",
    author: "Alex Kim",
    role: "Founder, AI Labs",
    avatar: "AK"
  }
];

export default function Testimonials() {
  return (
    <section id="testimonials" className="container mx-auto px-4 py-16 md:py-24 scroll-mt-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Trusted by Founders
        </h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          See what other entrepreneurs are saying about dassyor
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {testimonials.map((testimonial, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            viewport={{ once: true }}
          >
            <Card className="h-full">
              <CardContent className="p-6">
                <blockquote className="text-lg mb-6">
                  "{testimonial.quote}"
                </blockquote>
                <div className="flex items-center">
                  <Avatar className="h-12 w-12 mr-4">
                    <AvatarFallback>{testimonial.avatar}</AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="font-semibold">{testimonial.author}</div>
                    <div className="text-sm text-muted-foreground">
                      {testimonial.role}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
}