// cn utility — combines clsx + tailwind-merge
// The standard className composition utility for the Cianfhoghlaim OS.

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}