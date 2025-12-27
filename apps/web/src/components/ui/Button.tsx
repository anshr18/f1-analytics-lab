import { ButtonHTMLAttributes } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
  isLoading?: boolean;
}

export function Button({ variant = "primary", isLoading, className, children, disabled, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
        {
          "bg-f1red text-white hover:bg-red-700": variant === "primary",
          "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600": variant === "secondary",
          "border-2 border-f1red text-f1red hover:bg-f1red hover:text-white": variant === "outline",
        },
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? "Loading..." : children}
    </button>
  );
}
