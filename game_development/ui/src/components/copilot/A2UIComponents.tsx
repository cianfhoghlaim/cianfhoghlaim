/**
 * A2UI Generative UI Components
 *
 * Declarative components rendered from agent state
 */

import { useState } from 'react';
import type { RenderComponent } from '../../hooks/useCoAgent';

interface A2UIRendererProps {
  components: RenderComponent[];
  slot?: 'main' | 'sidebar' | 'overlay';
}

export function A2UIRenderer({ components, slot }: A2UIRendererProps) {
  const filteredComponents = slot
    ? components.filter((c) => c.slot === slot)
    : components;

  return (
    <div className="a2ui-container">
      {filteredComponents.map((component, index) => (
        <A2UIComponent key={`${component.component}-${index}`} {...component} />
      ))}
    </div>
  );
}

function A2UIComponent({ component, props }: RenderComponent) {
  switch (component) {
    case 'VocabularyCard':
      return <VocabularyCard {...props} />;
    case 'GrammarExplainer':
      return <GrammarExplainer {...props} />;
    case 'QuestProgress':
      return <QuestProgress {...props} />;
    case 'MapMarker':
      return <MapMarker {...props} />;
    case 'CharacterCard':
      return <CharacterCard {...props} />;
    case 'StoryTimeline':
      return <StoryTimeline {...props} />;
    default:
      return null;
  }
}

// Vocabulary Flashcard Component
interface VocabularyCardProps {
  language?: string;
  level?: string;
  topic?: string;
}

function VocabularyCard({
  language = 'ga',
  level = 'beginner',
  topic = 'greetings',
}: VocabularyCardProps) {
  const [flipped, setFlipped] = useState(false);

  const vocabulary: Record<string, { word: string; translation: string; audio?: string }[]> = {
    greetings: [
      { word: 'Dia duit', translation: 'Hello' },
      { word: 'Slán', translation: 'Goodbye' },
      { word: 'Go raibh maith agat', translation: 'Thank you' },
      { word: 'Fáilte', translation: 'Welcome' },
    ],
  };

  const words = vocabulary[topic] || vocabulary.greetings;
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentWord = words[currentIndex];

  const nextWord = () => {
    setCurrentIndex((i) => (i + 1) % words.length);
    setFlipped(false);
  };

  return (
    <div className="bg-emerald-900/30 border border-emerald-700 rounded-lg p-4">
      <div className="text-sm text-emerald-400 mb-2">
        Vocabulary - {topic.charAt(0).toUpperCase() + topic.slice(1)}
      </div>

      <div
        className="bg-slate-800 rounded-lg p-6 cursor-pointer min-h-[120px] flex items-center justify-center"
        onClick={() => setFlipped(!flipped)}
      >
        <div className="text-center">
          <div className="text-2xl font-bold text-white mb-2">
            {flipped ? currentWord.translation : currentWord.word}
          </div>
          <div className="text-sm text-slate-400">
            {flipped ? 'English' : 'Gaeilge'}
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center mt-4">
        <span className="text-sm text-slate-400">
          {currentIndex + 1} / {words.length}
        </span>
        <button
          onClick={nextWord}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm"
        >
          Next Word
        </button>
      </div>
    </div>
  );
}

// Grammar Explainer Component
interface GrammarExplainerProps {
  language?: string;
  topic?: string;
}

function GrammarExplainer({
  language = 'ga',
  topic = 'word_order',
}: GrammarExplainerProps) {
  const grammarTopics: Record<string, { title: string; explanation: string; examples: string[] }> = {
    word_order: {
      title: 'VSO Word Order',
      explanation:
        'Irish uses Verb-Subject-Object order, unlike English which uses Subject-Verb-Object.',
      examples: [
        'Tá mé ag léamh (I am reading) - literally "Is me at reading"',
        'Itheann sé úll (He eats an apple) - literally "Eats he apple"',
      ],
    },
    mutations: {
      title: 'Initial Mutations',
      explanation:
        'The first consonant of a word changes based on grammatical context.',
      examples: [
        'bean (woman) → an bhean (the woman) - séimhiú (lenition)',
        'cat (cat) → an cat (the cat) - no change (because c)',
      ],
    },
  };

  const grammar = grammarTopics[topic] || grammarTopics.word_order;

  return (
    <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
      <div className="text-sm text-blue-400 mb-2">Grammar Point</div>

      <h4 className="text-lg font-bold text-white mb-2">{grammar.title}</h4>

      <p className="text-slate-300 text-sm mb-4">{grammar.explanation}</p>

      <div className="space-y-2">
        {grammar.examples.map((example, i) => (
          <div
            key={i}
            className="bg-slate-800 rounded p-2 text-sm text-slate-200 font-mono"
          >
            {example}
          </div>
        ))}
      </div>
    </div>
  );
}

