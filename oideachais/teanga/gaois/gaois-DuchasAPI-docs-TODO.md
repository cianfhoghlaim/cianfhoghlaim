# Issues to be addressed

## Essential

- A number of the filter parameters in the Main Manuscript Collection API, e.g. `CollectorID`, `InformantID`, `PlaceID`, etc., do not retrieve the complete result sets that they should. This is not due to any technical issue with the API, rather it is the result of changes that are currently underway to the data structure of this collection. The editors have requested that certain data be associated with manuscript items rather than manuscript parts. This issue is currently being addressed.
- Transcripts in the Schools' Collection API are currently served from a copy of the production database. These services need to be integrated so that transcripts are retrieved from the 'live' data.

## Planned

- The Schools' Collection stores personal names in a different format to the rest of the collections. In the Schools' Collection surname prefixes such as Mac, Mc, Ní, Nic, Ó, O', etc. are stored as part of the `FirstNames` property; this is not the case in the other collections. It is planned to standardise the approach.

## Desirable

- Fulltext search across collections, e.g. `/api/v1.0/cbes/?Query=St.+John's+Eve`
- Query parameter for retrieving items or pages from the Schools' Collection (and, in the future, the Main Manuscript Collection) that have/have not been transcribed.
- Provide image metadata for Main Manuscript, Schools' and Photographic Collections, e.g. URL, width, height, MIME type, etc.
