import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Loader2 } from "lucide-react";
import ProgressTracker from "./progress-tracker";

type Step = 'idea' | 'refinement' | 'analyzing' | 'email' | 'success';

interface IdeaFormData {
  idea: string;
  problem_statement: string;
  target_audience: string;
  email: string;
}

export default function IdeaValidationForm() {
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState<Step>('idea');
  const [formData, setFormData] = useState<IdeaFormData>({
    idea: '',
    problem_statement: '',
    target_audience: '',
    email: '',
  });
  const [analysisText, setAnalysisText] = useState("Searching discussions...");
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Validate if the idea is understandable
  const isValidIdea = (idea: string): boolean => {
    const words = idea.trim().split(/\s+/);
    return words.length > 2 && idea.length >= 10;
  };

  const handleNextStep = async () => {
    if (currentStep === 'idea') {
      if (!formData.idea.trim()) {
        toast({
          title: "Required Field",
          description: "Please describe your business idea",
          variant: "destructive",
        });
        return;
      }
      await generateRefinements(formData.idea);
    } else if (currentStep === 'refinement') {
      if (
        !formData.problem_statement.trim() ||
        formData.problem_statement === "The problem statement" ||
        !formData.target_audience.trim() ||
        formData.target_audience === "The target audience"
      ) {
        toast({
          title: "Required Fields",
          description: "Please fill in both Problem Statement and Target Audience",
          variant: "destructive",
        });
        return;
      }
      setCurrentStep('analyzing');
      setAnalysisProgress(0);

      const interval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 0.5;
        });
      }, 100);

      setTimeout(() => {
        setAnalysisText("Analyzing discussions...");
      }, 8000);

      setTimeout(() => {
        clearInterval(interval);
        setCurrentStep('email');
      }, 16000);
    }
  };

  const generateRefinements = async (idea: string) => {
    setIsLoading(true);
    try {
      if (!isValidIdea(idea)) {
        setFormData(prev => ({
          ...prev,
          problem_statement: "The problem statement",
          target_audience: "The target audience",
        }));
        setCurrentStep('refinement');
        return;
      }

      const response = await fetch('/api/refine-idea', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idea }),
      });

      if (!response.ok) {
        throw new Error('Failed to refine idea');
      }

      const data = await response.json();
      setFormData(prev => ({
        ...prev,
        problem_statement: data.problem_statement,
        target_audience: data.target_audience,
      }));
      setCurrentStep('refinement');
    } catch (error) {
      console.error('Error refining idea:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to refine idea. Please try again.",
        variant: "destructive",
      });
      setCurrentStep('idea');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email) {
      toast({
        title: "Required Field",
        description: "Please enter your email to receive the results",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      // Log the payload for debugging
      console.log('Submitting data:', {
        email: formData.email.trim(),
        idea: formData.idea.trim(),
        problem_statement: formData.problem_statement.trim(),
        target_audience: formData.target_audience.trim(),
      });

      const response = await fetch('/api/submit-idea', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email.trim(),
          idea: formData.idea.trim(),
          problem_statement: formData.problem_statement.trim(),
          target_audience: formData.target_audience.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to submit idea');
      }

      const data = await response.json();
      setCurrentStep('success');
      toast({
        title: "Success",
        description: data.message,
      });
    } catch (error) {
      console.error('Submission error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Scroll to waitlist section
  const scrollToWaitlist = () => {
    const waitlistSection = document.querySelector('#waitlist');
    if (waitlistSection) {
      waitlistSection.scrollIntoView({ behavior: 'smooth' });
    } else {
      window.location.href = '/#waitlist';
    }
  };

  // Common styles update
  const buttonClassName = "max-w-[220px] bg-blue-600 hover:bg-blue-500 text-white px-6 py-3.5 rounded-xl shadow-sm transition-all duration-200 hover:shadow-md active:scale-[0.98]";
  const formContainerClassName = "max-w-2xl mx-auto bg-white/95 backdrop-blur-sm rounded-lg p-6 transition-all duration-300";

  // Add consistent form section class
  const formSectionClassName = "max-w-lg mx-auto space-y-6";

  return (
    <div className={formContainerClassName}>
      <ProgressTracker currentStep={currentStep} />
      <AnimatePresence mode="wait">
        {currentStep === 'idea' && (
          <motion.div
            key="idea"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-4"
          >
            <div>
              <label className="text-lg font-medium mb-3 block">
                <div className="flex justify-between items-center">
                  <span>What's your business idea?</span>
                </div>
              </label>
              <Textarea
                name="idea"
                placeholder="Describe your business idea..."
                value={formData.idea}
                onChange={handleChange}
                className="min-h-[120px] resize-none bg-white border-gray-200 text-base"
                disabled={isLoading}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Your business idea is not saved or viewed by dassyor.
              </div>
              <Button
                onClick={handleNextStep}
                className={buttonClassName}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Next step
                    <ArrowRight className="ml-2.5 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        )}

        {currentStep === 'refinement' && (
          <motion.div
            key="refinement"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-6"
          >
            <div>
              <label className="text-lg font-medium mb-3 block">Problem Statement</label>
              <Textarea
                name="problem_statement"
                value={formData.problem_statement}
                onChange={handleChange}
                className="min-h-[100px] resize-none bg-white border-gray-200 text-base"
                placeholder="The problem statement"
              />
            </div>
            <div>
              <label className="text-lg font-medium mb-3 block">Target Audience</label>
              <Textarea
                name="target_audience"
                value={formData.target_audience}
                onChange={handleChange}
                className="resize-none bg-white border-gray-200 text-base"
                placeholder="The target audience"
              />
            </div>
            <div className="flex justify-end">
              <Button
                onClick={handleNextStep}
                className={buttonClassName}
              >
                Search
                <ArrowRight className="ml-2.5 h-4 w-4" />
              </Button>
            </div>
          </motion.div>
        )}

        {currentStep === 'analyzing' && (
          <motion.div
            key="analyzing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="py-8 space-y-6"
          >
            <div className="w-full max-w-md mx-auto space-y-4">
              <div className="bg-gray-100 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-blue-600 rounded-full"
                  initial={{ width: "0%" }}
                  animate={{ width: `${analysisProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <motion.p
                key={analysisText}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                transition={{ duration: 0.5 }}
                className="text-sm text-gray-600 text-center"
              >
                {analysisText}
              </motion.p>
            </div>
          </motion.div>
        )}

        {currentStep === 'email' && (
          <motion.div
            key="email"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={formSectionClassName}
          >
            <div className="max-w-lg space-y-6">
              <h3 className="text-lg font-medium text-gray-900 text-left">
                The analysis is complete! Where should we send the results?
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  type="email"
                  name="email"
                  placeholder="Enter your email..."
                  value={formData.email}
                  onChange={handleChange}
                  className="bg-white border-gray-200 text-base h-12 w-full"
                />
                <div className="flex justify-end">
                  <Button
                    type="submit"
                    className={buttonClassName}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      "Send me the results"
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </motion.div>
        )}

        {currentStep === 'success' && (
          <motion.div
            key="success"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={formSectionClassName}
          >
            <div className="max-w-lg space-y-4">
              <h3 className="text-lg font-medium text-gray-900 text-left">
                Your analysis on the way
              </h3>
              <p className="text-gray-600">
                You should receive an email with the results shortly. In the meantime, join our waitlist for early beta access and be among the first to turn your idea into a product that people actually want.
              </p>
            </div>
            <div className="flex justify-center pt-2">
              <Button
                onClick={scrollToWaitlist}
                className={`${buttonClassName} hover:bg-blue-500`}
              >
                Join Waitlist
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}