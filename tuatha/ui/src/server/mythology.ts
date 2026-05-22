/**
 * Mythology Server Functions
 *
 * TanStack Start server functions for Celtic mythology data
 */

import { createServerFn } from '@tanstack/react-start';
import { z } from 'zod';

// Types
export interface MythologyCharacter {
  id: string;
  name: string;
  nativeName: string;
  tradition: string;
  cycle: string;
  type: 'deity' | 'hero' | 'monster' | 'mortal' | 'magical';
  description: string;
  powers: string[];
  relationships: string[];
  imageUrl?: string;
}

export interface MythologyStory {
  id: string;
  title: string;
  englishTitle: string;
  tradition: string;
  cycle: string;
  summary: string;
  themes: string[];
  mainCharacters: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

export interface MythologyLocation {
  id: string;
  name: string;
  englishName: string;
  tradition: string;
  type: 'otherworld' | 'fortress' | 'sacred_site' | 'battlefield' | 'natural';
  description: string;
  latitude?: number;
  longitude?: number;
  associatedStories: string[];
}

export interface MythologySearchResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
  nextCursor?: string;
}

// Validation schemas
const searchSchema = z.object({
  query: z.string().optional(),
  tradition: z.string().optional(),
  cycle: z.string().optional(),
  page: z.number().min(1).default(1),
  pageSize: z.number().min(1).max(50).default(20),
  cursor: z.string().optional(),
});

const byIdSchema = z.object({
  id: z.string(),
});

