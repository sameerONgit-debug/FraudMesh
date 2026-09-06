'use client';

import { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Search, 
  Network, 
  Bell, 
  ShieldCheck, 
  FileText,
  Building2,
  User,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { NavItem } from './ui/nav-item';

interface AppShellProps {
  children: React.ReactNode;
  institution?: string;
  userName?: string;
}

export function AppShell({ children, institution = 'BANK_A', userName = 'Analyst' }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activePath, setActivePath] = useState('/');

  useEffect(() => {
    setActivePath(window.location.pathname);
  }, []);

  const navItems = [
    { icon: LayoutDashboard, label: 'Overview', href: '/' },
    { icon: Search, label: 'Investigations', href: '/cases', badge: 3 },
    { icon: Network, label: 'Network', href: '/network' },
    { icon: Bell, label: 'Signals', href: '/signals', badge: 1 },
    { icon: ShieldCheck, label: 'Evidence', href: '/evidence' },
    { icon: FileText, label: 'Trust', href: '/trust' },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile menu button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-card border border-border"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
      >
        {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-card border-r border-border transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-auto
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-border">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-6 w-6 text-primary" />
              <div>
                <h1 className="text-lg font-semibold tracking-tight">FraudMesh</h1>
                <p className="text-xs text-muted-foreground">Cross-institution intelligence</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <NavItem
                key={item.href}
                icon={item.icon}
                label={item.label}
                href={item.href}
                active={activePath === item.href}
                badge={item.badge}
              />
            ))}
          </nav>

          {/* Bottom section */}
          <div className="p-4 border-t border-border space-y-4">
            {/* Institution */}
            <div className="flex items-center gap-2 px-3 py-2 rounded-md bg-secondary/50 border border-border">
              <Building2 className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-foreground truncate">{institution}</p>
                <p className="text-xs text-muted-foreground">Institution</p>
              </div>
            </div>

            {/* User */}
            <div className="flex items-center gap-2 px-3 py-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-foreground truncate">{userName}</p>
                <p className="text-xs text-muted-foreground">Fraud Analyst</p>
              </div>
              <LogOut className="h-4 w-4 text-muted-foreground hover:text-foreground cursor-pointer" />
            </div>

            {/* System Status */}
            <div className="flex items-center gap-2 px-3 py-2">
              <div className="h-2 w-2 rounded-full bg-risk-low animate-pulse-slow" />
              <span className="text-xs text-muted-foreground">All systems operational</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-auto">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-6">
          <div className="flex-1">
            <h2 className="text-sm font-medium text-muted-foreground">
              {activePath === '/' && 'Fraud Operations Command Center'}
              {activePath === '/cases' && 'Investigation Queue'}
              {activePath === '/network' && 'Fraud Network Explorer'}
              {activePath === '/signals' && 'Cross-Institution Signals'}
              {activePath === '/evidence' && 'Evidence & Provenance'}
              {activePath === '/trust' && 'Trust & Verification'}
            </h2>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search cases, entities..."
                className="h-9 w-64 rounded-md border border-border bg-card pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            {/* Notifications */}
            <button className="relative p-2 rounded-md hover:bg-secondary/50">
              <Bell className="h-4 w-4 text-muted-foreground" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-risk-critical" />
            </button>
          </div>
        </header>

        {/* Page content */}
        <div className="p-6">
          {children}
        </div>
      </main>

      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </div>
  );
}
