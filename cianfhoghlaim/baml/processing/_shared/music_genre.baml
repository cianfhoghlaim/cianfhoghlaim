// =============================================================================
// MusicGenre — hoisted canonical enum
// =============================================================================
// Merged from the 2 dups removed in `2026-07-12-baml-rename-42-duplicates-v1`:
//   - processing/portfolio_extraction.baml (7 values)
//   - processing/artwork_analysis.baml (14 values)
// The consumer files use the renamed locals:
//   - MusicGenrePortfolio (portfolio_extraction.baml)
//   - MusicGenreArtwork (artwork_analysis.baml)
// Add a new consumer file by importing or referencing `MusicGenre` here.
// =============================================================================

enum MusicGenre {
  // Portfolio-extraction values
  ELECTRONIC @description("Electronic music including EDM, house, techno")
  AMBIENT @description("Ambient and atmospheric music")
  EXPERIMENTAL @description("Experimental and avant-garde")
  INDIE @description("Indie music")
  SOUNDTRACK @description("Film/game soundtracks")
  CELTIC @description("Celtic traditional or Celtic fusion")
  OTHER @description("Other genres")

  // Artwork-analysis additions
  DNB @description("Drum and bass")
  LIQUID @description("Liquid (DnB subgenre)")
  TECHNO @description("Techno")
  HOUSE @description("House")
  CHILLOUT @description("Chillout / downtempo")
  JAZZ @description("Jazz")
  CLASSICAL @description("Classical")
  HIP_HOP @description("Hip-hop")
  ROCK @description("Rock")
  POP @description("Pop")
}