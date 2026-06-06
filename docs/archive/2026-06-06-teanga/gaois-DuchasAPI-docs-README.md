# Dúchas Application Programming Interface (Version 0.5): Developer documentation

## Moved

***Please see [docs.gaois.ie](https://docs.gaois.ie) for the latest documentation in respect of the Dúchas API. This repository is no longer being actively maintained. It will be preserved, however, for archival purposes.***

## Contents

**Note:** This documentation describes a **prerelease** version of the Dúchas API. Features are being added on an ongoing basis. This documentation will be revised in advance of the v1.0 release. 

1. [Introduction](#introduction)
2. [API overview](#api-overview)
3. [API versioning](#api-versioning)
4. [API authentication](#api-authentication)
5. [API access privileges](#api-access-privileges)
6. [Security](#security)
7. [Resource paths](#resource-paths)
8. [HTTP status codes](#http-status-codes)
9. [Data retention and data protection](#data-retention-and-data-protection)

## Introduction

Dúchas is a project is to initiate the digitization of the [National Folklore Collection](https://www.ucd.ie/irishfolklore/en) (NFC), held at University College Dublin (UCD), Ireland. The results of the work to date have been made publicly available at [www.duchas.ie](https://www.duchas.ie) and are in the process of being archived for preservation by the [UCD Digital Library](https://digital.ucd.ie/). The technical solution is provided by [Fiontar & Scoil na Gaeilge](https://www.dcu.ie/fiontar_scoilnagaeilge/), Dublin City University (DCU). This documentation describes a web-based Application Programming Interface (API) that exposes the published content from the Collection to programmatic queries. A [data dictionary](https://github.com/gaois/DuchasAPI-docs/blob/master/DATADICT.md) is available to assist users in parsing results returned by the API.

### The National Folklore Collection and its collections

Data from three of the five major collections of folklore held by Cnuasach Bhéaloideas Éireann/the National Folklore Collection are currently accessible via this platform. An understanding of the composition of these collections will aid your use of the API. Note that the databases associated with these collections are commonly referred to in shorthand form using acronyms such as CBÉS, CBÉG, etc. These acronyms are generally formed from the Irish-language name of the NFC: *Cnuasach Bhéaloideas Éireann* followed by a single letter that denotes the database in question. The database of the NFC's Main Manuscript Collection is simply referred to as CBÉ.

#### The Main Manuscript Collection (CBÉ)

The Main Manuscript Collection comprises 2,400 bound volumes of material collected since 1932. Full- and part-time collectors compiled the majority of these under the auspices of the Irish Folklore Commission (1935–1971). Approximately two thirds of the material is in Irish and it includes every aspect of the Irish oral tradition. This Collection is in the process of digitization with approximately 70 volumes published online to date. 

#### The Schools' Collection (CBÉS)

Approximately 740,000 pages (288,000 pages in the pupils’ original exercise books; 451,000 pages in bound volumes) of folklore and local tradition were compiled by pupils from 5,000 primary schools in the Irish Free State between 1937 and 1939. This scheme, known as *Scéim na Scol*, resulted in the creation of over half a million manuscript pages, generally referred to as ‘Bailiúchán na Scol’ or ‘The Schools’ Collection’. There are 1,128 volumes, numbered and bound, in the Collection, all of which have been digitised.

#### The Photographic Collection (CBÉG)

The National Folklore Collection’s photographic collection consists of some 80,000 photographs, the majority of which were taken by members of the Irish Folklore Commission (1935-70) and its successors, including staff of the NFC. The process of digitising and conserving the collection continues apace; some 10,000 images have been made available online for the first time.

#### The Persons Database (CBÉD)

Persons named within the CBÉ and CBÉG metadata are identified by reference to objects in this database. CBÉD does not map directly to any physical collection held by the NFC. Rather, given that many persons appear in several NFC collections—some photographers in CBÉG are also collectors in CBÉ, for example—the Persons Database is designed to serve as a single source of truth for personal metadata across the entire data set. At present, the Persons Database comprises all persons in the digitised portions of CBÉ and CBÉG. Due to the scope of the Schools' Collection digitisation project it has not yet been feasible to extract a normalised set of personal metadata; it is hoped to revisit this work in the future, however.

Further information regarding the NFC and its collections is available [here](https://www.duchas.ie/en/info/cbe).

## API overview

The Dúchas API provides access to a number of resources by means of a defined URL schema. Specific resources are accessed via unique paths appended to the main website host. In some cases the resources that are returned may be filtered using optional query parameters. Attempts to access a resource provided by the API are referred to as requests. Following a successful request, resources are returned in the form of JSON. An unsuccessful attempt to access a resource will receive, at a minimum, a relevant HTTP status code in response to the request. An example of a valid request to the API is as follows:

> `https://www.duchas.ie/api/v0.5/cbed/315678333`

Users or applications (clients) requesting a resource via the API must authenticate their identity. This is achieved by providing an API key with each request. Each client must obtain a unique API key prior to interacting with the interface. Authentication is required to prevent abuse of the service and to track general usage statistics. Further details are provided below.

## API versioning

Multiple API versions are facilitated. This is to say, more than one version of the API may be accessible at the same time. Newer API versions may offer additional resources or functionalities but may require a different request syntax to older versions. The target API version is indicated by the second path parameter in the request URL:

> /api/**v0.5**/authors

Older versions will be supported for developer convenience: without versioning, frequent changes to API syntax may cause dependent client applications to malfunction. We will endeavour to add new resources incrementally and will implement breaking changes only as a last resort. The API is versioned using [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) (semver) and follows the semver specification. For brevity, however, only major and minor version points are reflected in request URLs.

After a period of time it may become necessary to deprecate older API versions for maintenance or performance reasons. When you register for your API key, you will be asked if you are willing to receive communications from Fiontar & Scoil na Gaeilge from time to time. Agreeing to receive such communication means you will receive advance notice of any such changes.

**Note:** Prerelease versions of this API (i.e. < v1.0) are for testing purposes and will not be maintained once a v1.0 release has been reached.

## API authentication

Clients requesting a resource via the API are required to authenticate their identity. This is achieved by passing an API key to the service with each request. Authentication offers some protection to the service provider from abuse of the API involving request overloads. It also allows us to retain some usage statistics, with a view to performance monitoring and service enhancement. Learn more about the data we retain in the following sections.

### How to obtain your API key

Visit the Gaois Developer Hub at [gaois.ie](https://www.gaois.ie/). Log in or register to create an account and you will be able to access your unique API key.

**Note:** This registration service is coming soon. In the meantime, please contact us at [eolas@duchas.ie](mailto:eolas@duchas.ie) to request or reset your API key.

### How to pass your API key

Your API key may be passed to the service in a few different ways. Choose whichever method is easiest for you.

#### HTTP header

Pass the API key into an `X-Api-Key` header:

> `'X-Api-Key: <API_KEY_HERE>' 'https://www.duchas.ie/api/v0.5/cbed/1740563'`

#### GET query parameter

Pass the API key into an `apiKey` GET query string parameter:

> `'https://www.duchas.ie/api/v0.5/cbed/1740563?apiKey=API_KEY_HERE'`

**Note:** The GET query parameter may be used for non-GET requests (such as POST and PUT).

#### HTTP Basic Authentication username

As an alternative, pass the API key as the username (with an empty password) using HTTP basic authentication:

> `'https://API_KEY_HERE@www.duchas.ie/api/v0.5/cbed/1740563'`

## API access privileges

The Dúchas API caters to a number of different consumer types, including public users, archival users and internal clients. As a result of this, each API user—identified through their associated API key—is granted access permissions in accordance with our Terms of Service. Privileged consumers have access to material that is not yet ready, or is deemed unsuitable, for publication as well as  internal editorial metadata. They can also filter query results according to certain additional parameters. Metadata and query parameters which are unavailable to public consumers are labelled 'Privileged' in the API documentation. Generally speaking, only internal clients in UCD and DCU are privileged consumers. If you have any questions regarding your current access privileges please [contact us](mailto:eolas@duchas.ie).

## Security

The API is served over a HTTPS protocol. Though HTTP requests to the service are automatically redirected to HTTPS, you should only ever interact with the API using HTTPS-prefixed URLs.

While HTTPS offers a signficant level of security, we would stress that the basic authentication methods described above do not amount to end-to-end encryption. **You should only ever pass your API Key to the service**—never include sensitive data, particularly passwords, as part of your requests.

## Resource paths

The resources provided by the API are accessed via unique paths appended to the main website URL. All currently-available request paths are listed below. A [data dictionary](https://github.com/gaois/DuchasAPI-docs/blob/master/DATADICT.md) is available to assist users in parsing results returned by the API.

| Method      | Path                          | Collection     | Resource                  |
| :---------- | :---------------------------- | :------------- | :------------------------ |
| GET         | `/api`                        | N/A            | General API metadata.     |
| GET         | `/api/v0.5`                   | N/A            | General API metadata.     |
| GET         | `/api/v0.5/cbe`               | CBÉ            | List of manuscript volumes and associated metadata.* |
| GET         | `/api/v0.5/cbe/volumes`       | CBÉ            | Index of manuscript volumes and summary metadata. |
| GET         | `/api/v0.5/cbed`              | CBÉD           | List of persons and associated metadata. |
| GET         | `/api/v0.5/cbed/{id}`         | CBÉD           | Metadata associated with an individual person. |
| GET         | `/api/v0.5/cbed/occupations`  | CBÉD           | Reference list of metadata associated with occupations. |
| GET         | `/api/v0.5/cbeg`              | CBÉG           | List of photographs and associated metadata.** |
| GET         | `/api/v0.5/cbeg/{id}`         | CBÉG           | Metadata associated with an individual photograph. |
| GET         | `/api/v0.5/cbeg/topics/handbook`   | CBÉG           | Reference list of subject headings (topics) in Seán Ó Súilleabháin's [*An Handbook of Irish Folklore*](https://www.duchas.ie/en/tpc/cbeg). |
| GET         | `/api/v0.5/cbes`              | CBÉS           | List of manuscript volumes and associated metadata.*** |
| GET         | `/api/v0.5/cbes/volumes`      | CBÉS           | Index of manuscript volumes and summary metadata. |
| GET         | `/api/v0.5/cbes/topics`       | CBÉS           | Reference list of topics from the [Schools' Collection Subject List](https://www.duchas.ie/en/tpc/cbes).
| GET         | `/api/v0.5/counties`          | N/A            | Reference list of metadata associated with Irish counties. |
| GET         | `/api/v0.5/countries`         | N/A            | Reference list of metadata associated with countries. |

**\*** Requests to the `/api/v0.5/cbe` endpoint must be filtered by at least one of the following parameters: `VolumeID`, `VolumeNumber`, `PageID`, `PartID`, `ItemID`,`CountyID`, `PlaceID`, `Country`, `GeoNameID`, `CollectorID`, `InformantID`, or `PersonID`.

**\*\*** Requests to the `/api/v0.5/cbeg` endpoint must be filtered by at least one of the following parameters: `CountyID`, `PlaceID`, , `Country`, `GeoNameID`, `PhotographerID`, `RelevantPersonID`, or `PersonID`.

**\*\*\*** Requests to the `/api/v0.5/cbes` endpoint must be filtered by at least one of the following parameters: `VolumeID`, `VolumeNumber`, `PageID`, `PartID`, `ItemID`, `SchoolCountyID`, `SchoolPlaceID`, `TeacherID`, `CountyID`, `PlaceID`, `Country`, `GeoNameID`, `CollectorID`, `InformantID`, or `PersonID`.

### URL path parameters

| Name          | Type          | Description    |
| :------------ | :------------ | :------------- |
| `id`          | integer       | Resource ID.    |

### URL query parameters

Use these query parameters to filter the results returned by the API.

#### The Main Manuscript Collection (CBÉ)

| Name          | Type          | Description    |
| :------------ | :------------ | :------------- |
| `Status`      | integer       | Filter by editorial status (0-4). **(Privileged)** |
| `VolumeNumber` | string        | Filter by manuscript volume archival reference (e.g. '0154') |
| `VolumeID`    | integer       | Filter by manuscript volume identifer. |
| `PageID`      | integer       | Filter by manuscript page identifer. |
| `PartID`      | integer       | Filter by manuscript part identifer. |
| `ItemID`      | integer       | Filter by manuscript item identifer. |
| `CollectorID` | integer       | Filter by collector's CBÉD identifier. |
| `InformantID` | integer       | Filter by informant's CBÉD identifier. |
| `RelevantPersonID` | integer       | Filter by person's CBÉD identifer. |
| `PersonID` | integer       | Filter by person's CBÉD identifer. This filter encompasses all person types (i.e. collector, informant, relevant person). |
| `CountyID`    | integer       | Filter by county using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `PlaceID`     | integer       | Filter by place using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `Country`     | ISO 3166 country code* | Filter by country using ISO code (e.g. DE, US, GB-ENG). |
| `GeoNameID`   | integer       | Filter by place using [GeoName](https://www.geonames.org) placename identifer.  |
| `Language`    | string        | Filter items by language using ISO 639-1 language code |
| `DateFrom`    | integer**     | Retrieve records associated with this year or later. |
| `DateTo`      | integer**     | Retrieve records associated with this year or earlier. |
| `DateAccuracy` | string       | Filter by accuracy of date record (APPROX, INFER, QUESTION). |
| `CreatedBefore` | ISO 8601 datetime | Retrieve records created before a given date in `YYYY-MM-DD` format. |
| `CreatedSince` | ISO 8601 datetime | Retrieve records created after a given date in `YYYY-MM-DD` format. |
| `ModifiedBefore` | ISO 8601 datetime | Retrieve records last updated before a given date in `YYYY-MM-DD` format. |
| `ModifiedSince` | ISO 8601 datetime | Retrieve records last updated after a given date in `YYYY-MM-DD` format. |

**\*Note:** The two-letter country codes accepted by the `Country` parameter conform to the [ISO 3166-1](https://www.iso.org/iso-3166-country-codes.html) standard. However, four additional ISO 3166-2 codes are accepted to facilitate differentiation between England, Northern Ireland, Scotland, and Wales. These are, respectively: `GB-ENG`, `GB-NIR`, `GB-SCT` and `GB-WLS`.

**\*\*Note:** The `DateFrom` and `DateTo` parameters currently only accept years in `YYYY` format.

#### The Schools' Collection (CBÉS)

| Name          | Type          | Description    |
| :------------ | :------------ | :------------- |
| `Status`      | integer       | Filter by editorial status (0-4). **(Privileged)** |
| `VolumeNumber` | string        | Filter by manuscript volume archival reference (e.g. '0154') |
| `VolumeID`    | integer       | Filter by manuscript volume identifer. |
| `PageID`      | integer       | Filter by manuscript page identifer. |
| `PartID`      | integer       | Filter by manuscript part identifer. |
| `ItemID`      | integer       | Filter by manuscript item identifer. |
| `SchoolCountyID`    | integer       | Filter schools (i.e. manucript parts) by county using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `SchoolPlaceID`     | integer       | Filter schools (i.e. manucript parts) by place using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `TeacherID`   | integer       | Filter schools (i.e. manucript parts) by teacher's CBÉS identifier. |
| `CollectorID` | integer       | Filter items by collector's CBÉS identifier. |
| `InformantID` | integer       | Filter items by informant's CBÉS identifier. |
| `PersonID`    | integer       | Filter items by person's CBÉS identifer. This filter encompasses both collectors and informants. |
| `CountyID`    | integer       | Filter items by county using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `PlaceID`     | integer       | Filter items by place using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `TopicID`     | integer       | Filter items by topic using CBÉS topic identifier. |
| `Language`    | string        | Filter items by language using ISO 639-1 language code. |
| `CreatedBefore` | ISO 8601 datetime | Retrieve records created before a given date in `YYYY-MM-DD` format. |
| `CreatedSince` | ISO 8601 datetime | Retrieve records created after a given date in `YYYY-MM-DD` format. |
| `ModifiedBefore` | ISO 8601 datetime | Retrieve records last updated before a given date in `YYYY-MM-DD` format. This includes new or updated page transcripts. |
| `ModifiedSince` | ISO 8601 datetime | Retrieve records last updated after a given date in `YYYY-MM-DD` format. This includes new or updated page transcripts. |

#### The Photographic Collection (CBÉG)

| Name          | Type          | Description    |
| :------------ | :------------ | :------------- |
| `Status`      | integer       | Filter by editorial status (0-4). **(Privileged)** |
| `Digitized`   | boolean       | Filter by digitization status. |
| `Copyright`   | string        | Filter by copyright holder (e.g. CBE, UNK). |
| `Condition`   | integer       | Filter by physical condition (0-3). |
| `HandbookTopic` | string        | Filter by [*A Handbook of Irish Folklore*](https://www.duchas.ie/en/tpc/cbeg) subject code (e.g. B005). |
| `PersonID`    | integer       | Filter by person's CBÉD identifer. |
| `PhotographerID` | integer       | Filter by photographer's CBÉD identifer. |
| `RelevantPersonID` | integer       | Filter by person's CBÉD identifer. |
| `CountyID`    | integer       | Filter by county using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `PlaceID`     | integer       | Filter by place using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `Country`     | ISO 3166 country code* | Filter by country using ISO code (e.g. DE, US, GB-ENG). |
| `GeoNameID`   | integer       | Filter by place using [GeoName](https://www.geonames.org) placename identifer.  |
| `DateFrom`    | integer**     | Retrieve records associated with this year or later. |
| `DateTo`      | integer**     | Retrieve records associated with this year or earlier. |
| `DateAccuracy` | string       | Filter by accuracy of date record (APPROX, INFER, QUESTION). |
| `CreatedBefore` | ISO 8601 datetime | Retrieve records created before a given date in `YYYY-MM-DD` format. |
| `CreatedSince` | ISO 8601 datetime | Retrieve records created after a given date in `YYYY-MM-DD` format. |
| `ModifiedBefore` | ISO 8601 datetime | Retrieve records last updated before a given date in `YYYY-MM-DD` format. |
| `ModifiedSince` | ISO 8601 datetime | Retrieve records last updated after a given date in `YYYY-MM-DD` format. |

**\*Note:** The two-letter country codes accepted by the `Country` parameter conform to the [ISO 3166-1](https://www.iso.org/iso-3166-country-codes.html) standard. However, four additional ISO 3166-2 codes are accepted to facilitate differentiation between England, Northern Ireland, Scotland, and Wales. These are, respectively: `GB-ENG`, `GB-NIR`, `GB-SCT` and `GB-WLS`.

**\*\*Note:** The `DateFrom` and `DateTo` parameters currently only accept years in `YYYY` format.

#### The Persons Database (CBÉD)

| Name          | Type          | Description    |
| :------------ | :------------ | :------------- |
| `Gender`      | string        | Filter by person's gender (f, m).  |
| `AinmID`      | integer       | Filter by [ainm.ie](https://www.ainm.ie) entry ID.  |
| `ViafID`      | integer       | Filter by [VIAF](https://viaf.org/) entryID.  |
| `CountyID`    | integer       | Filter by county using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `PlaceID`     | integer       | Filter by place using [logainm.ie](https://www.logainm.ie) placename identifer.  |
| `Country`     | ISO 3166 country code* | Filter by country ISO code (e.g. DE, US, GB-ENG). |
| `GeoNameID`   | integer       | Filter by [GeoName](https://www.geonames.org) placename identifer.  |
| `Occupation`  | string        | Filter by occupation (e.g. IASC, FEIRM). |
| `BirthDateFrom` | integer**     | Retrieve records associated with this birth year or later. |
| `BirthDateTo` | integer**     | Retrieve records associated with this birth year or earlier. |
| `BirthDateAccuracy` | string       | Filter by accuracy of birth date record (APPROX, INFER, QUESTION). |
| `DeathDateFrom` | integer**     | Retrieve records associated with this death year or later. |
| `DeathDateTo` | integer**     | Retrieve records associated with this death year or earlier. |
| `DeathDateAccuracy` | string       | Filter by accuracy of death date record (APPROX, INFER, QUESTION). |
| `CreatedBefore` | ISO 8601 datetime | Retrieve records created before a given date in `YYYY-MM-DD` format. |
| `CreatedSince` | ISO 8601 datetime | Retrieve records created after a given date in `YYYY-MM-DD` format. |
| `ModifiedBefore` | ISO 8601 datetime | Retrieve records last updated before a given date in `YYYY-MM-DD` format. |
| `ModifiedSince` | ISO 8601 datetime | Retrieve records last updated after a given date in `YYYY-MM-DD` format. |

**\*Note:** The two-letter country codes accepted by the `Country` parameter conform to the [ISO 3166-1](https://www.iso.org/iso-3166-country-codes.html) standard. However, four additional ISO 3166-2 codes are accepted to facilitate differentiation between England, Northern Ireland, Scotland, and Wales. These are, respectively: `GB-ENG`, `GB-NIR`, `GB-SCT` and `GB-WLS`.

**\*\*Note:** The `DateFrom` and `DateTo` parameters currently only accept years in `YYYY` format.

### Illustrative examples

Below is a non-exhaustive list of valid API request URLs, provided for demonstration purposes:

- `https://www.duchas.ie/api/v0.5/cbe/?VolumeID=7000256`
- `https://www.duchas.ie/api/v0.5/cbe/?PersonID=315678581`
- `https://www.duchas.ie/api/v0.5/cbed/315678333`
- `https://www.duchas.ie/api/v0.5/cbed/1740563`
- `https://www.duchas.ie/api/v0.5/cbed/?ModifiedSince=2019-01-01`
- `https://www.duchas.ie/api/v0.5/cbed/?PlaceID=35176`
- `https://www.duchas.ie/api/v0.5/cbed/?Gender=f&CountyID=100013`
- `https://www.duchas.ie/api/v0.5/cbed/?Country=AU`
- `https://www.duchas.ie/api/v0.5/cbed/?GeoNameID=2177413`
- `https://www.duchas.ie/api/v0.5/cbed/?PlaceID=130443&Occupation=IASC`
- `https://www.duchas.ie/api/v0.5/cbeg/974`
- `https://www.duchas.ie/api/v0.5/cbeg/?CountyID=100009&ModifiedSince=2018-09-01`
- `https://www.duchas.ie/api/v0.5/cbeg/?Status=4&CountyID=100023`
- `https://www.duchas.ie/api/v0.5/cbeg/?Copyright=UNK&PhotographerID=93573082`
- `https://www.duchas.ie/api/v0.5/cbeg/?HandbookTopic=E&PhotographerID=93573082&Digitized=false`
- `https://www.duchas.ie/api/v0.5/cbeg/?HandbookTopic=B006&CountyID=100023`
- `https://www.duchas.ie/api/v0.5/cbeg/?CountyID=100024&DateFrom=1960&DateTo=1969&DateAccuracy=APPROX`
- `https://www.duchas.ie/api/v0.5/cbes/?VolumeNumber=0133`
- `https://www.duchas.ie/api/v0.5/cbes/?CountyID=100002&TopicID=5192275&Language=en`
- `https://www.duchas.ie/api/v0.5/cbes/?PlaceID=18689`
- `https://www.duchas.ie/api/v0.5/cbes/topics`
- `https://www.duchas.ie/api/v0.5/counties`

## HTTP status codes

The status of all requests will be communicated, in the first instance, via standard HTTP status codes. We recommend that any applications interacting with the API handle the following status codes:

| Code  | Definition            | Further information |
| :---- | :-------------------- | :------------------ |
| 200   | OK                    | One or more JSON objects will be returned.  |
| 400   | BAD REQUEST           | The request syntax was invalid—a JSON object describing the error may be returned. |
| 401   | UNAUTHORISED          | A valid API key was not provided. |
| 404   | NOT FOUND             | The resource does not exist. |
| 500   | INTERNAL SERVER ERROR | Please contact us at [eolas@duchas.ie](mailto:eolas@duchas.ie) quoting the request path. |

**Note:** The current API does not handle create-, update-, or delete-type requests. Therefore, only HTTP GET methods are facilitated at this time.

## Data retention and data protection

We store the following data every time a request is made to the API:

1. Request path
2. Response status code
3. Result count
4. Query response time
5. Client ID (obtained with reference to the provided API key)

The client ID links your request to the data you have stored in the gaois.ie Developer Hub (the data you provided when you signed up for the service, for example). You can view all of the above data at any time in the Gaois.ie Developer Hub. These data are stored by Fiontar & Scoil na Gaeilge in a GDPR-compliant manner.

We reserve the right to report and/or publish aggregated or anonymised API query metrics. We will not report, publish or share any specific client data (i.e. your client ID or any associated client identification data) with any third party. We reserve the right to retain data items 1–4, listed above, indefinitely for the purposes of performance monitoring, research and service enhancement.

You are entitled to have your personal data removed from our systems at any time. This means deleting your username, password, name, organisational affiliation, and association with stored requests, completely and permanently. Please contact us at [eolas@duchas.ie](mailto:eolas@duchas.ie) if you wish to request that your personal data be removed.

By accessing the API you agree to abide by all policies and practices outlined in this document.
