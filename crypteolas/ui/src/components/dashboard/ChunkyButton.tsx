import React from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface ChunkyButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "accent" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export function ChunkyButton({
  className,
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  children,
  ...props
}: ChunkyButtonProps) {
  const baseStyles =
    "relative inline-flex items-center justify-center font-bold transition-all active:translate-y-[2px] active:shadow-none border-2 select-none disabled:opacity-50 disabled:pointer-events-none";

  const variants = {
    primary:
      "bg-indigo-500 border-indigo-700 text-white shadow-[0_4px_0_0_rgb(67,56,202)] hover:bg-indigo-400 hover:shadow-[0_4px_0_0_rgb(79,70,229)] active:bg-indigo-600",
    secondary:
      "bg-slate-700 border-slate-900 text-slate-100 shadow-[0_4px_0_0_rgb(15,23,42)] hover:bg-slate-600 hover:shadow-[0_4px_0_0_rgb(30,41,59)] active:bg-slate-800",
    accent:
      "bg-emerald-500 border-emerald-700 text-white shadow-[0_4px_0_0_rgb(4,120,87)] hover:bg-emerald-400 hover:shadow-[0_4px_0_0_rgb(5,150,105)] active:bg-emerald-600",
    danger:
      "bg-rose-500 border-rose-700 text-white shadow-[0_4px_0_0_rgb(190,18,60)] hover:bg-rose-400 hover:shadow-[0_4px_0_0_rgb(225,29,72)] active:bg-rose-600",
    ghost:
      "bg-transparent border-transparent text-slate-400 shadow-none hover:bg-slate-800 hover:text-white active:translate-y-0",
  };

  const sizes = {
    sm: "h-8 px-3 text-xs rounded-md",
    md: "h-10 px-4 text-sm rounded-lg",
    lg: "h-12 px-6 text-base rounded-xl",
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : icon ? (
        <span className="mr-2">{icon}</span>
      ) : null}
      {children}
    </button>
  );
}
