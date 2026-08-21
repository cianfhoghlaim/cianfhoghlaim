import { Link } from "@tanstack/react-router";
import { FileText, History, Settings, Cpu } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:border-slate-700 dark:bg-slate-900/95">
      <div className="container mx-auto flex h-14 items-center px-4">
        <div className="flex items-center gap-2 font-semibold">
          <FileText className="h-5 w-5 text-blue-600" />
          <span className="text-slate-900 dark:text-white">OCR Compare</span>
        </div>

        <nav className="ml-8 flex items-center gap-6">
          <NavLink to="/" icon={<Cpu className="h-4 w-4" />}>
            Dashboard
          </NavLink>
          <NavLink to="/compare" icon={<FileText className="h-4 w-4" />}>
            Compare
          </NavLink>
          <NavLink to="/history" icon={<History className="h-4 w-4" />}>
            History
          </NavLink>
          <NavLink to="/models" icon={<Settings className="h-4 w-4" />}>
            Models
          </NavLink>
        </nav>

        <div className="ml-auto flex items-center gap-4">
          <span className="text-xs text-slate-500 dark:text-slate-400">
            14 models available
          </span>
        </div>
      </div>
    </header>
  );
}

function NavLink({
  to,
  icon,
  children,
}: {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Link
      to={to}
      className="flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
      activeProps={{
        className: "text-blue-600 dark:text-blue-400",
      }}
    >
      {icon}
      {children}
    </Link>
  );
}
