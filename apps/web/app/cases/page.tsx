"use client";

import { useState } from "react";
import { Shield, CheckCircle, XCircle, HelpCircle, FileCheck } from "lucide-react";
import { RiskGauge } from "@/components/RiskGauge";
import { FraudGraph } from "@/components/FraudGraph";
import { CaseTimeline } from "@/components/CaseTimeline";

export default function CasesPage() {
  const [selectedCase, setSelectedCase] = useState<string | null>("FM-DEMO-001");
  const [caseStatus, setCaseStatus] = useState("UNDER_REVIEW");

  const cases = [
    { id: "FM-DEMO-001", risk: 97, status: "UNDER_REVIEW", amount: "₹85,000", institution: "BANK_A", customer: "CUS-882" },
    { id: "FM-2024-0892", risk: 84, status: "DISPUTED", amount: "₹42,500", institution: "BANK_B", customer: "CUS-445" },
    { id: "FM-2024-0891", risk: 91, status: "CONFIRMED", amount: "₹1,25,000", institution: "BANK_A", customer: "CUS-221" },
    { id: "FM-2024-0890", risk: 76, status: "CLEARED", amount: "₹18,000", institution: "BANK_C", customer: "CUS-998" },
  ];

  const selectedCaseData = cases.find(c => c.id === selectedCase);

  const riskBreakdown = [
    { feature: "Amount Anomaly", impact: 23, description: "₹85,000 is 8.1× normal transfer amount" },
    { feature: "New Beneficiary", impact: 18, description: "First transaction to this account" },
    { feature: "New Device", impact: 16, description: "Device first seen 8 minutes ago" },
    { feature: "Network Risk", impact: 19, description: "Connected to 2 accounts with unresolved fraud" },
    { feature: "External Signal", impact: 19, description: "Bank B confirmed mule association (CLM-1092)" },
  ];

  const externalSignal = {
    claimId: "CLM-1092",
    sourceInstitution: "BANK_B",
    signalType: "CONFIRMED_MULE_ASSOCIATION",
    confidence: 0.91,
    issuedAt: "2024-09-01",
    expiresAt: "2024-12-01",
    verified: true,
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900">FraudMesh</h1>
                <p className="text-sm text-slate-500">Investigator Dashboard</p>
              </div>
            </div>
            <nav className="flex gap-4">
              <a href="/" className="text-slate-600 hover:text-blue-600 font-medium">Home</a>
              <a href="/cases" className="text-blue-600 font-medium">Cases</a>
              <a href="/network" className="text-slate-600 hover:text-blue-600 font-medium">Network</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cases List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="font-semibold text-slate-900">Open Investigations</h2>
              </div>
              <div className="divide-y">
                {cases.map((case_) => (
                  <button
                    key={case_.id}
                    onClick={() => setSelectedCase(case_.id)}
                    className={`w-full p-4 text-left hover:bg-slate-50 transition-colors ${
                      selectedCase === case_.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-slate-900">{case_.id}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        case_.status === 'CONFIRMED' ? 'bg-red-100 text-red-700' :
                        case_.status === 'DISPUTED' ? 'bg-yellow-100 text-yellow-700' :
                        case_.status === 'CLEARED' ? 'bg-green-100 text-green-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {case_.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="text-sm text-slate-600">{case_.institution} • {case_.amount}</div>
                    <div className="text-xs text-slate-500 mt-1">Risk: {case_.risk}/100</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Case Details */}
          <div className="lg:col-span-2 space-y-6">
            {selectedCaseData && (
              <>
                {/* Risk Overview */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h2 className="text-xl font-bold text-slate-900">{selectedCaseData.id}</h2>
                      <p className="text-slate-600 mt-1">Transaction: {selectedCaseData.amount}</p>
                      <p className="text-sm text-slate-500">Customer: {selectedCaseData.customer}</p>
                    </div>
                    <RiskGauge score={selectedCaseData.risk} size="lg" />
                  </div>

                  {/* Risk Breakdown */}
                  <div className="border-t pt-4">
                    <h3 className="font-semibold text-slate-900 mb-3">Why is this risky?</h3>
                    <div className="space-y-2">
                      {riskBreakdown.map((item) => (
                        <div key={item.feature} className="flex items-center justify-between p-3 bg-slate-50 rounded">
                          <div>
                            <div className="font-medium text-slate-900">{item.feature}</div>
                            <div className="text-sm text-slate-600">{item.description}</div>
                          </div>
                          <div className="text-lg font-bold text-red-600">+{item.impact}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* External Signal */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="h-5 w-5 text-indigo-600" />
                    <h3 className="font-semibold text-slate-900">Cross-Institution Signal</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-slate-500">Source Institution</div>
                      <div className="font-medium">{externalSignal.sourceInstitution}</div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-500">Signal Type</div>
                      <div className="font-medium">{externalSignal.signalType.replace('_', ' ')}</div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-500">Confidence</div>
                      <div className="font-medium">{(externalSignal.confidence * 100).toFixed(0)}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-500">Claim ID</div>
                      <div className="font-medium">{externalSignal.claimId}</div>
                    </div>
                  </div>
                  {externalSignal.verified && (
                    <div className="mt-4 flex items-center gap-2 text-green-600 text-sm">
                      <CheckCircle className="h-4 w-4" />
                      <span>Signature verified • Evidence integrity confirmed</span>
                    </div>
                  )}
                </div>

                {/* Fraud Graph */}
                <FraudGraph caseId={selectedCaseData.id} height="350px" />

                {/* Investigator Actions */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-semibold text-slate-900 mb-4">Investigation Decision</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={() => setCaseStatus('CONFIRMED')}
                      className={`p-4 rounded-lg border-2 flex flex-col items-center gap-2 transition-all ${
                        caseStatus === 'CONFIRMED'
                          ? 'border-red-600 bg-red-50'
                          : 'border-slate-200 hover:border-red-300'
                      }`}
                    >
                      <CheckCircle className="h-6 w-6 text-red-600" />
                      <span className="font-medium">Confirm Fraud</span>
                    </button>
                    <button
                      onClick={() => setCaseStatus('UNDER_REVIEW')}
                      className={`p-4 rounded-lg border-2 flex flex-col items-center gap-2 transition-all ${
                        caseStatus === 'UNDER_REVIEW'
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-slate-200 hover:border-blue-300'
                      }`}
                    >
                      <HelpCircle className="h-6 w-6 text-blue-600" />
                      <span className="font-medium">Keep Under Review</span>
                    </button>
                    <button
                      onClick={() => setCaseStatus('DISPUTED')}
                      className={`p-4 rounded-lg border-2 flex flex-col items-center gap-2 transition-all ${
                        caseStatus === 'DISPUTED'
                          ? 'border-yellow-600 bg-yellow-50'
                          : 'border-slate-200 hover:border-yellow-300'
                      }`}
                    >
                      <XCircle className="h-6 w-6 text-yellow-600" />
                      <span className="font-medium">Dispute Signal</span>
                    </button>
                    <button
                      onClick={() => setCaseStatus('CLEARED')}
                      className={`p-4 rounded-lg border-2 flex flex-col items-center gap-2 transition-all ${
                        caseStatus === 'CLEARED'
                          ? 'border-green-600 bg-green-50'
                          : 'border-slate-200 hover:border-green-300'
                      }`}
                    >
                      <CheckCircle className="h-6 w-6 text-green-600" />
                      <span className="font-medium">Clear Customer</span>
                    </button>
                  </div>
                  {caseStatus !== selectedCaseData.status && (
                    <div className="mt-4">
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Reason for decision
                      </label>
                      <textarea
                        className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        rows={3}
                        placeholder="Provide justification for this decision..."
                      />
                      <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Submit Decision
                      </button>
                    </div>
                  )}
                </div>

                {/* Timeline */}
                <CaseTimeline events={[]} />
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
