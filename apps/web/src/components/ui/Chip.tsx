"use client";

interface ChipProps {
  children: React.ReactNode;
  variant?: "success" | "warning" | "error" | "info" | "default";
  size?: "sm" | "md";
}

export function Chip({ children, variant = "default", size = "md" }: ChipProps) {
  const variantStyles = {
    success: "bg-[var(--color-success-light)] text-[var(--color-success)] border-[var(--color-success)]",
    warning: "bg-[var(--color-warning-light)] text-[var(--color-warning)] border-[var(--color-warning)]",
    error: "bg-[var(--color-error-light)] text-[var(--color-error)] border-[var(--color-error)]",
    info: "bg-[var(--color-info-light)] text-[var(--color-info)] border-[var(--color-info)]",
    default: "bg-[var(--color-surface)] text-[var(--color-text-secondary)] border-[var(--color-border)]",
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
  };

  return (
    <span
      className={`
        inline-flex items-center rounded-full border font-medium
        ${variantStyles[variant]}
        ${sizeStyles[size]}
      `}
    >
      {children}
    </span>
  );
}
