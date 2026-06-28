import React from "react";

interface CelticFrameProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  variant?: "primary" | "secondary" | "glass";
  cornerAccent?: boolean;
}

export const CelticFrame: React.FC<CelticFrameProps> = ({
  children,
  className = "",
  title,
  variant = "primary",
  cornerAccent = true,
}) => {
  const baseStyles = "relative overflow-hidden transition-all duration-300";

  const variants = {
    primary: "bg-slate-900 border-2 border-slate-700 shadow-xl shadow-black/50",
    secondary: "bg-slate-800 border border-slate-600 shadow-lg",
    glass:
      "bg-slate-900/80 backdrop-blur-md border border-slate-700/50 shadow-2xl",
  };

  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${className} rounded-lg group`}
    >
      {cornerAccent && (
        <>
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-emerald-600 rounded-tl-sm z-10" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-emerald-600 rounded-tr-sm z-10" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-emerald-600 rounded-bl-sm z-10" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-emerald-600 rounded-br-sm z-10" />

          <div className="absolute top-1 left-1 w-2 h-2 border-t border-l border-emerald-800/50 rounded-tl-sm" />
          <div className="absolute top-1 right-1 w-2 h-2 border-t border-r border-emerald-800/50 rounded-tr-sm" />
          <div className="absolute bottom-1 left-1 w-2 h-2 border-b border-l border-emerald-800/50 rounded-bl-sm" />
          <div className="absolute bottom-1 right-1 w-2 h-2 border-b border-r border-emerald-800/50 rounded-br-sm" />
        </>
      )}

      {title && (
        <div className="relative px-4 py-2 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700 flex items-center justify-center">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-8 h-[1px] bg-gradient-to-r from-transparent to-emerald-600" />
          <div className="absolute right-0 top-1/2 -translate-y-1/2 w-8 h-[1px] bg-gradient-to-l from-transparent to-emerald-600" />
          <h3 className="font-serif tracking-wider text-emerald-100 uppercase text-xs font-bold px-4">
            {title}
          </h3>
        </div>
      )}

      <div className="relative z-0">{children}</div>

      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIi8+CjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiMwMDAiLz4KPC9zdmc+')] mix-blend-overlay" />
    </div>
  );
};
