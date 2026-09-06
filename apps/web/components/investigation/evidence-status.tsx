import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

interface EvidenceStatusProps {
  status: 'verified' | 'mismatch' | 'pending' | 'failed';
  claimId?: string;
  ledgerTxId?: string;
  timestamp?: string;
}

export function EvidenceStatus({ status, claimId, ledgerTxId, timestamp }: EvidenceStatusProps) {
  const getConfig = () => {
    switch (status) {
      case 'verified':
        return {
          icon: CheckCircle2,
          color: 'text-risk-low',
          bg: 'bg-risk-low/10',
          label: 'Evidence Verified',
          description: 'Hash matches ledger record'
        };
      case 'mismatch':
        return {
          icon: AlertTriangle,
          color: 'text-risk-critical',
          bg: 'bg-risk-critical/10',
          label: 'Integrity Mismatch',
          description: 'Evidence has been modified'
        };
      case 'pending':
        return {
          icon: ShieldCheck,
          color: 'text-risk-moderate',
          bg: 'bg-risk-moderate/10',
          label: 'Pending Anchoring',
          description: 'Waiting for ledger confirmation'
        };
      case 'failed':
        return {
          icon: XCircle,
          color: 'text-muted-foreground',
          bg: 'bg-muted',
          label: 'Verification Failed',
          description: 'Unable to verify evidence'
        };
    }
  };

  const config = getConfig();
  const Icon = config.icon;

  return (
    <div className={`rounded-lg border border-border p-4 ${config.bg}`}>
      <div className="flex items-start gap-3">
        <Icon className={`h-5 w-5 ${config.color} mt-0.5`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className={`text-sm font-semibold ${config.color}`}>
              {config.label}
            </h4>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {config.description}
          </p>
          
          {(claimId || ledgerTxId || timestamp) && (
            <div className="mt-3 space-y-1">
              {claimId && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-muted-foreground">Claim ID:</span>
                  <code className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">
                    {claimId}
                  </code>
                </div>
              )}
              {ledgerTxId && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-muted-foreground">Ledger Tx:</span>
                  <code className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground truncate max-w-[200px]">
                    {ledgerTxId}
                  </code>
                </div>
              )}
              {timestamp && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-muted-foreground">Recorded:</span>
                  <span className="text-foreground">{timestamp}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Expandable technical details */}
      <details className="mt-3 group">
        <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground flex items-center gap-1">
          <span>Technical Details</span>
          <svg className="h-3 w-3 transform group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </summary>
        <div className="mt-2 p-3 rounded-md bg-background border border-border space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Algorithm:</span>
            <span className="text-foreground">SHA-256</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Ledger:</span>
            <span className="text-foreground">Hyperledger Fabric</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Channel:</span>
            <span className="text-foreground">fraudmesh-channel</span>
          </div>
          <p className="text-xs text-muted-foreground pt-2 border-t border-border">
            The ledger records the integrity and history of a shared claim. It does not prove that the underlying allegation is true.
          </p>
        </div>
      </details>
    </div>
  );
}
