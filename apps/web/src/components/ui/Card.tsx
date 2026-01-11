import { ReactNode } from "react";
import clsx from "clsx";

interface CardProps {
  children: ReactNode;
  className?: string;
}

interface CardHeaderProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={clsx(
        "bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6",
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className="mb-4 flex items-start justify-between">
      <div>
        {title && (
          <h4 className="text-lg font-semibold text-[var(--color-text-primary)] mb-1">
            {title}
          </h4>
        )}
        {subtitle && (
          <p className="text-sm text-[var(--color-text-secondary)]">{subtitle}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