// Characters
export const searchCharacters = createServerFn({
  method: 'GET',
})
  .validator((input: unknown) => searchSchema.parse(input))
  .handler(async ({ data }): Promise<MythologySearchResult<MythologyCharacter>> => {
    const { query, tradition, cycle, page, pageSize } = data;

    const apiUrl = process.env.API_URL || 'http://localhost:8000';

    try {
      const params = new URLSearchParams();
      if (query) params.set('query', query);
      if (tradition) params.set('tradition', tradition);
      if (cycle) params.set('cycle', cycle);
      params.set('page', page.toString());
      params.set('page_size', pageSize.toString());

      const response = await fetch(
        `${apiUrl}/api/mythology/characters?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      return getMockCharacters(query, tradition, page, pageSize);
    }
  });

export const getCharacterById = createServerFn({
  method: 'GET',
})
  .validator((input: unknown) => byIdSchema.parse(input))
  .handler(async ({ data }): Promise<MythologyCharacter | null> => {
    const result = await searchCharacters({ data: { page: 1, pageSize: 100 } });
    return result.items.find((c) => c.id === data.id) || null;
  });

// Stories
export const searchStories = createServerFn({
  method: 'GET',
})
  .validator((input: unknown) => searchSchema.parse(input))
  .handler(async ({ data }): Promise<MythologySearchResult<MythologyStory>> => {
    const { query, tradition, cycle, page, pageSize } = data;

    const apiUrl = process.env.API_URL || 'http://localhost:8000';

    try {
      const params = new URLSearchParams();
      if (query) params.set('query', query);
      if (tradition) params.set('tradition', tradition);
      if (cycle) params.set('cycle', cycle);
      params.set('page', page.toString());
      params.set('page_size', pageSize.toString());

      const response = await fetch(
        `${apiUrl}/api/mythology/stories?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      return getMockStories(query, tradition, page, pageSize);
    }
  });

// Locations
export const searchLocations = createServerFn({
  method: 'GET',
})
  .validator((input: unknown) => searchSchema.parse(input))
  .handler(async ({ data }): Promise<MythologySearchResult<MythologyLocation>> => {
    const { query, tradition, page, pageSize } = data;

    const apiUrl = process.env.API_URL || 'http://localhost:8000';

    try {
      const params = new URLSearchParams();
      if (query) params.set('query', query);
      if (tradition) params.set('tradition', tradition);
      params.set('page', page.toString());
      params.set('page_size', pageSize.toString());

      const response = await fetch(
        `${apiUrl}/api/mythology/locations?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      return getMockLocations(query, tradition, page, pageSize);
    }
  });

// Traditions and cycles
export const getTraditions = createServerFn({
  method: 'GET',
}).handler(async (): Promise<{ id: string; name: string; description: string }[]> => {
  return [
    {
      id: 'irish_mythology',
      name: 'Irish Mythology',
      description: 'Tales of the Tuatha Dé Danann, Ulster Cycle, and Fenian Cycle',
    },
    {
      id: 'welsh_mythology',
      name: 'Welsh Mythology',
      description: 'The Mabinogion and tales of Arthur in Welsh tradition',
    },
    {
      id: 'scottish_folklore',
      name: 'Scottish Folklore',
      description: 'Highland legends, fairy lore, and selkie tales',
    },
    {
      id: 'cornish_folklore',
      name: 'Cornish Folklore',
      description: 'Giants, piskies, and the legends of Cornwall',
    },
    {
      id: 'breton_folklore',
      name: 'Breton Folklore',
      description: 'Korrigans, the Ankou, and Breton Arthurian tales',
    },
    {
      id: 'manx_folklore',
      name: 'Manx Folklore',
      description: 'Fairy Bridge traditions and Isle of Man legends',
    },
  ];
});

export const getCycles = createServerFn({
  method: 'GET',
})
  .validator((input: unknown) =>
    z.object({ tradition: z.string().optional() }).parse(input)
  )
  .handler(async ({ data }): Promise<{ id: string; name: string; tradition: string }[]> => {
    const allCycles = [
      { id: 'mythological_cycle', name: 'Mythological Cycle', tradition: 'irish_mythology' },
      { id: 'ulster_cycle', name: 'Ulster Cycle', tradition: 'irish_mythology' },
      { id: 'fenian_cycle', name: 'Fenian Cycle', tradition: 'irish_mythology' },
      { id: 'historical_cycle', name: 'Historical Cycle', tradition: 'irish_mythology' },
      { id: 'mabinogion', name: 'Mabinogion', tradition: 'welsh_mythology' },
      { id: 'arthurian_welsh', name: 'Welsh Arthurian', tradition: 'welsh_mythology' },
      { id: 'taliesin', name: 'Taliesin Tradition', tradition: 'welsh_mythology' },
    ];

    if (data.tradition) {
      return allCycles.filter((c) => c.tradition === data.tradition);
    }

    return allCycles;
  });

// Mock data functions
function getMockCharacters(
  query: string | undefined,
  tradition: string | undefined,
  page: number,
  pageSize: number
): MythologySearchResult<MythologyCharacter> {
  const mockCharacters: MythologyCharacter[] = [
    {
      id: 'cu_chulainn',
      name: 'Cú Chulainn',
      nativeName: 'Cú Chulainn',
      tradition: 'irish_mythology',
      cycle: 'ulster_cycle',
      type: 'hero',
      description: 'The Hound of Ulster, greatest warrior of the Red Branch Knights',
      powers: ['ríastrad (warp spasm)', 'gáe bolga', 'superhuman strength'],
      relationships: ['Emer (wife)', 'Scáthach (teacher)', 'Lugh (father)'],
    },
    {
      id: 'lugh',
      name: 'Lugh',
      nativeName: 'Lugh Lámhfhada',
      tradition: 'irish_mythology',
      cycle: 'mythological_cycle',
      type: 'deity',
      description: 'The Long-Armed One, master of all arts',
      powers: ['all skills mastery', 'spear of light', 'leadership'],
      relationships: ['Cian (father)', 'Balor (grandfather)'],
    },
    {
      id: 'fionn',
      name: 'Fionn mac Cumhaill',
      nativeName: 'Fionn mac Cumhaill',
      tradition: 'irish_mythology',
      cycle: 'fenian_cycle',
      type: 'hero',
      description: 'Leader of the Fianna, gained wisdom from the Salmon of Knowledge',
      powers: ['prophetic thumb', 'wisdom', 'leadership'],
      relationships: ['Sadhbh (wife)', 'Oisín (son)', 'Oscar (grandson)'],
    },
    {
      id: 'medb',
      name: 'Medb',
      nativeName: 'Medb',
      tradition: 'irish_mythology',
      cycle: 'ulster_cycle',
      type: 'mortal',
      description: 'Queen of Connacht, initiator of the Cattle Raid of Cooley',
      powers: ['sovereignty', 'military command'],
      relationships: ['Ailill (husband)', 'Fergus mac Róich (ally)'],
    },
    {
      id: 'pryderi',
      name: 'Pryderi',
      nativeName: 'Pryderi fab Pwyll',
      tradition: 'welsh_mythology',
      cycle: 'mabinogion',
      type: 'hero',
      description: 'Son of Pwyll and Rhiannon, appears in all Four Branches',
      powers: ['strength', 'nobility'],
      relationships: ['Pwyll (father)', 'Rhiannon (mother)', 'Cigfa (wife)'],
    },
    {
      id: 'gwydion',
      name: 'Gwydion',
      nativeName: 'Gwydion fab Dôn',
      tradition: 'welsh_mythology',
      cycle: 'mabinogion',
      type: 'magical',
      description: 'The greatest magician and trickster of Welsh mythology',
      powers: ['illusion', 'transformation', 'wisdom'],
      relationships: ['Dôn (mother)', 'Math (uncle)', 'Lleu (nephew)'],
    },
    {
      id: 'balor',
      name: 'Balor',
      nativeName: 'Balor na Súile Nimhe',
      tradition: 'irish_mythology',
      cycle: 'mythological_cycle',
      type: 'monster',
      description: 'King of the Fomorians, with a deadly eye that destroys all it sees',
      powers: ['death gaze', 'giant strength'],
      relationships: ['Ethniu (daughter)', 'Lugh (grandson who killed him)'],
    },
  ];

  let filtered = mockCharacters;

  if (tradition) {
    filtered = filtered.filter((c) => c.tradition === tradition);
  }

  if (query) {
    const lowerQuery = query.toLowerCase();
    filtered = filtered.filter(
      (c) =>
        c.name.toLowerCase().includes(lowerQuery) ||
        c.description.toLowerCase().includes(lowerQuery)
    );
  }

  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);

  return {
    items,
    total: filtered.length,
    page,
    pageSize,
    hasMore: start + pageSize < filtered.length,
  };
}

function getMockStories(
  query: string | undefined,
  tradition: string | undefined,
  page: number,
  pageSize: number
): MythologySearchResult<MythologyStory> {
  const mockStories: MythologyStory[] = [
    {
      id: 'tain_bo_cuailnge',
      title: 'Táin Bó Cúailnge',
      englishTitle: 'The Cattle Raid of Cooley',
      tradition: 'irish_mythology',
      cycle: 'ulster_cycle',
      summary: 'Queen Medb of Connacht invades Ulster to steal the Brown Bull',
      themes: ['heroism', 'honor', 'warfare'],
      mainCharacters: ['Cú Chulainn', 'Medb', 'Fergus mac Róich'],
      difficulty: 'intermediate',
    },
    {
      id: 'oidheadh_chlainne_lir',
      title: 'Oidheadh Chlainne Lir',
      englishTitle: 'The Children of Lir',
      tradition: 'irish_mythology',
      cycle: 'mythological_cycle',
      summary: 'Four children cursed to spend 900 years as swans',
      themes: ['transformation', 'patience', 'redemption'],
      mainCharacters: ['Fionnuala', 'Aodh', 'Fiachra', 'Conn', 'Aoife'],
      difficulty: 'beginner',
    },
    {
      id: 'tochmarc_etaine',
      title: 'Tochmarc Étaíne',
      englishTitle: 'The Wooing of Étaín',
      tradition: 'irish_mythology',
      cycle: 'mythological_cycle',
      summary: 'The beautiful Étaín is transformed and reborn across generations',
      themes: ['love', 'jealousy', 'reincarnation'],
      mainCharacters: ['Étaín', 'Midir', 'Eochaid Airem'],
      difficulty: 'intermediate',
    },
    {
      id: 'branwen',
      title: 'Branwen ferch Llŷr',
      englishTitle: 'Branwen Daughter of Llŷr',
      tradition: 'welsh_mythology',
      cycle: 'mabinogion',
      summary: "Branwen's marriage leads to war between Britain and Ireland",
      themes: ['honor', 'vengeance', 'tragedy'],
      mainCharacters: ['Branwen', 'Bendigeidfran', 'Efnysien'],
      difficulty: 'intermediate',
    },
    {
      id: 'pwyll_pendefig_dyfed',
      title: 'Pwyll Pendefig Dyfed',
      englishTitle: 'Pwyll Prince of Dyfed',
      tradition: 'welsh_mythology',
      cycle: 'mabinogion',
      summary: 'Pwyll exchanges places with Arawn and later wins Rhiannon',
      themes: ['honor', 'kingship', 'the otherworld'],
      mainCharacters: ['Pwyll', 'Arawn', 'Rhiannon'],
      difficulty: 'beginner',
    },
  ];

  let filtered = mockStories;

  if (tradition) {
    filtered = filtered.filter((s) => s.tradition === tradition);
  }

  if (query) {
    const lowerQuery = query.toLowerCase();
    filtered = filtered.filter(
      (s) =>
        s.title.toLowerCase().includes(lowerQuery) ||
        s.englishTitle.toLowerCase().includes(lowerQuery) ||
        s.summary.toLowerCase().includes(lowerQuery)
    );
  }

  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);

  return {
    items,
    total: filtered.length,
    page,
    pageSize,
    hasMore: start + pageSize < filtered.length,
  };
}

function getMockLocations(
  query: string | undefined,
  tradition: string | undefined,
  page: number,
  pageSize: number
): MythologySearchResult<MythologyLocation> {
  const mockLocations: MythologyLocation[] = [
    {
      id: 'emain_macha',
      name: 'Emain Macha',
      englishName: 'Navan Fort',
      tradition: 'irish_mythology',
      type: 'fortress',
      description: 'Capital of Ulster and seat of King Conchobar mac Nessa',
      latitude: 54.3483,
      longitude: -6.695,
      associatedStories: ['Táin Bó Cúailnge', 'Deirdre of the Sorrows'],
    },
    {
      id: 'tir_na_nog',
      name: 'Tír na nÓg',
      englishName: 'Land of the Young',
      tradition: 'irish_mythology',
      type: 'otherworld',
      description: 'The supernatural realm where time stands still',
      associatedStories: ['Oisín in Tír na nÓg'],
    },
    {
      id: 'teamhair',
      name: 'Teamhair',
      englishName: 'Hill of Tara',
      tradition: 'irish_mythology',
      type: 'sacred_site',
      description: 'Seat of the High Kings of Ireland, home of the Lia Fáil',
      latitude: 53.5789,
      longitude: -6.6114,
      associatedStories: ['The High Kings', 'Lia Fáil'],
    },
    {
      id: 'annwfn',
      name: 'Annwfn',
      englishName: 'The Otherworld',
      tradition: 'welsh_mythology',
      type: 'otherworld',
      description: 'The Welsh otherworld, ruled by Arawn',
      associatedStories: ['Pwyll Pendefig Dyfed'],
    },
    {
      id: 'dinas_bran',
      name: 'Dinas Brân',
      englishName: 'Crow Castle',
      tradition: 'welsh_mythology',
      type: 'fortress',
      description: 'Hillfort associated with Brân the Blessed',
      latitude: 52.9801,
      longitude: -3.1681,
      associatedStories: ['Branwen ferch Llŷr'],
    },
  ];

  let filtered = mockLocations;

  if (tradition) {
    filtered = filtered.filter((l) => l.tradition === tradition);
  }

  if (query) {
    const lowerQuery = query.toLowerCase();
    filtered = filtered.filter(
      (l) =>
        l.name.toLowerCase().includes(lowerQuery) ||
        l.englishName.toLowerCase().includes(lowerQuery) ||
        l.description.toLowerCase().includes(lowerQuery)
    );
  }

  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);

  return {
    items,
    total: filtered.length,
    page,
    pageSize,
    hasMore: start + pageSize < filtered.length,
  };
}
