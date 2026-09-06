interface RiskGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function RiskGauge({ score, size = 'md', showLabel = true }: RiskGaugeProps) {
  const getRiskLevel = (score: number) => {
    if (score >= 85) return { level: 'CRITICAL', color: 'text-risk-critical', bg: 'bg-risk-critical' };
    if (score >= 60) return { level: 'HIGH', color: 'text-risk-high', bg: 'bg-risk-high' };
    if (score >= 30) return { level: 'MODERATE', color: 'text-risk-moderate', bg: 'bg-risk-moderate' };
    return { level: 'LOW', color: 'text-risk-low', bg: 'bg-risk-low' };
  };

  const { level, color, bg } = getRiskLevel(score);
  
  const sizeClasses = {
    sm: { container: 'h-16 w-16', text: 'text-lg', label: 'text-xs' },
    md: { container: 'h-24 w-24', text: 'text-2xl', label: 'text-sm' },
    lg: { container: 'h-32 w-32', text: 'text-4xl', label: 'text-base' },
  };

  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`relative ${sizeClasses[size].container}`}>
        <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-secondary"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${color} transition-all duration-500 ease-out`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${sizeClasses[size].text} ${color}`}>
            {score}
          </span>
        </div>
      </div>
      {showLabel && (
        <span className={`font-semibold ${sizeClasses[size].label} ${color}`}>
          {level}
        </span>
      )}
    </div>
  );
}
