# Changelog

## **0.5.1** - 2019-07-08

### Added

- `DateCreated` and `DateModified` properties to all `page` objects in the Main Manuscript and Schools' Collections.

### Changed

- Fixed issue with slow response times/status 500 errors when querying the Main Manuscript and Schools' Collections using `CreatedBefore`, `CreatedSince`, `ModifiedBefore`, or `ModifiedSince` query parameters.
- Queries to the Main Manuscript and Schools' Collections filtered with parameters other than `VolumeID` or `VolumeNumber` return only assigned pages with the response. That is to say, they include only pages which are assigned to a manuscript item or are marked as title pages; blank pages are excluded from the response. This helps return relevant results and reduces response payload size. For consumers wishing to obtain both assigned and unassigned pages it is recommended to iterate over the collections by volume ID. An index of volume IDs can be obtained from the `/cbe/volumes` and `/cbes/volumes`endpoints.

## **0.5.2** - 2019-10-24

### Changed

- The API is now accessible via the production www.duchas.ie domain. The documentation has been updated to remove references to the test domain.
