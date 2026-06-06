# Changelog

## **0.9.1** - 2019-11-18

### Added

- `Page` and `PerPage` query parameters to facilitate pagination of place result sets.
- `TotalPages`, `CurrentPage` and `CountPerPage` properties to the `placeList` result object, to be displayed when the result set is paginated.
- Additional descriptive error messages related to pagination (e.g. for index out of range-type errors).

### Changed

- Updated documentation and data dictionary to reflect the above additions.
- Both 400 and 404 errors now return descriptive error messages in JSON format in addition to the appropriate HTTP status codes.