// Quest Progress Component
interface QuestProgressProps {
  questId?: string;
  currentStep?: number;
  totalSteps?: number;
}

function QuestProgress({
  questId = 'tutorial_greetings',
  currentStep = 1,
  totalSteps = 5,
}: QuestProgressProps) {
  const questNames: Record<string, string> = {
    tutorial_greetings: 'First Words',
    village_exploration: 'Explore the Village',
    meet_the_elder: 'Meet the Elder',
  };

  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="bg-amber-900/30 border border-amber-700 rounded-lg p-4">
      <div className="text-sm text-amber-400 mb-2">Quest Progress</div>

      <h4 className="text-lg font-bold text-amber-200 mb-2">
        {questNames[questId] || 'Unknown Quest'}
      </h4>

      <div className="mb-2">
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-amber-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="text-sm text-slate-300">
        Step {currentStep} of {totalSteps}
      </div>
    </div>
  );
}

// Map Marker Component
interface MapMarkerProps {
  zone?: string;
  target?: string;
}

function MapMarker({ zone = 'village_center', target = 'village_elder' }: MapMarkerProps) {
  const directions: Record<string, string> = {
    village_elder: 'Near the standing stones, by the central fire',
    blacksmith: 'East of the village square',
    market: 'South side of the village',
  };

  return (
    <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-4">
      <div className="text-sm text-purple-400 mb-2">Objective Marker</div>

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
          <MarkerIcon />
        </div>
        <div>
          <div className="text-white font-medium capitalize">
            {target.replace(/_/g, ' ')}
          </div>
          <div className="text-sm text-slate-400">
            {directions[target] || zone.replace(/_/g, ' ')}
          </div>
        </div>
      </div>
    </div>
  );
}

function MarkerIcon() {
  return (
    <svg
      className="w-5 h-5 text-white"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
      />
    </svg>
  );
}

// Character Card Component
interface CharacterCardProps {
  character?: string;
  tradition?: string;
  showRelationships?: boolean;
}

