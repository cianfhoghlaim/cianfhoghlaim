/**
 * DialectSelector - Voice Component.
 *
 * Irish dialect selection (Connacht, Munster, Ulster, Standard).
 */

import { useMemo } from "react";
import { MapPin, Check } from "lucide-react";
import { type IrishDialect, DIALECTS, type DialectInfo } from "../../hooks/useIrishTTS";

// ============================================================================
// Types
// ============================================================================

export interface DialectSelectorProps {
  /** Current dialect */
  value: IrishDialect;
  /** Change handler */
  onChange: (dialect: IrishDialect) => void;
  /** Display variant */
  variant?: "buttons" | "dropdown" | "cards";
  /** Show region info */
  showRegion?: boolean;
  /** Show description */
  showDescription?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Size */
  size?: "sm" | "md" | "lg";
  /** Custom class name */
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function DialectSelector({
  value,
  onChange,
  variant = "buttons",
  showRegion = false,
  showDescription = false,
  disabled = false,
  size = "md",
  className = "",
}: DialectSelectorProps) {
  const dialects = useMemo(() => DIALECTS, []);

  const sizeConfig = {
    sm: { text: "text-xs", padding: "px-2 py-1", gap: "gap-1" },
    md: { text: "text-sm", padding: "px-3 py-1.5", gap: "gap-2" },
    lg: { text: "text-base", padding: "px-4 py-2", gap: "gap-3" },
  };

  const config = sizeConfig[size];

  // Buttons variant
  if (variant === "buttons") {
    return (
      <div className={`flex items-center ${config.gap} ${className}`}>
        {dialects.map((d) => (
          <button
            key={d.id}
            onClick={() => onChange(d.id)}
            disabled={disabled}
            className={`${config.padding} ${config.text} rounded-lg transition-colors ${
              value === d.id
                ? "bg-green-100 text-green-700 font-medium border border-green-300"
                : "bg-white border border-gray-200 text-gray-600 hover:border-green-300 hover:bg-green-50"
            } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
            title={`${d.name} - ${d.region}`}
          >
            {d.name}
          </button>
        ))}
      </div>
    );
  }

  // Dropdown variant
  if (variant === "dropdown") {
    return (
      <div className={`relative ${className}`}>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value as IrishDialect)}
          disabled={disabled}
          className={`w-full ${config.padding} ${config.text} rounded-lg border border-gray-300 bg-white text-gray-700 focus:border-green-500 focus:ring-2 focus:ring-green-200 appearance-none cursor-pointer ${
            disabled ? "opacity-50 cursor-not-allowed" : ""
          }`}
        >
          {dialects.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name} - {d.region}
            </option>
          ))}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <MapPin className="h-4 w-4 text-gray-400" />
        </div>
      </div>
    );
  }

  // Cards variant
  return (
    <div className={`grid grid-cols-2 ${config.gap} ${className}`}>
      {dialects.map((d) => (
        <button
          key={d.id}
          onClick={() => onChange(d.id)}
          disabled={disabled}
          className={`p-3 rounded-lg border text-left transition-colors ${
            value === d.id
              ? "bg-green-50 border-green-300 ring-2 ring-green-200"
              : "bg-white border-gray-200 hover:border-green-300 hover:bg-green-50/50"
          } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className={`font-medium text-gray-900 ${config.text}`}>
                {d.name}
              </p>
              {showRegion && (
                <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {d.region}
                </p>
              )}
              {showDescription && (
                <p className="text-xs text-gray-400 mt-1">{d.description}</p>
              )}
            </div>
            {value === d.id && (
              <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
            )}
          </div>
        </button>
      ))}
    </div>
  );
}

/**
 * Compact dialect badge that shows current selection.
 */
export function DialectBadge({
  dialect,
  size = "sm",
  className = "",
}: {
  dialect: IrishDialect;
  size?: "sm" | "md";
  className?: string;
}) {
  const info = DIALECTS.find((d) => d.id === dialect);

  const sizeConfig = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-1",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full bg-green-100 text-green-700 ${sizeConfig[size]} ${className}`}
      title={info?.description}
    >
      <MapPin className={size === "sm" ? "h-3 w-3" : "h-3.5 w-3.5"} />
      {info?.name || dialect}
    </span>
  );
}

export default DialectSelector;
