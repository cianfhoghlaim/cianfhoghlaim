/**
 * Mythology Page with useInfiniteQuery
 *
 * Demonstrates paginated data fetching with TanStack Query
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { useState, useCallback } from 'react';
import {
  useCharacterSearch,
  useStorySearch,
  useFlattenedCharacters,
  useFlattenedStories,
  useTraditions,
  useCycles,
} from '../hooks/useMythologySearch';

export const Route = createFileRoute('/mythology')({
  component: MythologyPage,
});

function MythologyPage() {
  const [activeTab, setActiveTab] = useState<'characters' | 'stories'>('characters');
  const [selectedTradition, setSelectedTradition] = useState<string | undefined>();
  const [selectedCycle, setSelectedCycle] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch traditions and cycles
  const traditionsQuery = useTraditions();
  const cyclesQuery = useCycles(selectedTradition);

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-900 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <Link
            to="/"
            className="text-slate-400 hover:text-white flex items-center gap-2"
          >
            <BackIcon />
            Back to Home
          </Link>
        </div>

        <h1 className="text-4xl font-bold text-amber-300 mb-2">
          Celtic Mythology
        </h1>
        <p className="text-purple-200">
          Explore the legends, heroes, and gods of the Celtic world
        </p>
      </header>

      {/* Filters */}
      <div className="container mx-auto px-4 mb-8">
        <div className="bg-slate-800/50 rounded-xl p-4 flex flex-wrap gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="Search mythology..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Tradition Select */}
          <select
            value={selectedTradition || ''}
            onChange={(e) => {
              setSelectedTradition(e.target.value || undefined);
              setSelectedCycle(undefined);
            }}
            className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            <option value="">All Traditions</option>
            {traditionsQuery.data?.map((tradition) => (
              <option key={tradition.id} value={tradition.id}>
                {tradition.name}
              </option>
            ))}
          </select>

          {/* Cycle Select */}
          <select
            value={selectedCycle || ''}
            onChange={(e) => setSelectedCycle(e.target.value || undefined)}
            className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
            disabled={!cyclesQuery.data?.length}
          >
            <option value="">All Cycles</option>
            {cyclesQuery.data?.map((cycle) => (
              <option key={cycle.id} value={cycle.id}>
                {cycle.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className="container mx-auto px-4 mb-6">
        <div className="flex gap-4 border-b border-slate-700">
          <TabButton
            active={activeTab === 'characters'}
            onClick={() => setActiveTab('characters')}
          >
            Characters
          </TabButton>
          <TabButton
            active={activeTab === 'stories'}
            onClick={() => setActiveTab('stories')}
          >
            Stories
          </TabButton>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 pb-12">
        {activeTab === 'characters' ? (
          <CharactersTab
            query={searchQuery}
            tradition={selectedTradition}
            cycle={selectedCycle}
          />
        ) : (
          <StoriesTab
            query={searchQuery}
            tradition={selectedTradition}
            cycle={selectedCycle}
          />
        )}
      </div>
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

function TabButton({ active, onClick, children }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-3 font-medium transition-colors border-b-2 -mb-px ${
        active
          ? 'text-purple-300 border-purple-500'
          : 'text-slate-400 border-transparent hover:text-white'
      }`}
    >
      {children}
    </button>
  );
}

interface TabProps {
  query: string;
  tradition?: string;
  cycle?: string;
}

function CharactersTab({ query, tradition, cycle }: TabProps) {
  const searchResult = useCharacterSearch({
    query: query || undefined,
    tradition,
    cycle,
    pageSize: 12,
  });

  const characters = useFlattenedCharacters(searchResult);

  const {
    isFetching,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    error,
  } = searchResult;

  if (error) {
    return (
      <div className="text-red-400 text-center py-12">
        Error loading characters: {error.message}
      </div>
    );
  }

  return (
    <div>
      {/* Results Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {characters.map((character) => (
          <CharacterCard key={character.id} character={character} />
        ))}
      </div>

      {/* Loading indicator for initial load */}
      {isFetching && !isFetchingNextPage && characters.length === 0 && (
        <div className="text-center py-12">
          <LoadingSpinner />
          <p className="text-slate-400 mt-4">Loading characters...</p>
        </div>
      )}

      {/* Empty state */}
      {!isFetching && characters.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          No characters found matching your criteria.
        </div>
      )}

      {/* Load More Button */}
      {hasNextPage && (
        <div className="text-center mt-8">
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white rounded-lg transition-colors"
          >
            {isFetchingNextPage ? (
              <span className="flex items-center gap-2">
                <LoadingSpinner small />
                Loading more...
              </span>
            ) : (
              'Load More Characters'
            )}
          </button>
        </div>
      )}
    </div>
  );
}

function StoriesTab({ query, tradition, cycle }: TabProps) {
  const searchResult = useStorySearch({
    query: query || undefined,
    tradition,
    cycle,
    pageSize: 10,
  });

  const stories = useFlattenedStories(searchResult);

  const {
    isFetching,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    error,
  } = searchResult;

  if (error) {
    return (
      <div className="text-red-400 text-center py-12">
        Error loading stories: {error.message}
      </div>
    );
  }

  return (
    <div>
      {/* Results List */}
      <div className="space-y-6">
        {stories.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))}
      </div>

      {/* Loading indicator */}
      {isFetching && !isFetchingNextPage && stories.length === 0 && (
        <div className="text-center py-12">
          <LoadingSpinner />
          <p className="text-slate-400 mt-4">Loading stories...</p>
        </div>
      )}

      {/* Empty state */}
      {!isFetching && stories.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          No stories found matching your criteria.
        </div>
      )}

      {/* Load More Button */}
      {hasNextPage && (
        <div className="text-center mt-8">
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white rounded-lg transition-colors"
          >
            {isFetchingNextPage ? (
              <span className="flex items-center gap-2">
                <LoadingSpinner small />
                Loading more...
              </span>
            ) : (
              'Load More Stories'
            )}
          </button>
        </div>
      )}
    </div>
  );
}

interface CharacterCardProps {
  character: {
    id: string;
    name: string;
    nativeName: string;
    type: string;
    description: string;
    tradition: string;
    cycle: string;
    powers: string[];
  };
}

function CharacterCard({ character }: CharacterCardProps) {
  const typeColors: Record<string, string> = {
    deity: 'bg-amber-500',
    hero: 'bg-emerald-500',
    monster: 'bg-red-500',
    mortal: 'bg-blue-500',
    magical: 'bg-purple-500',
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700/80 transition-colors">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 bg-purple-700 rounded-full flex items-center justify-center text-xl font-bold text-white">
          {character.name.charAt(0)}
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-bold text-white">{character.name}</h3>
          <p className="text-purple-300 text-sm">{character.nativeName}</p>
        </div>
        <span
          className={`px-2 py-1 ${typeColors[character.type] || 'bg-slate-600'} rounded text-xs font-medium text-white capitalize`}
        >
          {character.type}
        </span>
      </div>

      <p className="text-slate-300 text-sm mb-4 line-clamp-2">
        {character.description}
      </p>

      {character.powers.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {character.powers.slice(0, 3).map((power) => (
            <span
              key={power}
              className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300"
            >
              {power}
            </span>
          ))}
        </div>
      )}

      <div className="flex justify-between text-xs text-slate-500">
        <span className="capitalize">{character.tradition.replace(/_/g, ' ')}</span>
        <span className="capitalize">{character.cycle.replace(/_/g, ' ')}</span>
      </div>
    </div>
  );
}

interface StoryCardProps {
  story: {
    id: string;
    title: string;
    englishTitle: string;
    tradition: string;
    cycle: string;
    summary: string;
    themes: string[];
    mainCharacters: string[];
    difficulty: string;
  };
}

function StoryCard({ story }: StoryCardProps) {
  const difficultyColors: Record<string, string> = {
    beginner: 'text-emerald-400 border-emerald-400',
    intermediate: 'text-amber-400 border-amber-400',
    advanced: 'text-red-400 border-red-400',
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700/80 transition-colors">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h3 className="text-xl font-bold text-white">{story.title}</h3>
          <p className="text-purple-300 text-sm">{story.englishTitle}</p>
        </div>
        <span
          className={`px-2 py-1 border rounded text-xs font-medium capitalize ${difficultyColors[story.difficulty] || ''}`}
        >
          {story.difficulty}
        </span>
      </div>

      <p className="text-slate-300 mb-4">{story.summary}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {story.themes.map((theme) => (
          <span
            key={theme}
            className="px-2 py-1 bg-purple-900/50 rounded-full text-xs text-purple-300"
          >
            {theme}
          </span>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-slate-500">Characters:</span>
        {story.mainCharacters.map((char) => (
          <span key={char} className="text-xs text-slate-400">
            {char}
          </span>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-700 flex justify-between text-xs text-slate-500">
        <span className="capitalize">{story.tradition.replace(/_/g, ' ')}</span>
        <span className="capitalize">{story.cycle.replace(/_/g, ' ')}</span>
      </div>
    </div>
  );
}

function LoadingSpinner({ small = false }: { small?: boolean }) {
  const size = small ? 'w-4 h-4' : 'w-8 h-8';
  return (
    <div
      className={`${size} border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto`}
    />
  );
}

function BackIcon() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M10 19l-7-7m0 0l7-7m-7 7h18"
      />
    </svg>
  );
}
