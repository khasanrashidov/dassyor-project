import { ScrollArea } from "@/components/ui/scroll-area";
import Navbar from "@/components/landing/navbar";
import { useLocation } from "wouter";

export default function TermsOfService() {
  const [_, setLocation] = useLocation();

  const handleNavigation = () => {
    setLocation('/');
    // Wait for navigation to complete before scrolling
    setTimeout(() => {
      const newsletterSection = document.getElementById('newsletter');
      if (newsletterSection) {
        newsletterSection.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  return (
    <ScrollArea className="h-screen w-full">
      <Navbar />
      <main className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto prose">
          <h1>Terms of Service</h1>
          <p className="text-sm text-muted-foreground">Effective Date: 13 February 2025</p>

          <h2>1. Acceptance of Terms</h2>
          <p>By joining the dassyor.com waitlist and using our services, you agree to be bound by these Terms of Service. If you do not agree, please do not use our site.</p>

          <h2>2. Description of Service</h2>
          <p>Dassyor is an AI-powered platform for startup success that provides users with guidance, tools, and services to help launch and grow their business. Specific features may vary as we continue to develop our platform.</p>

          <h2>3. User Obligations</h2>
          <ul>
            <li>You must provide accurate and up-to-date information when joining the waitlist.</li>
            <li>You agree not to misuse the platform or engage in any activities that may disrupt our services.</li>
          </ul>

          <h2>4. Intellectual Property</h2>
          <p>All content on dassyor.com—including text, graphics, logos, and images—is the property of Dassyor or its licensors. You may not reproduce, distribute, or modify any content without our prior written consent.</p>

          <h2>5. Disclaimers</h2>
          <p>Our services are provided "as is" and "as available." Dassyor makes no warranties regarding the reliability, accuracy, or suitability of our services. Use them at your own risk.</p>

          <h2>6. Limitation of Liability</h2>
          <p>In no event shall Dassyor be liable for any direct, indirect, incidental, or consequential damages arising from your use of the platform.</p>

          <h2>7. Modifications to Terms</h2>
          <p>We reserve the right to update these Terms at any time. Changes will be posted on our website, and continued use of our services constitutes your acceptance of the new terms.</p>

          <h2>8. Contact Information</h2>
          <p>For any questions or concerns regarding these Terms, please contact us at aziz@dassyor.com.</p>
        </div>
      </main>
    </ScrollArea>
  );
}