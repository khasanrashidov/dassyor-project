import { LoadingMascot } from "./mascot";

interface LoadingStateProps {
  fullScreen?: boolean;
  children: React.ReactNode;
  isLoading: boolean;
}

export function LoadingState({ fullScreen = false, children, isLoading }: LoadingStateProps) {
  if (!isLoading) return <>{children}</>;

  const containerClasses = fullScreen
    ? "fixed inset-0 bg-background/80 backdrop-blur-sm"
    : "relative min-h-[200px]";

  return (
    <div className={containerClasses}>
      <div className="absolute inset-0 flex items-center justify-center">
        <LoadingMascot />
      </div>
      <div className={isLoading ? "invisible" : undefined}>
        {children}
      </div>
    </div>
  );
}
