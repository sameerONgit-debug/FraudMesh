interface CaseTimelineProps {
  events: Array<{
    eventId: string;
    eventType: string;
    timestamp: string;
    actor: string;
    institution: string;
    reason?: string;
    previousState?: string;
    newState?: string;
  }>;
}

export function CaseTimeline({ events }: CaseTimelineProps) {
  const getEventIcon = (eventType: string) => {
    if (eventType.includes('CREATED')) return '📋';
    if (eventType.includes('RISK')) return '⚠️';
    if (eventType.includes('GRAPH')) return '🕸️';
    if (eventType.includes('SIGNAL')) return '📡';
    if (eventType.includes('INVESTIGATION')) return '🔍';
    if (eventType.includes('CONFIRMED')) return '✅';
    if (eventType.includes('DISPUTED')) return '⚔️';
    if (eventType.includes('CLEARED')) return '✓';
    return '📝';
  };

  const getEventColor = (eventType: string) => {
    if (eventType.includes('CONFIRMED') || eventType.includes('CLEARED')) return 'border-risk-low bg-risk-low/10';
    if (eventType.includes('DISPUTED')) return 'border-risk-critical bg-risk-critical/10';
    if (eventType.includes('RISK') || eventType.includes('SIGNAL')) return 'border-risk-high bg-risk-high/10';
    return 'border-border bg-card';
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground">Case Timeline</h3>
      
      <div className="relative space-y-0">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
        
        {events.map((event, index) => (
          <div key={event.eventId} className="relative pl-12 pb-6 last:pb-0">
            {/* Dot on timeline */}
            <div className={`
              absolute left-0 top-1 h-8 w-8 rounded-full border-2 flex items-center justify-center text-xs
              ${getEventColor(event.eventType)}
            `}>
              {getEventIcon(event.eventType)}
            </div>
            
            {/* Content */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium text-foreground">
                  {event.eventType.replace(/_/g, ' ')}
                </span>
                <span className="text-xs text-muted-foreground">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
              
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span>{event.actor}</span>
                <span>•</span>
                <span>{event.institution}</span>
              </div>
              
              {(event.previousState && event.newState) && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground">
                    {event.previousState.replace(/_/g, ' ')}
                  </span>
                  <svg className="h-3 w-3 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="px-2 py-0.5 rounded bg-primary text-primary-foreground">
                    {event.newState.replace(/_/g, ' ')}
                  </span>
                </div>
              )}
              
              {event.reason && (
                <p className="text-xs text-muted-foreground italic border-l-2 border-border pl-3">
                  "{event.reason}"
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
