# API Design Decisions

This document outlines the rationale for some of the major design decisions involved in building the Logainm API in Q&A format.

## 1. How did you choose the API authentication method? Why not use OAuth or another JWT-based authentication protocol?

Our requirements for authentication are minimal and extend only to performance and usage monitoring. In terms of end-user experience, we wanted to keep the barrier to entry as low as possible. As such, the simple, key-based protocol we have chosen means that API consumers can get set up and start working quickly and without the need for any pre-existing tooling.

## 2. Did you consider structuring the data according to JSON-LD, RDF-JSON or another linked data standard?

It is precisely this multiplicity of standards that discouraged us from taking such an approach at this stage. We were reluctant to 
bet on a standard that may, or may not, be useful to our API consumers. We felt that, at this juncture, there was more benefit to be derived from making the data retrieval process as useful and as performant as possible, and producing high-quality and comprehensive documentation. We welcome feedback in this regard, however, and if there is reasonable demand for a particular linked data standard this is something we would consider implementing in v2.0 of the API. You might also be interested in looking at the [Linked Logainm](https://www.logainm.ie/en/inf/proj-machines) project.

## 3. How does the Logainm API represent the hierarchical nature of the data set?

Consumers of the API will have noticed that aspects of the Logainm data set are hierarchical in nature (e.g. townlands can be sub-units of civil parishes, which can be sub-units of baronies, which can be sub-units of counties, etc.) but that the API returns a 'flat', unnested array of `place` objects. There are several reasons for this, but again the user experience is paramount: were we to return fully-hierarchical result sets consumers would be required to write complex recursive functions to parse the data. The result sets would also be orders of magnitude larger and have a performance impact for all concerned. We believe the current approach offers a pragmatic solution: the `includedIn` property of each `place` object represents that place's hierarchical antecedents while the `PlaceID` query parameter makes it easy to query for sub-units included within a particular place.
