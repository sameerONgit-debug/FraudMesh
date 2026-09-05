import React from 'react';
import { FileCheck, AlertTriangle, Shield, CheckCircle, XCircle, HelpCircle } from 'lucide-react';

interface TimelineEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  actor: string;
  institution: string;
  reason?: string;
}

interface CaseTimelineProps {
  events: TimelineEvent[];
}

export function CaseTimeline({ events }: CaseTimelineProps) {
  const getEventIcon = (eventType: string) => {
    if (eventType.includes('CREATED')) return <FileCheck className="h-4 w-4" />;
    if (eventType.includes('RISK')) return <AlertTriangle className="h-4 w-4" />;
    if (eventType.includes('GRAPH')) return <Shield className="h-4 w-4" />;
    if (eventType.includes('EXTERNAL')) return <Shield className="h-4 w-4" />;
    if (eventType.includes('CONFIRMED')) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (eventType.includes('DISPUTED')) return <XCircle className="h-4 w-4 text-red-600" />;
    if (eventType.includes('CLEARED')) return <CheckCircle className="h-4 w-4 text-green-600" />;
    return <HelpCircle className="h-4 w-4" />;
  };

  const getEventColor = (eventType: string) => {
    if (eventType.includes('CREATED')) return 'bg-blue-100 border-blue-300';
    if (eventType.includes('RISK')) return 'bg-orange-100 border-orange-300';
    if (eventType.includes('GRAPH')) return 'bg-purple-100 border-purple-300';
    if (eventType.includes('EXTERNAL')) return 'bg-indigo-100 border-indigo-300';
    if (eventType.includes('CONFIRMED')) return 'bg-green-100 border-green-300';
    if (eventType.includes('DISPUTED')) return 'bg-red-100 border-red-300';
    if (eventType.includes('CLEARED')) return 'bg-green-100 border-green-300';
    return 'bg-slate-100 border-slate-300';
  };

  // Demo events if none provided
  const demoEvents: TimelineEvent[] = [
    {
      event_id: 'EV-001',
      event_type: 'CASE_CREATED',
      timestamp: '2024-09-05T09:31:00Z',
      actor: 'SYSTEM',
      institution: 'BANK_A',
    },
    {
      event_id: 'EV-002',
      event_type: 'RISK_COMPUTED',
      timestamp: '2024-09-05T09:31:15Z',
      actor: 'ML_ENGINE',
      institution: 'BANK_A',
      reason: 'Initial risk score: 72/100',
    },
    {
      event_id: 'EV-003',
      event_type: 'GRAPH_ENRICHED',
      timestamp: '2024-09-05T09:31:30Z',
      actor: 'GRAPH_SERVICE',
      institution: 'BANK_A',
      reason: 'Risk increased to 88/100 - shared device detected',
    },
    {
      event_id: 'EV-004',
      event_type: 'EXTERNAL_SIGNAL_RECEIVED',
      timestamp: '2024-09-05T09:31:45Z',
      actor: 'SIGNAL_SERVICE',
      institution: 'BANK_B',
      reason: 'Claim CLM-1092 - Confirmed mule association',
    },
    {
      event_id: 'EV-005',
      event_type: 'EVIDENCE_ANCHORED',
      timestamp: '2024-09-05T09:32:00Z',
      actor: 'LEDGER_SERVICE',
      institution: 'BANK_A',
      reason: 'Evidence hash recorded on permissioned ledger',
    },
    {
      event_id: 'EV-006',
      event_type: 'INVESTIGATION_STARTED',
      timestamp: '2024-09-05T09:32:30Z',
      actor: 'INV-32',
      institution: 'BANK_A',
    },
  ];

  const timelineEvents = events.length > 0 ? events : demoEvents;

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-slate-900">Case Audit Timeline</h3>
        <p className="text-sm text-slate-500 mt-1">
          Complete provenance history with evidence hashes
        </p>
      </div>
      <div className="p-4">
        <div className="space-y-4">
          {timelineEvents.map((event, index) => (
            <div key={event.event_id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${getEventColor(event.event_type)}`}>
                  {getEventIcon(event.event_type)}
                </div>
                {index < timelineEvents.length - 1 && (
                  <div className="w-0.5 flex-1 bg-slate-200 my-1" />
                )}
              </div>
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-slate-900">
                    {event.event_type.replace(/_/g, ' ')}
                  </div>
                  <div className="text-xs text-slate-500">
                    {new Date(event.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="text-sm text-slate-600 mt-1">
                  {event.actor} • {event.institution}
                </div>
                {event.reason && (
                  <div className="text-sm text-slate-700 mt-2 bg-slate-50 p-2 rounded">
                    {event.reason}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
