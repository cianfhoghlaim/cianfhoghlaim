# Changedetection — Website Monitoring

Monitors 19 wiki/site pages for changes at `https://changedetection.cianfhoghlaim.ie`. Login via PocketID SSO.

### Monitored Pages
University of Galway, Fine Gael, Alliance Party of Northern Ireland, Liberal Democrats, Keir Starmer, Charles Windsor, Manannán Mac Lir, The Lisbon Treaty, The Equal Status Act, The Wheel of Time, The Irish High Court, Éamonn Deacy Park, The Manx Pound, The British Isles, Goidelic Languages, Brythonic Languages, Alan Turing (plus 2 configurable slots)

### Integration
Changes trigger n8n's `wiki-page-monitor` workflow:
- LLM classifies edit as neutral/biased/hostile/factual-error
- Flagged edits create Vikunja tasks + email alerts
- Weekly digest aggregates all changes with severity scores

Backed by PlanetScale "bunchloch" (schema: `changedetect`).
