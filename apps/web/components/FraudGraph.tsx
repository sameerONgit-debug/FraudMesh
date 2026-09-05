"use client";

import React, { useEffect, useState } from 'react';
import CytoscapeComponent from 'cytoscape-react';
import cytoscape from 'cytoscape';

interface NodeData {
  id: string;
  label: string;
  type: 'account' | 'device' | 'customer' | 'transaction' | 'beneficiary';
  risk?: number;
}

interface EdgeData {
  source: string;
  target: string;
  label: string;
  confidence?: number;
}

interface FraudGraphProps {
  caseId?: string;
  width?: string;
  height?: string;
}

export function FraudGraph({ caseId, width = '100%', height = '400px' }: FraudGraphProps) {
  const [cy, setCy] = useState<any>(null);
  const [elements, setElements] = useState<any[]>([]);

  // Demo data for the MVP - will be replaced with real API data
  useEffect(() => {
    const demoElements = [
      // Nodes
      { data: { id: 'ACC-A101', label: 'ACC-A101', type: 'account', risk: 97 } },
      { data: { id: 'ACC-B781', label: 'ACC-B781', type: 'account', risk: 95 } },
      { data: { id: 'ACC-B552', label: 'ACC-B552', type: 'account', risk: 100 } },
      { data: { id: 'DEV-442', label: 'Device 442', type: 'device', risk: 90 } },
      { data: { id: 'CUS-882', label: 'Customer 882', type: 'customer', risk: 85 } },
      { data: { id: 'TX-9822', label: '₹85,000', type: 'transaction', risk: 97 } },
      
      // Edges
      { data: { source: 'CUS-882', target: 'ACC-A101', label: 'OWNS' } },
      { data: { source: 'ACC-A101', target: 'TX-9822', label: 'SENT' } },
      { data: { source: 'TX-9822', target: 'ACC-B781', label: 'RECEIVED' } },
      { data: { source: 'ACC-A101', target: 'DEV-442', label: 'USED' } },
      { data: { source: 'ACC-B781', target: 'DEV-442', label: 'USED' } },
      { data: { source: 'ACC-B781', target: 'ACC-B552', label: 'ASSOCIATED_WITH' } },
      { data: { source: 'ACC-B552', target: 'DEV-442', label: 'USED' } },
    ];
    
    setElements(demoElements);
  }, [caseId]);

  const stylesheet = [
    {
      selector: 'node[type="account"]',
      style: {
        'background-color': '#3b82f6',
        label: 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        color: '#fff',
        'font-size': '12px',
        width: '40px',
        height: '40px',
      },
    },
    {
      selector: 'node[type="device"]',
      style: {
        'background-color': '#8b5cf6',
        label: 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        color: '#fff',
        'font-size': '10px',
        width: '30px',
        height: '30px',
      },
    },
    {
      selector: 'node[type="customer"]',
      style: {
        'background-color': '#10b981',
        label: 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        color: '#fff',
        'font-size': '12px',
        width: '45px',
        height: '45px',
      },
    },
    {
      selector: 'node[type="transaction"]',
      style: {
        'background-color': '#f97316',
        label: 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        color: '#fff',
        'font-size': '11px',
        width: '50px',
        height: '50px',
      },
    },
    {
      selector: 'edge',
      style: {
        width: 2,
        'line-color': '#94a3b8',
        'target-arrow-color': '#94a3b8',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        label: 'data(label)',
        'font-size': '10px',
        'text-rotation': 'autorotate',
      },
    },
    {
      selector: 'node[risk >= 85]',
      style: {
        'border-width': '3px',
        'border-color': '#dc2626',
      },
    },
    {
      selector: 'node[risk >= 60][risk < 85]',
      style: {
        'border-width': '2px',
        'border-color': '#f97316',
      },
    },
  ];

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-slate-900">Fraud Network Graph</h3>
        <p className="text-sm text-slate-500 mt-1">
          Showing connected entities and risk relationships
        </p>
      </div>
      <div style={{ width, height }}>
        <CytoscapeComponent
          elements={CytoscapeComponent.normalizeElements(elements)}
          stylesheet={stylesheet}
          layout={{ name: 'force', animate: true }}
          className="w-full h-full"
          cy={(cyInstance) => setCy(cyInstance)}
        />
      </div>
      <div className="p-4 border-t bg-slate-50">
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-slate-600">Account</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-slate-600">Device</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-slate-600">Customer</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span className="text-slate-600">Transaction</span>
          </div>
        </div>
      </div>
    </div>
  );
}
