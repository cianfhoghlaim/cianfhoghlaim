import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { authClient } from '@/lib/client/auth-client';
import { useNavigate } from '@tanstack/react-router';
import type { User } from 'better-auth/types';

interface UserMenuProps {
  user: User;
}

export function UserMenu({ user }: UserMenuProps) {
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await authClient.signOut();
    navigate({ to: '/' });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring/20 rounded-full transition-all">
          {user.image ? (
            <img
              src={user.image}
              alt={user.name}
              className="w-9 h-9 rounded-full cursor-pointer hover:opacity-90 shadow-sm border border-white"
            />
          ) : (
            <div className="w-9 h-9 rounded-full bg-linear-to-br from-blue-500 to-indigo-600 flex items-center justify-center cursor-pointer hover:shadow-md transition-shadow text-white shadow-sm border border-white">
              <span className="font-semibold text-sm">
                {user.name?.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="w-56 rounded-xl border-border shadow-lg shadow-black/5 p-1"
      >
        <DropdownMenuLabel className="px-3 py-2">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-semibold text-foreground">{user.name}</p>
            <p className="text-xs text-muted-foreground font-medium">
              {user.email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-border my-1" />
        <DropdownMenuItem
          onClick={handleSignOut}
          className="rounded-lg text-red-600 focus:text-red-700 focus:bg-red-50 px-3 cursor-pointer"
        >
          Sign Out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
