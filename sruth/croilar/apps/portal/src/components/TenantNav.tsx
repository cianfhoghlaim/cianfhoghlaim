/**
 * Dynamic Navigation Component
 * Renders navigation based on tenant configuration
 */

import { Link, useRouter } from "@tanstack/react-router";
import { useTenant, useNavigation } from "@/lib/tenant";
import type { TenantFeatures } from "@/lib/tenant";
import {
  BookOpen,
  Languages,
  MessageCircle,
  Folder,
  Music,
  Code,
  Gamepad2,
  User,
  Home,
  Settings,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

// Icon mapping for navigation items
const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  book: BookOpen,
  languages: Languages,
  "message-circle": MessageCircle,
  folder: Folder,
  music: Music,
  code: Code,
  gamepad: Gamepad2,
  user: User,
  home: Home,
  settings: Settings,
};

interface NavItemProps {
  label: string;
  path: string;
  icon?: string;
  isActive?: boolean;
  onClick?: () => void;
}

function NavItem({ label, path, icon, isActive, onClick }: NavItemProps) {
  const Icon = icon ? iconMap[icon] : null;

  return (
    <Link
      to={path}
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
        "hover:bg-primary/10",
        isActive && "bg-primary/20 text-primary font-medium"
      )}
    >
      {Icon && <Icon className="w-5 h-5" />}
      <span>{label}</span>
    </Link>
  );
}

export function TenantNav() {
  const tenant = useTenant();
  const { primary, footer } = useNavigation();
  const router = useRouter();
  const currentPath = router.state.location.pathname;
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and brand */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-3">
              <img
                src={tenant.theme.logo}
                alt={tenant.name}
                className="h-8 w-8"
                onError={(e) => {
                  // Fallback to text if logo fails to load
                  e.currentTarget.style.display = "none";
                }}
              />
              <span
                className="text-xl font-bold"
                style={{ fontFamily: tenant.theme.fontHeading }}
              >
                {tenant.name}
              </span>
            </Link>
            {tenant.tagline && (
              <span className="hidden md:inline text-sm text-muted-foreground">
                {tenant.tagline}
              </span>
            )}
          </div>

          {/* Desktop navigation */}
          <div className="hidden md:flex items-center gap-1">
            {primary.map((item) => (
              <NavItem
                key={item.path}
                label={item.label}
                path={item.path}
                icon={item.icon}
                isActive={currentPath === item.path}
              />
            ))}
          </div>

          {/* Mobile menu button */}
          <button
            type="button"
            className="md:hidden p-2 rounded-lg hover:bg-primary/10"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border/50">
          <div className="px-4 py-3 space-y-1">
            {primary.map((item) => (
              <NavItem
                key={item.path}
                label={item.label}
                path={item.path}
                icon={item.icon}
                isActive={currentPath === item.path}
                onClick={() => setMobileMenuOpen(false)}
              />
            ))}
            <hr className="my-3 border-border/50" />
            {footer.map((item) => (
              <NavItem
                key={item.path}
                label={item.label}
                path={item.path}
                onClick={() => setMobileMenuOpen(false)}
              />
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}

export function TenantFooter() {
  const tenant = useTenant();
  const { footer } = useNavigation();

  return (
    <footer className="border-t border-border/50 bg-background/95 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Brand */}
          <div className="flex items-center gap-2">
            <img
              src={tenant.theme.logo}
              alt={tenant.name}
              className="h-6 w-6"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
            <span className="font-medium">{tenant.displayName}</span>
          </div>

          {/* Footer links */}
          <div className="flex items-center gap-4">
            {footer.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Copyright */}
          <div className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} {tenant.name}. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}

/**
 * Feature Guard Component
 * Only renders children if the feature is enabled for the tenant
 */
interface FeatureGuardProps {
  feature: keyof TenantFeatures;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function FeatureGuard({ feature, children, fallback }: FeatureGuardProps) {
  const tenant = useTenant();
  const isEnabled = tenant.features[feature];

  if (!isEnabled) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
}

/**
 * Route Guard Component
 * Redirects if the route is disabled for the tenant
 */
interface RouteGuardProps {
  path: string;
  children: React.ReactNode;
}

export function RouteGuard({ path, children }: RouteGuardProps) {
  const tenant = useTenant();
  const disabledPaths = tenant.routes.disabled;

  // Check if route is explicitly disabled
  if (disabledPaths.includes(path)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <h1 className="text-2xl font-bold">Page Not Available</h1>
        <p className="text-muted-foreground">
          This page is not available for {tenant.displayName}.
        </p>
        <Link to="/" className="text-primary hover:underline">
          Return to Home
        </Link>
      </div>
    );
  }

  return <>{children}</>;
}
