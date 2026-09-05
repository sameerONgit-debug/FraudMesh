"use client";

import { useState } from "react";
import { Activity, Shield, Network, FileCheck, Users, TrendingUp } from "lucide-react";

export default function Home() {
  const [demoStep, setDemoStep] = useState(0);

  const demoSteps = [
    { title: "Transaction Received", risk: 0, description: "₹85,000 transaction from ACC-A101 to ACC-B781" },
    { title: "Local AI Risk Score", risk: 72, description: "HIGH RISK - Amount anomaly detected" },
    { title: "Graph Enrichment", risk: 88, description: "CRITICAL - Shared device with known fraud account" },
    { title: "External Signal", risk: 97, description: "CRITICAL - Bank B confirms mule association" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900">FraudMesh</h1>
                <p className="text-sm text-slate-500">Detect the Network. Verify the Signal. Preserve the Evidence.</p>
              </div>
            </div>
            <nav className="flex gap-4">
              <a href="/dashboard" className="text-slate-600 hover:text-blue-600 font-medium">Dashboard</a>
              <a href="/cases" className="text-slate-600 hover:text-blue-600 font-medium">Cases</a>
              <a href="/network" className="text-slate-600 hover:text-blue-600 font-medium">Network</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Demo Section */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Live Demo Scenario</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex gap-4 mb-6">
              {demoSteps.map((step, index) => (
                <button
                  key={index}
                  onClick={() => setDemoStep(index)}
                  className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                    demoStep === index
                      ? "border-blue-600 bg-blue-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="text-sm font-medium text-slate-600 mb-1">Step {index + 1}</div>
                  <div className="text-xs text-slate-500">{step.title}</div>
                </button>
              ))}
            </div>

            <div className="bg-slate-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">{demoSteps[demoStep].title}</h3>
                <div className={`px-4 py-2 rounded-full text-white font-bold ${
                  demoSteps[demoStep].risk === 0 ? 'bg-green-500' :
                  demoSteps[demoStep].risk < 70 ? 'bg-yellow-500' :
                  demoSteps[demoStep].risk < 90 ? 'bg-orange-500' : 'bg-red-600'
                }`}>
                  Risk: {demoSteps[demoStep].risk}/100
                </div>
              </div>
              <p className="text-slate-700">{demoSteps[demoStep].description}</p>
              
              {demoStep >= 1 && (
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="bg-white p-3 rounded border">
                    <div className="text-xs text-slate-500">Amount Anomaly</div>
                    <div className="text-lg font-bold text-orange-600">+23</div>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <div className="text-xs text-slate-500">New Beneficiary</div>
                    <div className="text-lg font-bold text-orange-600">+18</div>
                  </div>
                  {demoStep >= 2 && (
                    <>
                      <div className="bg-white p-3 rounded border">
                        <div className="text-xs text-slate-500">New Device</div>
                        <div className="text-lg font-bold text-red-600">+16</div>
                      </div>
                      <div className="bg-white p-3 rounded border">
                        <div className="text-xs text-slate-500">Network Risk</div>
                        <div className="text-lg font-bold text-red-600">+19</div>
                      </div>
                    </>
                  )}
                  {demoStep >= 3 && (
                    <div className="bg-white p-3 rounded border col-span-2">
                      <div className="text-xs text-slate-500">External Signal (Bank B)</div>
                      <div className="text-lg font-bold text-red-600">+19 - Confirmed Mule Association</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Metrics Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-3">
              <Activity className="h-6 w-6 text-blue-600" />
              <h3 className="font-semibold text-slate-900">Transactions Analyzed</h3>
            </div>
            <div className="text-3xl font-bold text-slate-900">2,847</div>
            <div className="text-sm text-green-600 mt-1">↑ 12% from yesterday</div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="h-6 w-6 text-orange-600" />
              <h3 className="font-semibold text-slate-900">High-Risk Alerts</h3>
            </div>
            <div className="text-3xl font-bold text-slate-900">23</div>
            <div className="text-sm text-slate-500 mt-1">5 require immediate review</div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-3">
              <Network className="h-6 w-6 text-purple-600" />
              <h3 className="font-semibold text-slate-900">Fraud Networks</h3>
            </div>
            <div className="text-3xl font-bold text-slate-900">7</div>
            <div className="text-sm text-green-600 mt-1">2 new clusters detected</div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-3">
              <FileCheck className="h-6 w-6 text-green-600" />
              <h3 className="font-semibold text-slate-900">Open Cases</h3>
            </div>
            <div className="text-3xl font-bold text-slate-900">14</div>
            <div className="text-sm text-slate-500 mt-1">3 disputed, 11 under review</div>
          </div>
        </section>

        {/* Recent Cases */}
        <section className="bg-white rounded-lg shadow mb-8">
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-slate-900">Recent Investigations</h2>
          </div>
          <div className="divide-y">
            {[
              { id: "FM-DEMO-001", risk: 97, status: "Under Review", amount: "₹85,000", institution: "BANK_A" },
              { id: "FM-2024-0892", risk: 84, status: "Disputed", amount: "₹42,500", institution: "BANK_B" },
              { id: "FM-2024-0891", risk: 91, status: "Confirmed", amount: "₹1,25,000", institution: "BANK_A" },
              { id: "FM-2024-0890", risk: 76, status: "Cleared", amount: "₹18,000", institution: "BANK_C" },
            ].map((case_) => (
              <div key={case_.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-3 rounded-full ${
                    case_.risk >= 85 ? 'bg-red-600' :
                    case_.risk >= 70 ? 'bg-orange-500' : 'bg-yellow-500'
                  }`} />
                  <div>
                    <div className="font-medium text-slate-900">{case_.id}</div>
                    <div className="text-sm text-slate-500">{case_.institution} • {case_.amount}</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    case_.status === 'Confirmed' ? 'bg-red-100 text-red-700' :
                    case_.status === 'Disputed' ? 'bg-yellow-100 text-yellow-700' :
                    case_.status === 'Cleared' ? 'bg-green-100 text-green-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {case_.status}
                  </span>
                  <span className="text-sm font-medium text-slate-700">Risk: {case_.risk}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Trust & Privacy */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Trust & Privacy</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              "No raw PII on ledger",
              "Institution-signed claims",
              "Claim expiry enforcement",
              "Full audit trail",
              "Role-based access",
              "Evidence integrity",
              "Purpose-bound queries",
              "Dispute lifecycle",
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-green-600" />
                <span className="text-sm text-slate-700">{feature}</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
