export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1">
        <section className="px-6 py-20 sm:px-10 md:px-16 lg:px-20">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight">
              Startup Idea Agent
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-black/70 dark:text-white/70">
              Buy one high‑quality, research‑backed startup idea each day for $1.
              Curated from real business changes in the world—delivered with market size,
              timing, and concrete first steps.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <a
                href="/idea-of-the-day"
                className="inline-flex items-center justify-center rounded-full bg-foreground text-background px-6 py-3 text-base font-medium hover:opacity-90 transition"
              >
                Get today’s idea — $1
              </a>
              <a
                href="#how-it-works"
                className="inline-flex items-center justify-center rounded-full border border-black/10 dark:border-white/20 px-6 py-3 text-base font-medium hover:bg-black/5 dark:hover:bg-white/10 transition"
              >
                How it works
              </a>
            </div>
            <p className="mt-3 text-sm text-black/50 dark:text-white/50">
              Secured by 402 payments. No accounts. No subscriptions. Instant delivery.
            </p>
          </div>
        </section>

        <section id="how-it-works" className="px-6 py-16 sm:px-10 md:px-16 lg:px-20">
          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl border border-black/10 dark:border-white/10">
              <h3 className="text-lg font-semibold">Curated signals</h3>
              <p className="mt-2 text-black/70 dark:text-white/70">
                We purchase curated business news focused on operational changes and emerging opportunities.
              </p>
            </div>
            <div className="p-6 rounded-2xl border border-black/10 dark:border-white/10">
              <h3 className="text-lg font-semibold">AI research & analysis</h3>
              <p className="mt-2 text-black/70 dark:text-white/70">
                Analyzes each signal to extract the opportunity, market size, why now, and concrete first steps.
              </p>
            </div>
            <div className="p-6 rounded-2xl border border-black/10 dark:border-white/10">
              <h3 className="text-lg font-semibold">Actionable idea</h3>
              <p className="mt-2 text-black/70 dark:text-white/70">
                Returns a single best idea with linked source article and a short plan you can execute today.
              </p>
            </div>
          </div>
        </section>

        <section className="px-6 pb-24 sm:px-10 md:px-16 lg:px-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-black/10 dark:border-white/10 px-4 py-2 text-xs uppercase tracking-wide">
              <span>Price</span>
              <span className="h-1 w-1 rounded-full bg-current" />
              <span>$1 per idea</span>
            </div>
            <h2 className="mt-6 text-2xl sm:text-3xl font-semibold">Own the day’s best idea</h2>
            <p className="mt-3 text-black/70 dark:text-white/70">
              No logins or emails. Pay, receive the idea instantly as JSON, and build.
            </p>
            <div className="mt-8">
              <a
                href="/idea-of-the-day"
                className="inline-flex items-center justify-center rounded-full bg-foreground text-background px-6 py-3 text-base font-medium hover:opacity-90 transition"
              >
                Buy today’s idea — $1
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="px-6 py-8 sm:px-10 md:px-16 lg:px-20 border-t border-black/10 dark:border-white/10">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-black/60 dark:text-white/60">
          <span>Startup Idea Agent</span>
          <span>Powered by 402 payments</span>
        </div>
      </footer>
    </div>
  );
}
