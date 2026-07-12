import type { Persona } from "./_schema";
import { aleyum } from "./aleyum";
import { cianfhoghlaim } from "./cianfhoghlaim";

export const PERSONAS: Persona[] = [aleyum, cianfhoghlaim];
export const PERSONA_MAP = new Map(PERSONAS.map((p) => [p.slug, p]));

export const DEFAULT_PERSONA = "aleyum";

export function getPersona(slug: string): Persona | undefined {
  return PERSONA_MAP.get(slug);
}

export function resolvePersona(slug: string | undefined): Persona {
  if (slug) {
    const found = getPersona(slug);
    if (found) return found;
  }
  return getPersona(DEFAULT_PERSONA)!;
}
