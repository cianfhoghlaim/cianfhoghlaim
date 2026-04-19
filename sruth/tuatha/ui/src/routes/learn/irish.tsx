/**
 * Irish language learning page
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/learn/irish')({
  component: LearnIrishPage,
});

function LearnIrishPage() {
  const [activeTab, setActiveTab] = useState<'lessons' | 'vocabulary' | 'grammar' | 'practice'>('lessons');

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/80 border-b border-emerald-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-amber-300">Learn Irish</h1>
              <p className="text-emerald-300">Foghlaim Gaeilge</p>
            </div>
            <Link
              to="/"
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded"
            >
              ← Back
            </Link>
          </div>

          {/* Tabs */}
          <nav className="flex gap-2 mt-4">
            {(['lessons', 'vocabulary', 'grammar', 'practice'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-t font-medium transition-colors ${
                  activeTab === tab
                    ? 'bg-emerald-700 text-white'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'lessons' && <LessonsTab />}
        {activeTab === 'vocabulary' && <VocabularyTab />}
        {activeTab === 'grammar' && <GrammarTab />}
        {activeTab === 'practice' && <PracticeTab />}
      </main>
    </div>
  );
}

function LessonsTab() {
  const lessons = [
    {
      id: 1,
      title: 'Greetings & Introductions',
      nativeTitle: 'Beannachtaí & Cur in Aithne',
      level: 'Beginner',
      duration: '15 min',
      progress: 100,
    },
    {
      id: 2,
      title: 'Numbers 1-20',
      nativeTitle: 'Uimhreacha 1-20',
      level: 'Beginner',
      duration: '20 min',
      progress: 60,
    },
    {
      id: 3,
      title: 'Family Members',
      nativeTitle: 'Baill an Teaghlaigh',
      level: 'Beginner',
      duration: '25 min',
      progress: 0,
    },
    {
      id: 4,
      title: 'Present Tense Verbs',
      nativeTitle: 'An Aimsir Láithreach',
      level: 'Elementary',
      duration: '30 min',
      progress: 0,
    },
  ];

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {lessons.map((lesson) => (
        <div
          key={lesson.id}
          className="bg-slate-800/50 border border-emerald-700/50 rounded-lg p-4 hover:border-emerald-500 transition-colors"
        >
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-bold text-white">{lesson.title}</h3>
              <p className="text-amber-300 text-sm">{lesson.nativeTitle}</p>
            </div>
            <span className="text-xs px-2 py-1 bg-emerald-700 text-emerald-100 rounded">
              {lesson.level}
            </span>
          </div>
          <div className="flex items-center justify-between mt-4">
            <span className="text-sm text-slate-400">{lesson.duration}</span>
            <div className="flex items-center gap-2">
              <div className="w-24 h-2 bg-slate-700 rounded-full">
                <div
                  className="h-full bg-emerald-500 rounded-full"
                  style={{ width: `${lesson.progress}%` }}
                />
              </div>
              <span className="text-xs text-slate-400">{lesson.progress}%</span>
            </div>
          </div>
          <button className="mt-3 w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium">
            {lesson.progress === 0 ? 'Start' : lesson.progress === 100 ? 'Review' : 'Continue'}
          </button>
        </div>
      ))}
    </div>
  );
}

