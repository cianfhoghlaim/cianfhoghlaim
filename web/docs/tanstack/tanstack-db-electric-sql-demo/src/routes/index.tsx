import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { authClient, useSession } from '@/lib/client/auth-client';
import { Cloud, TrendingDown, Calendar } from 'lucide-react';
import { useEffect } from 'react';

export const Route = createFileRoute('/')({ component: LandingPage });

function LandingPage() {
  const navigate = useNavigate();
  const { data: session } = useSession();

  useEffect(() => {
    if (session) {
      navigate({ to: '/dashboard' });
    }
  }, [session, navigate]);

  const handleGoogleSignIn = async () => {
    await authClient.signIn.social({
      provider: 'google',
      callbackURL: '/dashboard',
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4 sm:p-6 font-sans text-foreground">
      <Card className="w-full max-w-4xl border-0 shadow-xl rounded-3xl overflow-hidden bg-card p-0 gap-0">
        {/* Hero Section */}
        <div className="p-10 sm:p-14 md:p-16 text-center flex flex-col items-center space-y-10">
          <div className="w-full max-w-lg space-y-10">
            {/* Logo */}
            <div className="flex justify-center">
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-green-500/20 transform rotate-3 transition-transform hover:rotate-6">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="w-8 h-8"
                >
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
              </div>
            </div>

            {/* Copy */}
            <div className="space-y-5">
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tighter text-foreground">
                Crush your debt.
              </h1>
              <p className="text-lg sm:text-xl text-muted-foreground leading-normal">
                The simple, powerful calculator to help you plan your payoff
                strategy and save thousands in interest.
              </p>
            </div>

            {/* Action */}
            <div className="space-y-4 pt-2">
              <Button
                onClick={handleGoogleSignIn}
                size="lg"
                className="w-full sm:w-auto sm:px-12 h-14 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 cursor-pointer"
              >
                <svg
                  className="mr-3 h-5 w-5"
                  aria-hidden="true"
                  focusable="false"
                  data-prefix="fab"
                  data-icon="google"
                  role="img"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 488 512"
                >
                  <path
                    fill="currentColor"
                    d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"
                  ></path>
                </svg>
                Sign in with Google
              </Button>
              <p className="text-xs text-muted-foreground">
                No credit card required.
              </p>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="bg-muted/30 border-t border-border/40 p-10 sm:p-14 md:p-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-12">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-12 h-12 bg-background rounded-xl flex items-center justify-center shadow-sm text-green-600 ring-1 ring-black/5">
                <TrendingDown className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-2">
                  Smart Strategies
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Compare Avalanche vs. Snowball to find your fastest debt-free
                  path.
                </p>
              </div>
            </div>

            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-12 h-12 bg-background rounded-xl flex items-center justify-center shadow-sm text-green-600 ring-1 ring-black/5">
                <Calendar className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-2">
                  Clear Timeline
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Visualize your progress with a clear payoff date and monthly
                  schedule.
                </p>
              </div>
            </div>

            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-12 h-12 bg-background rounded-xl flex items-center justify-center shadow-sm text-green-600 ring-1 ring-black/5">
                <Cloud className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-2">
                  Access Anywhere
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Securely save your plan to track your journey from any device.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
