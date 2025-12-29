import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  variant?: 'default' | 'primary' | 'danger' | 'warning';
}

export function StatCard({ title, value, subtitle, icon: Icon, trend, variant = 'default' }: StatCardProps) {
  const variantStyles = {
    default: 'border-border',
    primary: 'border-primary/30 shadow-[0_0_30px_hsl(142_76%_45%_/_0.1)]',
    danger: 'border-destructive/30 shadow-[0_0_30px_hsl(0_84%_60%_/_0.1)]',
    warning: 'border-warning/30 shadow-[0_0_30px_hsl(38_92%_50%_/_0.1)]',
  };

  const iconStyles = {
    default: 'bg-secondary text-muted-foreground',
    primary: 'bg-primary/20 text-primary',
    danger: 'bg-destructive/20 text-destructive',
    warning: 'bg-warning/20 text-warning',
  };

  return (
    <div className={cn("stat-card border", variantStyles[variant])}>
      <div className="flex items-start justify-between">
        <div className="space-y-3">
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{title}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold tracking-tight animate-count">{value}</span>
            {subtitle && (
              <span className="text-sm text-muted-foreground">{subtitle}</span>
            )}
          </div>
          {trend && (
            <div className={cn(
              "flex items-center gap-1 text-sm font-medium",
              trend.isPositive ? "text-primary" : "text-destructive"
            )}>
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span>{Math.abs(trend.value)}% from last hour</span>
            </div>
          )}
        </div>
        <div className={cn("p-3 rounded-xl", iconStyles[variant])}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}
