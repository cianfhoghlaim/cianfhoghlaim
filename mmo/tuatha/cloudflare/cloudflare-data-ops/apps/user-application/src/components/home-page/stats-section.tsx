import { Card, CardContent } from "@/components/ui/card";

const stats = [
  {
    number: "99.9%",
    label: "Uptime Guarantee",
    description: "Rock-solid reliability for your links",
  },
  {
    number: "< 100ms",
    label: "Average Response Time",
    description: "Lightning-fast redirects worldwide",
  },
  {
    number: "10,000+",
    label: "Businesses Protected",
    description: "Trusted by companies worldwide",
  },
  {
    number: "$2.3M",
    label: "Revenue Saved",
    description: "Protected from broken links this month",
  },
];

export function StatsSection() {
  return (
    <section className="py-16 bg-primary/5">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-4">
            Trusted by businesses worldwide
          </h2>
          <p className="text-muted-foreground">
            Join thousands of companies protecting their revenue with our
            platform
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <Card
              key={index}
              className="text-center bg-card/50 backdrop-blur border-0"
            >
              <CardContent className="pt-6">
                <div className="text-2xl sm:text-3xl font-bold text-primary mb-1">
                  {stat.number}
                </div>
                <div className="font-semibold text-sm mb-2">{stat.label}</div>
                <div className="text-xs text-muted-foreground">
                  {stat.description}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
