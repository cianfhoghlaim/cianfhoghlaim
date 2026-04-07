import React from "react";
import {
  MapPin,
  Sword,
  Book,
  Scroll,
  CheckCircle2,
  Circle,
} from "lucide-react";
import { CelticFrame } from "./CelticFrame";

export interface Quest {
  id: string;
  title: string;
  type: "exploration" | "combat" | "lore" | "fetch";
  status: "active" | "completed" | "failed";
  progress: number;
  maxProgress: number;
  description?: string;
}

interface QuestTrackerProps {
  quests: Quest[];
  onQuestClick?: (questId: string) => void;
  className?: string;
}

export const QuestTracker: React.FC<QuestTrackerProps> = ({
  quests,
  onQuestClick,
  className = "",
}) => {
  const getIcon = (type: Quest["type"]) => {
    switch (type) {
      case "combat":
        return <Sword size={16} className="text-red-400" />;
      case "exploration":
        return <MapPin size={16} className="text-emerald-400" />;
      case "lore":
        return <Book size={16} className="text-indigo-400" />;
      case "fetch":
        return <Scroll size={16} className="text-amber-400" />;
      default:
        return <Circle size={16} />;
    }
  };

  return (
    <CelticFrame
      title="Active Quests"
      variant="glass"
      className={`w-64 ${className}`}
    >
      <div className="p-2 space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
        {quests.length === 0 ? (
          <div className="text-center py-4 text-slate-500 text-sm italic">
            No active quests
          </div>
        ) : (
          quests.map((quest) => (
            <div
              key={quest.id}
              onClick={() => onQuestClick?.(quest.id)}
              className="group relative bg-slate-900/50 hover:bg-slate-800 border border-slate-700 hover:border-emerald-600/50 rounded p-2 transition-all cursor-pointer overflow-hidden"
            >
              <div className="absolute inset-0 bg-emerald-600/5 opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="relative flex items-start gap-2">
                <div className="mt-1 shrink-0">
                  {quest.status === "completed" ? (
                    <CheckCircle2 size={16} className="text-emerald-500" />
                  ) : (
                    getIcon(quest.type)
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-slate-200 group-hover:text-emerald-300 transition-colors truncate">
                    {quest.title}
                  </h4>

                  {quest.status === "active" && (
                    <div className="mt-1.5 space-y-1">
                      <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-600 rounded-full transition-all duration-500"
                          style={{
                            width: `${(quest.progress / quest.maxProgress) * 100}%`,
                          }}
                        />
                      </div>
                      <div className="text-[10px] text-slate-500 text-right">
                        {quest.progress} / {quest.maxProgress}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </CelticFrame>
  );
};
