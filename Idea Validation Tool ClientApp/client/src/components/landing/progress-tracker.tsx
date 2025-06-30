import { motion } from "framer-motion";
import { Check } from "lucide-react";

type Step = 'idea' | 'refinement' | 'analyzing' | 'email' | 'success';

interface ProgressTrackerProps {
  currentStep: Step;
}

const steps: { id: Step; label: string }[] = [
  { id: 'idea', label: 'Step 1' },
  { id: 'refinement', label: 'Step 2' },
  { id: 'analyzing', label: 'Step 3' },
  { id: 'email', label: 'Step 4' },
  { id: 'success', label: 'Step 5' }
];

export default function ProgressTracker({ currentStep }: ProgressTrackerProps) {
  const getStepStatus = (stepId: Step) => {
    const stepIndex = steps.findIndex(s => s.id === stepId);
    const currentIndex = steps.findIndex(s => s.id === currentStep);

    if (stepIndex < currentIndex) return 'Completed';
    if (stepIndex === currentIndex) return 'In Progress';
    return 'Pending';
  };

  return (
    <div className="max-w-2xl mx-auto mb-12">
      <div className="relative bg-white/95 backdrop-blur-sm rounded-xl p-8 shadow-sm">
        {/* Steps container */}
        <div className="relative flex justify-between">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id);
            const isCompleted = status === 'Completed';
            const isInProgress = status === 'In Progress';

            return (
              <div key={step.id} className="flex flex-col items-center relative z-10">
                {/* Step circle with white background gap */}
                <div className="bg-white p-1 rounded-full relative">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center
                    transition-all duration-200 border-2
                    ${isCompleted 
                      ? 'bg-green-500 border-green-500 text-white' 
                      : isInProgress 
                      ? 'bg-white border-blue-600' 
                      : 'bg-white border-gray-200'}
                  `}>
                    {isCompleted ? (
                      <Check className="w-5 h-5" />
                    ) : isInProgress ? (
                      <div className="w-4 h-4 rounded-full bg-blue-600" />
                    ) : null}
                  </div>
                </div>

                {/* Step label */}
                <div className="text-xs font-medium text-gray-600 mt-2">
                  {step.label}
                </div>

                {/* Step status */}
                <div className={`text-xs mt-1
                  ${isCompleted ? 'text-green-500' : isInProgress ? 'text-blue-600' : 'text-gray-400'}
                `}>
                  {status}
                </div>
              </div>
            );
          })}

          {/* Connector lines container - positioned below circles */}
          <div className="absolute top-[1.125rem] left-0 right-0 -z-10">
            {steps.map((_, index) => (
              index < steps.length - 1 && (
                <div 
                  key={`connector-${index}`}
                  className="absolute h-[2px]"
                  style={{
                    left: `${(index * 100) / (steps.length - 1)}%`,
                    width: `${100 / (steps.length - 1)}%`,
                  }}
                >
                  <div className={`
                    w-full h-full
                    ${getStepStatus(steps[index].id) === 'Completed' ? 'bg-green-500' : 'bg-gray-200'}
                  `} />
                </div>
              )
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}