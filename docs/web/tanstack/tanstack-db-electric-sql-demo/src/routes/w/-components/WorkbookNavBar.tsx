import { UserMenu } from '@/components/UserMenu';
import { workbooksCollection } from '@/lib/client/collections';
import { useNavigate } from '@tanstack/react-router';
import type { User } from 'better-auth/types';
import { Pencil } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface WorkbookNavBarProps {
  user: User;
  workbook?: { id: string; name: string; createdAt: string };
}

export function WorkbookNavBar({ user, workbook }: WorkbookNavBarProps) {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(workbook?.name || '');
  const [isHovered, setIsHovered] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (workbook?.name) {
      setEditedName(workbook.name);
    }
  }, [workbook?.name]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSaveName = () => {
    if (workbook && editedName.trim() && editedName !== workbook.name) {
      workbooksCollection.update(workbook.id, (draft) => {
        draft.name = editedName.trim();
      });
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSaveName();
    } else if (e.key === 'Escape') {
      setEditedName(workbook?.name || '');
      setIsEditing(false);
    }
  };

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-border sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-4 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <button
              onClick={() => navigate({ to: '/dashboard' })}
              className="flex items-center justify-center p-1 -mr-2 text-muted-foreground hover:text-foreground transition-colors text-sm font-medium"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="m15 18-6-6 6-6" />
              </svg>
            </button>
            <div className="h-6 w-px bg-border"></div>
            <div
              className="relative group"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              {isEditing ? (
                <input
                  ref={inputRef}
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  onBlur={handleSaveName}
                  onKeyDown={handleKeyDown}
                  maxLength={48}
                  className="text-xl font-bold text-foreground tracking-tight bg-transparent border-b-2 border-blue-500 outline-none px-1 -mx-1"
                  style={{
                    width: `${Math.max(editedName.length * 12, 120)}px`,
                  }}
                />
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className={`text-xl font-bold text-foreground tracking-tight flex items-center gap-2 px-1 -mx-1 transition-all border-b-2 ${
                    isHovered ? 'border-border' : 'border-transparent'
                  }`}
                >
                  <span>{workbook?.name || 'Payoff Plan'}</span>
                  {isHovered && (
                    <Pencil className="w-4 h-4 text-muted-foreground" />
                  )}
                </button>
              )}
            </div>
          </div>
          <UserMenu user={user} />
        </div>
      </div>
    </nav>
  );
}
