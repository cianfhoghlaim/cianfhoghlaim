// Nigerian 37-sub-unit state code registry.

class NigeriaState {
  SLUG string @description("nga_<state> — e.g. nga_los, nga_kan, nga_fct")
  NAME string @description("The English-language state name")
  REGION string @description("north_west | north_east | north_central | south_west | south_east | south_south")
  MAJORITY_LANG string @description("ha | yo | ig | pcm")
  CAPITAL string @description("The state capital")
}
