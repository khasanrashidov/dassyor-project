import confetti from 'canvas-confetti';
import { useCallback } from 'react';

type ConfettiColors = {
  primary?: string[];
  secondary?: string[];
};

export function useConfetti() {
  const fire = useCallback((colors?: ConfettiColors) => {
    // Create two confetti bursts for a more dynamic effect
    const count = 200;
    const defaults = {
      origin: { y: 0.7 },
      colors: colors?.primary || ['#4338ca', '#1d4ed8', '#2563eb'],
      disableForReducedMotion: true
    };

    function shoot() {
      confetti({
        ...defaults,
        particleCount: count,
        spread: 60,
        scalar: 1.2,
        drift: 0,
      });

      confetti({
        ...defaults,
        particleCount: count * 0.75,
        spread: 80,
        scalar: 0.8,
        drift: 1,
      });
    }

    // Fire two bursts in sequence
    shoot();
    setTimeout(shoot, 250);
  }, []);

  return { fire };
}