function CharacterCard({
  character = 'lugh',
  tradition = 'irish_mythology',
  showRelationships = false,
}: CharacterCardProps) {
  const characters: Record<string, {
    name: string;
    title: string;
    description: string;
    relationships?: string[];
  }> = {
    lugh: {
      name: 'Lugh Lámhfhada',
      title: 'The Long-Armed One',
      description: 'Master of all arts, wielder of the Spear of Victory',
      relationships: ['Cian (father)', 'Balor (grandfather)', 'Nuada (king)'],
    },
    cu_chulainn: {
      name: 'Cú Chulainn',
      title: 'The Hound of Ulster',
      description: 'Greatest warrior of the Red Branch Knights',
      relationships: ['Emer (wife)', 'Scáthach (teacher)', 'Lugh (father)'],
    },
  };

  const char = characters[character] || characters.lugh;

  return (
    <div className="bg-rose-900/30 border border-rose-700 rounded-lg p-4">
      <div className="text-sm text-rose-400 mb-2">Character Lore</div>

      <div className="flex items-start gap-3">
        <div className="w-12 h-12 bg-rose-700 rounded-full flex items-center justify-center text-xl">
          {char.name.charAt(0)}
        </div>
        <div className="flex-1">
          <h4 className="text-lg font-bold text-white">{char.name}</h4>
          <div className="text-sm text-rose-300">{char.title}</div>
        </div>
      </div>

      <p className="text-slate-300 text-sm mt-3">{char.description}</p>

      {showRelationships && char.relationships && (
        <div className="mt-3 pt-3 border-t border-rose-700/50">
          <div className="text-xs text-rose-400 mb-1">Relationships</div>
          <div className="flex flex-wrap gap-1">
            {char.relationships.map((rel, i) => (
              <span
                key={i}
                className="px-2 py-0.5 bg-rose-800/50 rounded text-xs text-rose-200"
              >
                {rel}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Story Timeline Component
interface StoryTimelineProps {
  cycle?: string;
  highlight?: string;
}

function StoryTimeline({
  cycle = 'mythological_cycle',
  highlight = 'four_treasures',
}: StoryTimelineProps) {
  const stories: Record<string, { title: string; events: string[] }> = {
    mythological_cycle: {
      title: 'Mythological Cycle',
      events: [
        'Arrival of the Tuatha Dé Danann',
        'The Four Treasures brought to Ireland',
        'Battle of Mag Tuired (First)',
        'Battle of Mag Tuired (Second)',
        'Arrival of the Milesians',
      ],
    },
    ulster_cycle: {
      title: 'Ulster Cycle',
      events: [
        'Birth of Cú Chulainn',
        'Training with Scáthach',
        'Táin Bó Cúailnge',
        'Death of Cú Chulainn',
      ],
    },
  };

  const story = stories[cycle] || stories.mythological_cycle;

  return (
    <div className="bg-indigo-900/30 border border-indigo-700 rounded-lg p-4">
      <div className="text-sm text-indigo-400 mb-2">{story.title}</div>

      <div className="relative">
        <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-indigo-700" />

        <div className="space-y-3">
          {story.events.map((event, i) => (
            <div key={i} className="flex items-start gap-3">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold z-10 ${
                  event.toLowerCase().includes(highlight.replace(/_/g, ' '))
                    ? 'bg-indigo-500 text-white'
                    : 'bg-slate-700 text-slate-300'
                }`}
              >
                {i + 1}
              </div>
              <div
                className={`text-sm ${
                  event.toLowerCase().includes(highlight.replace(/_/g, ' '))
                    ? 'text-indigo-200 font-medium'
                    : 'text-slate-400'
                }`}
              >
                {event}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// XP Indicator Component
interface XPIndicatorProps {
  xp: number;
  vocabularyCount: number;
}

export function XPIndicator({ xp, vocabularyCount }: XPIndicatorProps) {
  return (
    <div className="flex items-center gap-4 p-2 bg-slate-800 rounded-lg">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center">
          <StarIcon />
        </div>
        <div>
          <div className="text-xs text-slate-400">XP</div>
          <div className="text-lg font-bold text-amber-300">{xp}</div>
        </div>
      </div>

      <div className="h-8 w-px bg-slate-700" />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
          <BookIcon />
        </div>
        <div>
          <div className="text-xs text-slate-400">Words</div>
          <div className="text-lg font-bold text-emerald-300">{vocabularyCount}</div>
        </div>
      </div>
    </div>
  );
}

function StarIcon() {
  return (
    <svg
      className="w-4 h-4 text-white"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
    </svg>
  );
}

function BookIcon() {
  return (
    <svg
      className="w-4 h-4 text-white"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
      />
    </svg>
  );
}

// Tool Call Indicator Component
interface ToolCallIndicatorProps {
  toolName: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  parameters?: Record<string, unknown>;
}

export function ToolCallIndicator({
  toolName,
  status,
  parameters,
}: ToolCallIndicatorProps) {
  const statusColors = {
    pending: 'bg-slate-500',
    running: 'bg-amber-500 animate-pulse',
    complete: 'bg-emerald-500',
    error: 'bg-red-500',
  };

  return (
    <div className="flex items-center gap-2 p-2 bg-slate-800/50 rounded text-sm">
      <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      <span className="text-slate-300 font-mono">{toolName}</span>
      {parameters && (
        <span className="text-slate-500 text-xs">
          ({Object.keys(parameters).join(', ')})
        </span>
      )}
    </div>
  );
}
