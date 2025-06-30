import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertNewsletterSchema } from "@shared/schema";
import session from "express-session";
import { z } from "zod";
import rateLimit from 'express-rate-limit';
import XLSX from 'xlsx';
import OpenAI from "openai";
import https from 'https';
import fetch from 'node-fetch';

// Extend express-session types
declare module 'express-session' {
  interface SessionData {
    admin?: { username: string };
    adminIP?: string;
    loginAttempts?: number;
    lastLoginAttempt?: number;
  }
}


const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || ''
});

// Define validation schema for idea submission
const ideaSubmissionSchema = z.object({
  email: z.string().email("Invalid email format"),
  idea: z.string().min(1, "Idea is required"),
  problem_statement: z.string().min(1, "Problem statement is required"),
  target_audience: z.string().min(1, "Target audience is required"),
});

// Rate limiter for idea submissions
const submissionLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: "Too many submissions from this IP, please try again"
});

export function registerRoutes(app: Express): Server {
  // Trust proxy setting for rate limiter
  app.set('trust proxy', 1);

  // Session middleware configuration with improved security for production
  app.use(
    session({
      secret: process.env.SESSION_SECRET || "your-secret-key",
      resave: false,
      saveUninitialized: false,
      cookie: { 
        secure: process.env.NODE_ENV === "production",
        sameSite: process.env.NODE_ENV === "production" ? 'none' : 'lax',
        maxAge: 24 * 60 * 60 * 1000,
        httpOnly: true
      },
      name: 'launchpad.sid'
    })
  );

  // Updated submit-idea endpoint with rate limiting
  app.post("/api/submit-idea", submissionLimiter, async (req, res) => {
    try {
      // Validate request body
      const validatedData = ideaSubmissionSchema.parse(req.body);

      // Prepare data for external API in exact format required
      const apiPayload = {
        email: validatedData.email,
        query: validatedData.idea,  // Map 'idea' to 'query'
        problem_statement: validatedData.problem_statement,
        target_audience: validatedData.target_audience
      };

      try {
        // Create custom HTTPS agent to handle self-signed certificates
        const agent = new https.Agent({
          rejectUnauthorized: false
        });

        console.log('Sending request to API:', apiPayload);

        // Send to external API with updated endpoint
        const apiResponse = await fetch('https://34.145.73.155/api/v1/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(apiPayload),
          agent: agent,
          // Add timeout to prevent long-hanging requests
          timeout: 10000 // 10 seconds timeout
        });

        if (!apiResponse.ok) {
          const errorData = await apiResponse.json().catch(() => ({}));
          throw new Error(errorData.message || 'Failed to submit to external API');
        }

        // Return the exact response from the API
        const responseData = await apiResponse.json();
        console.log('API Response:', responseData);
        res.json(responseData);
      } catch (apiError) {
        console.error('External API Error:', apiError);
        
        // Fallback response when external API is unavailable
        res.json({
          message: "Thank you! We'll analyze your idea and send the results to your email shortly.",
          status: "success"
        });
      }

    } catch (error) {
      console.error('Error in /api/submit-idea:', error);
      if (error instanceof z.ZodError) {
        res.status(400).json({ 
          message: "Validation error", 
          errors: error.errors 
        });
      } else {
        res.status(500).json({ 
          message: "Failed to submit idea",
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
  });

  // Idea refinement endpoint
  app.post("/api/refine-idea", async (req, res) => {
    try {
      if (!process.env.OPENAI_API_KEY) {
        return res.status(503).json({ message: "OpenAI service not configured" });
      }

      const { idea } = req.body;

      if (!idea) {
        return res.status(400).json({ message: "Idea is required" });
      }

      const prompt = `Given this startup idea: "${idea}"

Provide a very simple problem statement and target audience. Be extremely concise.
Format your response as a JSON object with these keys:
{
  "problem_statement": "One short, simple sentence",
  "target_audience": "2-4 words only"
}

Example:
Input: "dating site for introverts"
Output: {
  "problem_statement": "Introverts find it hard to date on regular dating platforms",
  "target_audience": "Introverted singles"
}`;

      const completion = await openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: prompt }],
        response_format: { type: "json_object" }
      });

      if (!completion.choices[0]?.message?.content) {
        throw new Error('No content in OpenAI response');
      }

      const result = JSON.parse(completion.choices[0].message.content);
      console.log('OpenAI response:', result);
      res.json(result);

    } catch (error) {
      console.error('Error refining idea:', error);
      res.status(500).json({ 
        message: "Failed to refine idea",
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  // Newsletter routes
  app.post("/api/newsletter", async (req, res) => {
    try {
      const newsletter = insertNewsletterSchema.parse(req.body);
      
      // Check if the email already exists in the newsletter list
      const allNewsletters = await storage.getNewsletters();
      const emailExists = allNewsletters.some(
        existing => existing.email.toLowerCase() === newsletter.email.toLowerCase()
      );
      
      // Only insert if email doesn't already exist
      if (!emailExists) {
        await storage.createNewsletter(newsletter);
      }
      
      // Always return success response regardless of duplicate
      return res.json({
        message: "Welcome to dassyor! We'll notify you when we launch.",
        status: "success"
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        // For validation errors, return a 400 error
        return res.status(400).json({ message: "Invalid email format" });
      } else {
        // For any other error, still return success to the user
        console.error("Newsletter error (hidden from user):", error);
        return res.json({
          message: "Welcome to dassyor! We'll notify you when we launch.",
          status: "success"
        });
      }
    }
  });

  // Rate limiting middleware for admin login
  const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5,
    message: "Too many login attempts, please try again later"
  });

  // Auth middleware with enhanced security but more flexibility for production
  const requireAuth = (req: Request, res: Response, next: Function) => {
    if (!req.session.admin) {
      return res.status(401).json({ message: "Unauthorized" });
    }
    
    // Only perform IP validation in development environment
    // In production, IP addresses can change due to proxies, CDNs, etc.
    if (process.env.NODE_ENV !== "production") {
      const clientIP = req.ip;
      if (req.session.adminIP && req.session.adminIP !== clientIP) {
        req.session.destroy(() => {});
        return res.status(401).json({ message: "Session invalid" });
      }
    }
    
    next();
  };

  // Admin routes with enhanced security
  const adminRoute = process.env.VITE_ADMIN_ROUTE || 'secure-dashboard-login';
  app.post(`/api/${adminRoute}`, loginLimiter, async (req, res) => {
    const { username, password } = req.body;

    try {
      const isValid = await storage.verifyAdmin(username, password);

      if (isValid) {
        req.session.admin = { username };
        req.session.adminIP = req.ip;

        await new Promise<void>((resolve, reject) => {
          req.session.save((err) => {
            if (err) reject(err);
            else resolve();
          });
        });
        res.json({ message: "Logged in successfully" });
      } else {
        req.session.loginAttempts = (req.session.loginAttempts || 0) + 1;
        req.session.lastLoginAttempt = Date.now();

        res.status(401).json({ message: "Invalid credentials" });
      }
    } catch (error) {
      res.status(500).json({ message: "Login failed" });
    }
  });

  // Get all newsletters
  app.get("/api/admin/newsletters", requireAuth, async (_req, res) => {
    try {
      const newsletters = await storage.getNewsletters();
      res.json(newsletters);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch newsletters" });
    }
  });

  // Delete a newsletter subscription
  app.delete("/api/admin/newsletters/:id", requireAuth, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      await storage.deleteNewsletter(id);
      res.json({ message: "Newsletter deleted successfully" });
    } catch (error) {
      res.status(500).json({ message: "Failed to delete newsletter" });
    }
  });

  // Export newsletters as Excel
  app.get("/api/admin/newsletters/export", requireAuth, async (_req, res) => {
    try {
      const newsletters = await storage.getNewsletters();

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(newsletters);

      XLSX.utils.book_append_sheet(wb, ws, "Waitlist");

      const buffer = XLSX.write(wb, { type: "buffer", bookType: "xlsx" });

      res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
      res.setHeader("Content-Disposition", "attachment; filename=waitlist.xlsx");

      res.send(buffer);
    } catch (error) {
      res.status(500).json({ message: "Failed to export newsletters" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}