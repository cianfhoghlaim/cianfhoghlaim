import React from "react";
import { Sword, Shield, Wind, Zap, Sparkles } from "lucide-react";
import { CelticFrame } from "./CelticFrame";

export interface Skill {
  id: string;
  name: string;
  icon: "sword" | "shield" | "wind" | "zap" | "sparkles";
  cooldown: number;
  maxCooldown: number;
  cost?: number;
  hotkey: string;
  isActive?: boolean;
}

interface SkillBarProps {
  skills: Skill[];
  onSkillActivate: (skillId: string) => void;
  className?: string;
}

export const SkillBar: React.FC<SkillBarProps> = ({
  skills,
  onSkillActivate,
  className = "",
}) => {
  const getIcon = (icon: Skill["icon"], size: number = 24) => {
    switch (icon) {
      case "sword":
        return <Sword size={size} />;
      case "shield":
        return <Shield size={size} />;
      case "wind":
        return <Wind size={size} />;
      case "zap":
        return <Zap size={size} />;
      case "sparkles":
        return <Sparkles size={size} />;
      default:
        return <Sword size={size} />;
    }
  };

  return (
    <div className={`flex items-end gap-2 ${className}`}>
      <CelticFrame
        variant="primary"
        className="p-2 flex gap-3 items-center"
        cornerAccent={false}
      >
        {skills.map((skill) => {
          const isOnCooldown = skill.cooldown > 0;
          const cooldownPercent = isOnCooldown
            ? (skill.cooldown / skill.maxCooldown) * 100
            : 0;

          return (
            <div key={skill.id} className="relative group">
              <button
                onClick={() => !isOnCooldown && onSkillActivate(skill.id)}
                disabled={isOnCooldown}
                className={`
                  relative w-14 h-14 rounded-md border-2 
                  flex items-center justify-center transition-all duration-100
                  ${
                    isOnCooldown
                      ? "bg-slate-800 border-slate-600 cursor-not-allowed opacity-80"
                      : "bg-slate-800 border-slate-600 hover:bg-slate-700 active:translate-y-1 active:border-b-2 border-b-4 hover:border-emerald-500/50"
                  }
                  ${skill.isActive ? "ring-2 ring-emerald-400 ring-offset-2 ring-offset-slate-900" : ""}
                `}
              >
                <div
                  className={`${isOnCooldown ? "text-slate-500" : "text-emerald-100 group-hover:text-white group-hover:drop-shadow-[0_0_8px_rgba(52,211,153,0.8)] transition-all"}`}
                >
                  {getIcon(skill.icon)}
                </div>

                {isOnCooldown && (
                  <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center rounded-sm overflow-hidden">
                    <div
                      className="absolute bottom-0 left-0 right-0 bg-slate-900/50 transition-all duration-100"
                      style={{ height: `${cooldownPercent}%` }}
                    />
                    <span className="relative z-10 font-bold text-white text-lg drop-shadow-md">
                      {Math.ceil(skill.cooldown / 1000)}
                    </span>
                  </div>
                )}
              </button>

              <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-slate-900 border border-slate-600 text-slate-400 text-[10px] font-bold px-1.5 rounded-sm z-20 shadow-sm">
                {skill.hotkey}
              </div>

              <div className="absolute bottom-full mb-4 left-1/2 -translate-x-1/2 w-max max-w-[150px] bg-slate-900 border border-slate-600 p-2 rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-xl">
                <div className="text-sm font-bold text-emerald-100">
                  {skill.name}
                </div>
                {skill.cost && (
                  <div className="text-xs text-indigo-400">
                    {skill.cost} Mana
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </CelticFrame>
    </div>
  );
};