function VocabularyTab() {
  const vocabulary = [
    { word: 'Dia duit', pronunciation: 'DEE-ah gwit', meaning: 'Hello', category: 'Greetings' },
    { word: 'Slán', pronunciation: 'slawn', meaning: 'Goodbye', category: 'Greetings' },
    { word: 'Go raibh maith agat', pronunciation: 'guh rev mah ah-gut', meaning: 'Thank you', category: 'Phrases' },
    { word: 'Tá', pronunciation: 'taw', meaning: 'Yes/Is', category: 'Basic' },
    { word: 'Níl', pronunciation: 'neel', meaning: 'No/Is not', category: 'Basic' },
    { word: 'Conas atá tú?', pronunciation: 'KUN-us ah-TAW too', meaning: 'How are you?', category: 'Phrases' },
  ];

  return (
    <div className="bg-slate-800/50 rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-slate-700">
          <tr>
            <th className="text-left px-4 py-3 text-amber-300">Irish</th>
            <th className="text-left px-4 py-3 text-slate-300">Pronunciation</th>
            <th className="text-left px-4 py-3 text-slate-300">English</th>
            <th className="text-left px-4 py-3 text-slate-300">Category</th>
          </tr>
        </thead>
        <tbody>
          {vocabulary.map((item, index) => (
            <tr key={index} className="border-t border-slate-700 hover:bg-slate-700/30">
              <td className="px-4 py-3 font-medium text-white">{item.word}</td>
              <td className="px-4 py-3 text-emerald-300 text-sm">{item.pronunciation}</td>
              <td className="px-4 py-3 text-slate-300">{item.meaning}</td>
              <td className="px-4 py-3 text-slate-400 text-sm">{item.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GrammarTab() {
  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 border border-emerald-700/50 rounded-lg p-6">
        <h3 className="text-xl font-bold text-amber-300 mb-4">Initial Mutations (Na hAthruithe Tosaigh)</h3>
        <p className="text-slate-300 mb-4">
          Irish has two main types of initial consonant mutations: lenition (séimhiú) and eclipsis (urú).
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-slate-700/50 rounded p-4">
            <h4 className="font-bold text-emerald-300 mb-2">Séimhiú (Lenition)</h4>
            <p className="text-sm text-slate-400 mb-2">Adds 'h' after the consonant</p>
            <ul className="text-sm space-y-1">
              <li><span className="text-white">b → bh</span> <span className="text-slate-400">(bád → a bhád)</span></li>
              <li><span className="text-white">c → ch</span> <span className="text-slate-400">(cat → a chat)</span></li>
              <li><span className="text-white">d → dh</span> <span className="text-slate-400">(doras → a dhoras)</span></li>
            </ul>
          </div>

          <div className="bg-slate-700/50 rounded p-4">
            <h4 className="font-bold text-purple-300 mb-2">Urú (Eclipsis)</h4>
            <p className="text-sm text-slate-400 mb-2">Adds a letter before the consonant</p>
            <ul className="text-sm space-y-1">
              <li><span className="text-white">b → mb</span> <span className="text-slate-400">(bád → ar mbád)</span></li>
              <li><span className="text-white">c → gc</span> <span className="text-slate-400">(cat → ár gcat)</span></li>
              <li><span className="text-white">d → nd</span> <span className="text-slate-400">(doras → ár ndoras)</span></li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 border border-emerald-700/50 rounded-lg p-6">
        <h3 className="text-xl font-bold text-amber-300 mb-4">Word Order (Ord na bhFocal)</h3>
        <p className="text-slate-300 mb-4">
          Irish uses Verb-Subject-Object (VSO) word order, unlike English which uses SVO.
        </p>
        <div className="bg-slate-700/50 rounded p-4">
          <p className="text-emerald-300 font-medium">Léann Seán an leabhar</p>
          <p className="text-slate-400 text-sm">Reads Seán the book</p>
          <p className="text-white mt-2">"Seán reads the book"</p>
        </div>
      </div>
    </div>
  );
}

function PracticeTab() {
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleSubmit = () => {
    if (answer.toLowerCase().includes('dia duit') || answer.toLowerCase().includes('dia is muire duit')) {
      setFeedback('Maith thú! (Well done!) Correct!');
    } else {
      setFeedback('Try again! Hint: The greeting starts with "Dia..."');
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="bg-slate-800/50 border border-emerald-700/50 rounded-lg p-6">
        <h3 className="text-xl font-bold text-amber-300 mb-4">Practice Exercise</h3>

        <div className="mb-6">
          <p className="text-slate-300 mb-2">Translate to Irish:</p>
          <p className="text-2xl text-white font-medium">"Hello" (formal greeting)</p>
        </div>

        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your answer in Irish..."
          className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500 mb-4"
        />

        <button
          onClick={handleSubmit}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium"
        >
          Check Answer
        </button>

        {feedback && (
          <div className={`mt-4 p-3 rounded ${
            feedback.includes('Correct') ? 'bg-emerald-900/50 text-emerald-300' : 'bg-amber-900/50 text-amber-300'
          }`}>
            {feedback}
          </div>
        )}
      </div>
    </div>
  );
}
