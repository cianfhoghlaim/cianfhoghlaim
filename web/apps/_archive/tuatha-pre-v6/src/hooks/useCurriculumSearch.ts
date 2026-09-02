/**
 * useCurriculumSearch - Infinite query hook for curriculum data
 *
 * Uses TanStack Query's useInfiniteQuery for paginated curriculum search
 */

import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import {
  searchCurriculum,
  getCurriculumById,
  getCurriculumLevels,
  getCurriculumSubjects,
  type CurriculumItem,
  type CurriculumSearchResult,
} from '../server/curriculum';

interface UseCurriculumSearchOptions {
  query?: string;
  nation?: 'ireland' | 'wales' | 'scotland' | 'all';
  level?: string;
  subject?: string;
  pageSize?: number;
  enabled?: boolean;
}

export function useCurriculumSearch({
  query,
  nation = 'all',
  level,
  subject,
  pageSize = 20,
  enabled = true,
}: UseCurriculumSearchOptions = {}) {
  return useInfiniteQuery<CurriculumSearchResult, Error>({
    queryKey: ['curriculum', 'search', { query, nation, level, subject, pageSize }],
    queryFn: async ({ pageParam }) => {
      const result = await searchCurriculum({
        data: {
          query,
          nation,
          level,
          subject,
          page: pageParam as number,
          pageSize,
        },
      });
      return result;
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

export function useCurriculumItem(id: string | undefined) {
  return useQuery<CurriculumItem | null, Error>({
    queryKey: ['curriculum', 'item', id],
    queryFn: async () => {
      if (!id) return null;
      return getCurriculumById({ data: { id } });
    },
    enabled: !!id,
  });
}

export function useCurriculumLevels(nation?: string) {
  return useQuery<string[], Error>({
    queryKey: ['curriculum', 'levels', nation],
    queryFn: async () => {
      return getCurriculumLevels({ data: { nation } });
    },
  });
}

export function useCurriculumSubjects(nation?: string) {
  return useQuery<string[], Error>({
    queryKey: ['curriculum', 'subjects', nation],
    queryFn: async () => {
      return getCurriculumSubjects({ data: { nation } });
    },
  });
}

// Utility hook for flattening infinite query pages
export function useFlattenedCurriculumItems(
  queryResult: ReturnType<typeof useCurriculumSearch>
): CurriculumItem[] {
  const { data } = queryResult;

  if (!data) return [];

  return data.pages.flatMap((page) => page.items);
}

// Prefetch curriculum data for faster navigation
export async function prefetchCurriculumSearch(
  queryClient: ReturnType<typeof import('@tanstack/react-query').useQueryClient>,
  options: UseCurriculumSearchOptions
) {
  await queryClient.prefetchInfiniteQuery({
    queryKey: [
      'curriculum',
      'search',
      {
        query: options.query,
        nation: options.nation || 'all',
        level: options.level,
        subject: options.subject,
        pageSize: options.pageSize || 20,
      },
    ],
    queryFn: async () => {
      return searchCurriculum({
        data: {
          query: options.query,
          nation: options.nation || 'all',
          level: options.level,
          subject: options.subject,
          page: 1,
          pageSize: options.pageSize || 20,
        },
      });
    },
    initialPageParam: 1,
  });
}
