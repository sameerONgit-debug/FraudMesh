import React from 'react';

interface RiskGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export function RiskGauge({ score, size = 'md' }: RiskGaugeProps) {
  const getColor = (score: number) => {
    if (score < 30) return 'bg-green-500';
    if (score < 60) return 'bg-yellow-500';
    if (score < 85) return 'bg-orange-500';
    return 'bg-red-600';
  };

  const getLabel = (score: number) => {
    if (score < 30) return 'LOW';
    if (score < 60) return 'MODERATE';
    if (score < 85) return 'HIGH';
    return 'CRITICAL';
  };

  const sizeClasses = {
    sm: { container: 'w-16 h-16', text: 'text-lg', label: 'text-xs' },
    md: { container: 'w-24 h-24', text: 'text-2xl', label: 'text-sm' },
    lg: { container: 'w-32 h-32', text: 'text-4xl', label: 'text-base' },
  };

  const percentage = Math.min(score, 100);
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${sizeClasses[size].container}`}>
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="8"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke={score >= 85 ? '#dc2626' : score >= 60 ? '#f97316' : score >= 30 ? '#eab308' : '#22c55e'}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-500"
          />
        </svg>
        <div className={`absolute inset-0 flex items-center justify-center ${sizeClasses[size].text} font-bold text-slate-900`}>
          {score}
        </div>
      </div>
      <div className={`mt-2 px-3 py-1 rounded-full ${getColor(score)} text-white font-medium ${sizeClasses[size].label}`}>
        {getLabel(score)}
      </div>
    </div>
  );
}
