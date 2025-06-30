import { ScrollArea } from "@/components/ui/scroll-area";
import Navbar from "@/components/landing/navbar";
import { useLocation } from "wouter";

export default function PrivacyPolicy() {
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
          <h1>Privacy Policy</h1>
          <p className="text-sm text-muted-foreground">Effective Date: 13 February 2025</p>

          <h2>1. Introduction</h2>
          <p>At Dassyor, we value your privacy. This policy explains how we collect, use, and safeguard the personal information you provide when you join our waitlist and use our services.</p>

          <h2>2. Information We Collect</h2>
          <ul>
            <li>Personal Data: When you join our waitlist, we collect information such as your name and email address.</li>
            <li>Usage Data: We may collect non-personal information such as browser type and device information to improve our services.</li>
          </ul>

          <h2>3. How We Use Your Information</h2>
          <ul>
            <li>To provide updates and communications related to our platform.</li>
            <li>To analyze and improve our services and user experience.</li>
            <li>To comply with legal obligations and enforce our policies.</li>
          </ul>

          <h2>4. Data Sharing and Disclosure</h2>
          <p>We do not sell or share your personal information with third parties except when required by law or to protect our rights. Any data shared with partners is handled in compliance with this policy.</p>

          <h2>5. Data Security</h2>
          <p>We implement reasonable security measures to protect your information. However, no data transmission over the internet is completely secure, so we cannot guarantee absolute security.</p>

          <h2>6. Your Rights</h2>
          <p>You have the right to access, update, or delete your personal information. If you wish to exercise any of these rights, please contact us at aziz@dassyor.com.</p>

          <h2>7. Changes to This Privacy Policy</h2>
          <p>We may update this Privacy Policy from time to time. The most current version will be posted on dassyor.com. Your continued use of our services after changes are posted constitutes your acceptance of the new terms.</p>

          <h2>8. Contact Information</h2>
          <p>For questions or concerns about this Privacy Policy, please contact us at aziz@dassyor.com.</p>
        </div>
      </main>
    </ScrollArea>
  );
}