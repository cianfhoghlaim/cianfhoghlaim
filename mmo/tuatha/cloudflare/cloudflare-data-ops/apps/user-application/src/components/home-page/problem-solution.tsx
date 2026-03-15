import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  AlertTriangle,
  TrendingDown,
  DollarSign,
  CheckCircle,
  TrendingUp,
  Shield,
} from "lucide-react";

export function ProblemSolution() {
  return (
    <section className="py-20 sm:py-28">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Problem Side */}
          <div>
            <Badge variant="destructive" className="mb-4 px-3 py-1">
              The Problem
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-6">
              Broken Links = Lost Revenue
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Every day, businesses lose thousands of dollars because their
              links stop working. Product pages go offline, domains expire, and
              redirect chains break—leaving customers frustrated and revenue
              flowing to competitors.
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">27% Revenue Loss</h3>
                  <p className="text-sm text-muted-foreground">
                    Average revenue lost due to broken affiliate and marketing
                    links
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <TrendingDown className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">Poor User Experience</h3>
                  <p className="text-sm text-muted-foreground">
                    Dead links damage trust and drive customers to competitors
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <DollarSign className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">Hidden Costs</h3>
                  <p className="text-sm text-muted-foreground">
                    Manual link checking wastes time and still misses critical
                    failures
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Solution Side */}
          <div>
            <Badge className="mb-4 px-3 py-1">The Solution</Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-6">
              AI-Powered Link Protection
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Our intelligent platform continuously monitors your links,
              automatically detects failures, and keeps your revenue flowing
              with smart backup routing and instant alerts.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">24/7 AI Monitoring</h3>
                  <p className="text-sm text-muted-foreground">
                    Continuous monitoring catches broken links within minutes,
                    not days
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">Smart Backup Routing</h3>
                  <p className="text-sm text-muted-foreground">
                    Automatically route traffic to backup destinations when
                    primary links fail
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">Revenue Recovery</h3>
                  <p className="text-sm text-muted-foreground">
                    Convert failed clicks into sales with intelligent fallback
                    strategies
                  </p>
                </div>
              </div>
            </div>

            <Button size="lg" className="w-full sm:w-auto">
              Start Protecting Your Revenue
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
