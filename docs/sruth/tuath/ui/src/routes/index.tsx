/**
 * Tuath - Celtic Educational MMO
 * Landing page with language selection and game entry
 */

import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-900 via-emerald-800 to-slate-900">
      {/* Hero Section */}
      <header className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-6xl font-bold text-amber-300 mb-4">
          Tuath
        </h1>
        <p className="text-2xl text-emerald-100 mb-2">
          Fáilte go Tuath • Fàilte gu Tuath • Croeso i Tuath
        </p>
        <p className="text-lg text-emerald-200">
          Learn Celtic Languages Through Mythology and Adventure
        </p>
      </header>

      {/* Language Selection */}
      <section className="container mx-auto px-4 py-12">
        <h2 className="text-3xl font-bold text-amber-200 text-center mb-8">
          Choose Your Path
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {/* Irish */}
          <LanguageCard
            language="Irish"
            nativeName="Gaeilge"
            greeting="Dia duit!"
            description="Explore the myths of the Tuatha Dé Danann and the Fianna warriors."
            href="/learn/irish"
            color="emerald"
          />

          {/* Scottish Gaelic */}
          <LanguageCard
            language="Scottish Gaelic"
            nativeName="Gàidhlig"
            greeting="Halò!"
            description="Journey through the Highlands and Hebridean isles."
            href="/learn/gaelic"
            color="blue"
          />

          {/* Welsh */}
          <LanguageCard
            language="Welsh"
            nativeName="Cymraeg"
            greeting="Shwmae!"
            description="Discover the tales of the Mabinogion and ancient Cymru."
            href="/learn/welsh"
            color="red"
          />
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
          <FeatureCard
            icon="🎮"
            title="Play & Learn"
            description="Educational quests tied to real curriculum"
          />
          <FeatureCard
            icon="🐉"
            title="Mythology"
            description="Interact with legendary Celtic characters"
          />
          <FeatureCard
            icon="🗺️"
            title="Explore"
            description="Visit Gaeltacht and Celtic-speaking regions"
          />
          <FeatureCard
            icon="💬"
            title="AI Tutor"
            description="Personalized language learning assistance"
          />
        </div>
      </section>

      {/* Quick Actions */}
      <section className="container mx-auto px-4 py-12 text-center">
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/game"
            className="px-8 py-4 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-lg transition-colors"
          >
            Enter the Game World
          </Link>
          <Link
            to="/map"
            className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg transition-colors"
          >
            Explore Celtic Map
          </Link>
          <Link
            to="/mythology"
            className="px-8 py-4 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition-colors"
          >
            Discover Mythology
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center text-emerald-300">
        <p>Go n-éirí an t-ádh leat! • Gun soirbhich leat! • Pob lwc!</p>
        <p className="text-sm mt-2 text-emerald-400">(Good luck in Irish, Scottish Gaelic, and Welsh)</p>
      </footer>
    </div>
  );
}

interface LanguageCardProps {
  language: string;
  nativeName: string;
  greeting: string;
  description: string;
  href: string;
  color: 'emerald' | 'blue' | 'red';
}

function LanguageCard({ language, nativeName, greeting, description, href, color }: LanguageCardProps) {
  const colorClasses = {
    emerald: 'border-emerald-400 hover:bg-emerald-800/50',
    blue: 'border-blue-400 hover:bg-blue-800/50',
    red: 'border-red-400 hover:bg-red-800/50',
  };

  return (
    <Link
      to={href}
      className={`block p-6 border-2 ${colorClasses[color]} rounded-xl bg-slate-800/50 transition-colors`}
    >
      <h3 className="text-2xl font-bold text-white mb-1">{language}</h3>
      <p className="text-amber-300 mb-2">{nativeName}</p>
      <p className="text-xl text-emerald-300 mb-4">"{greeting}"</p>
      <p className="text-slate-300 text-sm">{description}</p>
    </Link>
  );
}

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="p-4 bg-slate-800/50 rounded-lg text-center">
      <div className="text-4xl mb-2">{icon}</div>
      <h4 className="font-bold text-amber-200 mb-1">{title}</h4>
      <p className="text-sm text-slate-300">{description}</p>
    </div>
  );
}
