import { LucideIcon } from 'lucide-react';

interface NavItemProps {
  icon: LucideIcon;
  label: string;
  href: string;
  active?: boolean;
  badge?: number;
}

export function NavItem({ icon: Icon, label, href, active, badge }: NavItemProps) {
  return (
    <a
      href={href}
      className={`
        group flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors
        ${active 
          ? 'bg-secondary text-foreground' 
          : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
        }
      `}
    >
      <div className="flex items-center gap-3">
        <Icon className={`h-4 w-4 ${active ? 'text-primary' : 'group-hover:text-primary'}`} />
        <span>{label}</span>
      </div>
      {badge !== undefined && badge > 0 && (
        <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1 text-xs font-medium text-primary-foreground">
          {badge > 99 ? '99+' : badge}
        </span>
      )}
    </a>
  );
}
