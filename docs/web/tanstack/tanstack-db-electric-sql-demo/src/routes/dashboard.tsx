import { Card, CardTitle } from '@/components/ui/card';
import { UserMenu } from '@/components/UserMenu';
import { WorkbookCard } from '@/components/WorkbookCard';
import { useSession } from '@/lib/client/auth-client';
import { workbooksCollection } from '@/lib/client/collections';
import { useLiveQuery } from '@tanstack/react-db';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Plus } from 'lucide-react';
import { useEffect } from 'react';
import { v7 as uuidv7 } from 'uuid';

export const Route = createFileRoute('/dashboard')({
  ssr: false,
  component: Dashboard,
});

function Dashboard() {
  const navigate = useNavigate();
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending && !session) {
      navigate({ to: '/' });
    }
  }, [session, isPending, navigate]);

  const { data: workbooks } = useLiveQuery((q) =>
    q
      .from({ workbook: workbooksCollection })
      .orderBy(({ workbook }) => workbook.updatedAt, 'desc'),
  );

  const handleCreateWorkbook = async () => {
    const id = uuidv7();
    workbooksCollection.insert({
      id: id,
      name: 'My Workbook',
      monthlyPayment: '0',
      strategy: 'avalanche',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    navigate({ to: '/w/$id', params: { id }, reloadDocument: true });
  };

  if (isPending) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <p className="text-gray-600 text-xl">Loading...</p>
      </div>
    );
  }

  if (!session?.user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Abstract Background Hotspots */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top Left - Green */}
        <div className="absolute -top-[20%] -left-[10%] w-[70%] h-[70%] rounded-full bg-green-500/10 blur-[120px]" />

        {/* Top Right - Green */}
        <div className="absolute -top-[10%] -right-[10%] w-[60%] h-[60%] rounded-full bg-green-500/5 blur-[100px]" />

        {/* Center/Bottom - Subtle Green */}
        <div className="absolute top-[10%] left-[20%] w-[50%] h-[50%] rounded-full bg-green-500/10 blur-[140px]" />
      </div>

      {/* Navigation Bar */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-border sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-4 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-foreground tracking-tight">
              Debt Payoff Calculator
            </h1>
            <UserMenu user={session.user} />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 relative z-10">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            Your Workbooks
          </h2>
          <p className="text-muted-foreground">
            Manage your debt payoff strategies with workbooks
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {workbooks.map((workbook) => (
            <WorkbookCard key={workbook.id} workbook={workbook} />
          ))}

          {/* New Workbook Button */}
          <Card
            className="cursor-pointer hover:shadow-lg transition-all border-2 border-dashed border-border bg-muted/30 hover:bg-muted/50 hover:border-muted-foreground/50 flex items-center justify-center"
            onClick={handleCreateWorkbook}
          >
            <div className="flex flex-col items-center gap-3 p-4">
              <div className="p-3 bg-muted/50 rounded-lg">
                <Plus className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="text-center">
                <CardTitle className="text-lg text-muted-foreground">
                  New Workbook
                </CardTitle>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
