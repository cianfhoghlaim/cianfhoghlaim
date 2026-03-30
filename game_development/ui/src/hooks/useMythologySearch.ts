/**
 * useMythologySearch - Infinite query hooks for mythology data
 *
 * Uses TanStack Query's useInfiniteQuery for paginated mythology content
 */

import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import {
  searchCharacters,
  searchStories,
  searchLocations,
  getCharacterById,
  getTraditions,
  getCycles,
  type MythologyCharacter,
  type MythologyStory,
  type MythologyLocation,
  type MythologySearchResult,
} from '../server/mythology';

interface UseSearchOptions {
  query?: string;
  tradition?: string;
  cycle?: string;
  pageSize?: number;
  enabled?: boolean;
}

// Characters
export function useCharacterSearch({
  query,
  tradition,
  cycle,
  pageSize = 20,
  enabled = true,
}: UseSearchOptions = {}) {
  return useInfiniteQuery<MythologySearchResult<MythologyCharacter>, Error>({
    queryKey: ['mythology', 'characters', { query, tradition, cycle, pageSize }],
    queryFn: async ({ pageParam }) => {
      return searchCharacters({
        data: {
          query,
          tradition,
          cycle,
          page: pageParam as number,
          pageSize,
        },
      });
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.hasMore) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled,
  });
}

export function useCharacter(id: string | undefined) {
  return useQuery<MythologyCharacter | null, Error>({
    queryKey: ['mythology', 'character', id],
    queryFn: async () => {
      if (!id) return null;
      return getCharacterById({ data: { id } });
    },
    enabled: !!id,
  });
}

// Stories
export function useStorySearch({
  query,
  tradition,
  cycle,
  pageSize = 20,
  enabled = true,
}: UseSearchOptions = {}) {
  return useInfiniteQuery<MythologySearchResult<MythologyStory>, Error>({
    queryKey: ['mythology', 'stories', { query, tradition, cycle, pageSize }],
    queryFn: async ({ pageParam }) => {
      return searchStories({
        data: {
          query,
          tradition,
          cycle,
          page: pageParam as number,
          pageSize,
        },
      });
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.hasMore) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled,
  });
}

// Locations
export function useLocationSearch({
  query,
  tradition,
  pageSize = 20,
  enabled = true,
}: Omit<UseSearchOptions, 'cycle'> = {}) {
  return useInfiniteQuery<MythologySearchResult<MythologyLocation>, Error>({
    queryKey: ['mythology', 'locations', { query, tradition, pageSize }],
    queryFn: async ({ pageParam }) => {
      return searchLocations({
        data: {
          query,
          tradition,
          page: pageParam as number,
          pageSize,
        },
      });
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.hasMore) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled,
  });
}

// Metadata
export function useTraditions() {
  return useQuery({
    queryKey: ['mythology', 'traditions'],
    queryFn: async () => {
      return getTraditions();
    },
    staleTime: 1000 * 60 * 60, // 1 hour - traditions rarely change
  });
}

export function useCycles(tradition?: string) {
  return useQuery({
    queryKey: ['mythology', 'cycles', tradition],
    queryFn: async () => {
      return getCycles({ data: { tradition } });
    },
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

// Utility functions
export function useFlattenedCharacters(
  queryResult: ReturnType<typeof useCharacterSearch>
): MythologyCharacter[] {
  const { data } = queryResult;
  if (!data) return [];
  return data.pages.flatMap((page) => page.items);
}

export function useFlattenedStories(
  queryResult: ReturnType<typeof useStorySearch>
): MythologyStory[] {
  const { data } = queryResult;
  if (!data) return [];
  return data.pages.flatMap((page) => page.items);
}

export function useFlattenedLocations(
  queryResult: ReturnType<typeof useLocationSearch>
): MythologyLocation[] {
  const { data } = queryResult;
  if (!data) return [];
  return data.pages.flatMap((page) => page.items);
}

// Prefetch functions for SSR
export async function prefetchCharacters(
  queryClient: ReturnType<typeof import('@tanstack/react-query').useQueryClient>,
  options: UseSearchOptions
) {
  await queryClient.prefetchInfiniteQuery({
    queryKey: [
      'mythology',
      'characters',
      {
        query: options.query,
        tradition: options.tradition,
        cycle: options.cycle,
        pageSize: options.pageSize || 20,
      },
    ],
    queryFn: async () => {
      return searchCharacters({
        data: {
          query: options.query,
          tradition: options.tradition,
          cycle: options.cycle,
          page: 1,
          pageSize: options.pageSize || 20,
        },
      });
    },
    initialPageParam: 1,
  });
}

export async function prefetchStories(
  queryClient: ReturnType<typeof import('@tanstack/react-query').useQueryClient>,
  options: UseSearchOptions
) {
  await queryClient.prefetchInfiniteQuery({
    queryKey: [
      'mythology',
      'stories',
      {
        query: options.query,
        tradition: options.tradition,
        cycle: options.cycle,
        pageSize: options.pageSize || 20,
      },
    ],
    queryFn: async () => {
      return searchStories({
        data: {
          query: options.query,
          tradition: options.tradition,
          cycle: options.cycle,
          page: 1,
          pageSize: options.pageSize || 20,
        },
      });
    },
    initialPageParam: 1,
  });
}
