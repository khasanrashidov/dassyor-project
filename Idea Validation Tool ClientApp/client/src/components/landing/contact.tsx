import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { insertNewsletterSchema } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import { Link } from "wouter";
import { SiTelegram, SiInstagram, SiLinkedin, SiX } from "react-icons/si";

const NavLink = ({ href, children, onClick }: { href: string, children: React.ReactNode, onClick?: () => void }) => {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    if (onClick) onClick();
  };

  return (
    <a
      href={href}
      onClick={handleClick}
      className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
    >
      {children}
    </a>
  );
};

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="container mx-auto px-4 py-16">
        {/* Links Section */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-16">
          <div>
            <h4 className="text-sm font-semibold mb-3 text-gray-900">Navigation</h4>
            <ul className="space-y-2">
              <li>
                <NavLink href="#features">Features</NavLink>
              </li>
              <li>
                <NavLink href="#how-it-works">How It Works</NavLink>
              </li>
            </ul>
          </div>

          <div className="md:col-span-2">
            <h4 className="text-sm font-semibold mb-3 text-gray-900">Social</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-3">
              <a 
                href="https://t.me/dassyorcom" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors inline-flex items-center gap-2"
              >
                <SiTelegram className="h-4 w-4 flex-shrink-0" />
                <span>Telegram</span>
              </a>
              
              <a 
                href="https://www.linkedin.com/company/dassyorcom" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors inline-flex items-center gap-2"
              >
                <SiLinkedin className="h-4 w-4 flex-shrink-0" />
                <span>LinkedIn</span>
              </a>
              
              <a 
                href="https://www.instagram.com/dassyorcom/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors inline-flex items-center gap-2"
              >
                <SiInstagram className="h-4 w-4 flex-shrink-0" />
                <span>Instagram</span>
              </a>
              
              <a 
                href="https://x.com/dassyor" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors inline-flex items-center gap-2"
              >
                <SiX className="h-4 w-4 flex-shrink-0" />
                <span>X (Twitter)</span>
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="text-center">
          <Link href="/" className="inline-block mb-4">
            <span className="font-semibold text-xl">
              <span className="text-blue-600">dassyor</span><span className="text-gray-900">.com</span>
            </span>
          </Link>
          <p className="text-sm text-gray-600">
            © {new Date().getFullYear()} dassyor.com. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}