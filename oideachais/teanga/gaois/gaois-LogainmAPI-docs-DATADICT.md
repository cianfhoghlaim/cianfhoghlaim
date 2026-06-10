# Logainm Application Programming Interface (Version 0.9): Data dictionary

**Note:** This documentation describes a **prerelease** version of the Logainm API. Features are being added on an ongoing basis. The documentation will be revised in advance of the v1.0 release.

This document describes the data structure of the results made available via the Logainm Application Programming Interface (API). Logainm is a comprehensive management system for data, archival records and placenames research conducted by the Government of Ireland. For general information regarding the API and for developer guidelines please consult the [developer documentation](https://github.com/gaois/LogainmAPI-docs/blob/master/README.md).

## Contents

- [`placeList`](#placeList)
- [`place`](#place)
  - [`cluster`](#cluster)
  - [`clusterMember`](#clusterMember)
  - [`placename`](#placename)
  - [`acceptability`](#acceptability)
  - [`audio`](#audio)
  - [`subName`](#subName)
  - [`placeSummary`](#placeSummary)
  - [`geography`](#geography)
  - [`coordinates`](#coordinates) 
  - [`gridReference`](#gridReference)
  - [`placeProperty`](#placeProperty)
  - [`image`](#image)
  - [`resource`](#resource)
  - [`supplier`](#supplier)
  - [`link`](#link)
  - [`biographyLink`](#biographyLink)
  - [`folkloreLink`](#folkloreLink)
  - [`sameAs`](#sameAs)
- [`category`](#category)
- [`glossary`](#glossary)

## `placeList`

Most API queries will return a `placeList` object. This contains a list of one or more places, if found, and additional metadata related to the query.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| TotalCount      | integer             | one                 | The total count of place records retrieved. |
| TotalPages      | integer             | none or one         | If the place list is paginated, the total number of pages in the result set. |
| CurrentPage     | integer             | none or one         | If the place list is paginated, the current page number. |
| CountPerPage    | integer             | none or one         | If the place list is paginated, the maximum count of results returned per page. |
| Places          | [`place`](#place)     | none or one or many | The retrieved place records. |
| SimilarNames    | string              | none or one or many | A set of names which have a similar spelling to the query text (if performing a textual search). For example, if searching for 'Ballybunion', 'Ballybunnion' will be suggested. |
| RelatedNames    | string              | none or one or many | A set of names which are related to the query text (if performing a textual search). For example, if searching for 'Lismore', the list of related names will suggest 'Lismore and Mocollop', 'Lismore Demesne', agus 'Lismore Road'. |

## `place`

The `place` object is at the core of the Logainm API: it represents a geographic location and includes associated toponymic, lexical, and other metadata. Queries specifying a place identifer in the request path will retrieve a single `place` object (if one exists) while broader queries may return one or more `place` objects in the response body.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The unique place identifier. |
| ReplacementID   | integer             | none or one         | If this value is set the requested place record has been merged into another record in the database. The value is the replacement record identifier. |
| DateCreated     | ISO 8601 datetime   | one                 | The date and time of entry creation.  |
| DateModified    | ISO 8601 datetime   | none or one         | The date and time of most recent modification to entry.  |
| Permalink       | string              | one                 | A permanent static hyperlink where a human reader can find more information about the place. This automatically redirects to the Irish or English version of the place information page. |
| Featured        | ISO 8601 datetime   | none or one or many | Denotes the date or dates on which this place was featured as the place of the day on the [logainm.ie](https://www.logainm.ie) website, if featured. |
| Cluster         | [`cluster`](#cluster) | none or one | Metadata representing a group of places, of which this place is a member, that share placenames and are colocated or are proximate to each other. |
| Placenames      | [`placename`](#placename) | one or many | One or more placenames, and associated metadata, that are given to this place. |
| Glossary        | [`glossary`](#glossary) | none or one | Describes words commonly found in Irish placenames and that are present in placenames associated with this place. |
| Categories        | [`category`](#category) | none or one or many | Describes the categories associated with this place. Only in exceptional cases will places have more than one category. |
| IncludedIn      | [`placeSummary`](#placeSummary) | none or one or many | Summary information regarding the administrative units (counties, civil parishes, etc.) which include this place. |
| Includes        | [`category`](#category) | none or one or many | Describes the place categories included within the bounds of this place. |
| Geography       | [`geography`](#geography) | none or one | Geographical location of the place expressed in terms of latitudinal and longitudinal coordinates. |
| GridReferences  | [`gridReference`](#gridReference) | none or one or many | Geographical location of the place expressed in terms of [Irish Grid Reference System](https://www.osi.ie/resources/reference-information-2/irish-grid-reference-system/) coordinates. |
| Gaeltacht       | [`placeProperty`](#placeProperty) | none or one         | Indicates whether the place is in the Gaeltacht. |
| PostOffice      | [`placeProperty`](#placeProperty) | none or one         | Indicates whether there is or was once a post office in this place. |
| NorthernIreland | [`placeProperty`](#placeProperty) | none or one         | Indicates whether this place is in Northern Ireland. |
| Images          | [`image`](#image)   | none or one or many | Describes one or more scanned records from the Placenames Branch archive relating to this place. |
| Resources       | [`resource`](#resource) | none or one or many | Describes one or more toponomy resources available on [logainm.ie](https://www.logainm.ie) relating to this place. |
| Links           | [`link`](#link) | none or one or many | Provides one or more links to related data in external resources. External resources include [OSI](https://www.osi.ie/), [Placenames Northern Ireland](http://www.placenamesni.org/), [Wikipedia](https://www.wikipedia.org/), [Geonames](http://www.geonames.org/), etc. |
| BornHere        | [`biographyLink`](#biographyLink) | none or one or many | Provides links to biographical data from [ainm.ie](https://www.ainm.ie) for any persons born in this place, if available. |
| Folklore        | [`folkloreLink`](#folkloreLink) | none or one or many | Provides links to folkloric data from [dúchas.ie](https://www.logainm.ie) associated with this place, if available. |
| SameAs          | [`sameAs`](#sameAs) | none or one or many | Specifies one or more co-references to this place in data sets other than the Placenames Database of Ireland. Consistent with OWL Web Ontology [SameAs](https://www.w3.org/TR/owl-ref/) definition. |

### `cluster`

Metadata representing a group of places that share placenames and are colocated or are proximate to each other.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| FocusID         | integer             | one                 | Identifies the place that forms the 'focus' of the cluster. It may represent the place category most readily associated with a particular placename or feature the richest set of metadata among all the cluster members. |
| Members         | [`clusterMember`](#clusterMember) | one or many         | Represents the individual places that make up the cluster. |

### `clusterMember`

Represents a member of a `cluster`.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| PlaceID         | integer             | one                 | The place identifier.     |
| Category        | [`category`](#category) | none or one         | The place category.      |

### `placename`

Describes a toponym associated with one or more places.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The placename identifier. |
| Language        | ISO 639-1 language code | none or one          | Indicates the language of the placename, if known. |
| Wording         | string              | one                 | The placename itself.     |
| Genetive        | string              | none or one         | In the case of Irish-language placenames this specifies the placename's grammatical form in the genitive case.     |
| Main            | boolean             | one                 | If true this is the place's main/canonical name. This is only important if the place has more than one name in the same language. |
| Acceptability   | [`acceptability`](#acceptability) | none or one         | Indicates the research and approval status of the placename. |
| Audio           | [`audio`](#audio)   | none or one         | Describes an audio file providing an indicative pronunciation of the placename. |
| SubNames        | [`subName`](#subName) | none or many       | A list of two or more discrete placenames. Provided when the parent placename is composed of two more or more names that are conjoined, e.g. [Rathgarvan or Clifden](https://www.logainm.ie/26783.aspx), or when part of the parent placename fulfils a qualifying or disambiguating role. |

### `acceptability`

Indicates the [research and approval status](https://www.logainm.ie/en/inf/help-notes) of a placename.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The acceptability status identifier. |
| TextEN          | string              | none or one         | An English-language label describing the acceptability status. |
| TextGA          | string              | none or one         | An Irish-language label describing the acceptability status. |

### `audio`

Describes an audio file providing an indicative pronunciation of a placename.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| FileName        | string              | one                 | The audio file name.      |
| Uri             | string              | one                 | The audio file URI.       |

### `subName`

A discrete name which may used in composing longer placenames.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Text            | string              | one                 | The text of the name.     |
| Disambiguates   | boolean             | one                 | If true, this name provides some form of disambiguation in respect of the parent placename. A disambiguating `subName` might, for example, distinguish the parent placename from other, similar names. |

### `placeSummary`

Summary information regarding a particular place.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The place identifier.     |
| NameEN          | string              | none or one         | The English-language placename. |
| NameGA          | string              | none or one         | The Irish-language placename. |
| Category        | [`category`](#category) | none or one         | The place category.      |

### `geography`

Expresses a geographical location in terms of latitudinal and longitudinal coordinates.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Accurate        | boolean             | one                 | Indicates whether the coordinates are believed to be precise. Inaccurate coordinates are those that have been obtained by extrapolation from neighbouring places. |
| Coordinates     | [`coordinates`](#coordinates) | one or many        | One or more pairs of latitudinal and longitudinal coordinates. Most places are represented by a single pair of coordinates. However, certain geographical features, such as rivers or islands, in particular, may have two or more pairs. |

### `coordinates`

Represents a pair of geographic coordinates.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Latitude        | double              | one                 | The latitudinal coordinate. |
| Longitude       | double              | one                 | The longitudinal coordinate. |

### `gridReference`

Expresses a geographical location in terms of [Irish Grid Reference System](https://www.osi.ie/resources/reference-information-2/irish-grid-reference-system/) coordinates.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Square          | string              | one                 | Specifies the grid square. |
| Easting         | long                | none or one         | Specifies the easting in the square. |
| Northing        | long                | none or one         | Specifies the northing in the square. |

### `placeProperty`

Describes a property of a particular place.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Extent          | string              | one                 | Specifies the extent to which the property applies to a particular place. If `all`, the property applies to the whole place. If `part`, the property only applies to some of the place. |

### `image`

Describes a scanned record from the Placenames Branch archive.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| FileName        | string              | one                 | The image file name.      |
| LabelEN         | string              | none or one         | An English-language description of the image category, if known. |
| LabelGA         | string              | none or one         | An Irish-language description of the image category, if known. |
| Uri             | string              | one                 | The image URI.            |

### `resource`

Describes a toponomy resource available on [logainm.ie](https://www.logainm.ie).

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The resource identifier.  |
| TypeID          | string              | one                 | Identifies the resource type. |
| TitleEN         | string              | none or one         | The resource's English-language title. |
| TitleGA         | string              | none or one         | The resource's Irish-language title. |
| PageReference   | string              | none or one         | Specifies the page or pages within the resource associated with a particular place, if applicable. |
| Supplier        | [`supplier`](#supplier) | none or one         | Metadata regarding the publisher/supplier of the resource. |

#### `TypeID`

This possible values of the `TypeID` property are as follows:

| Value           | Description               |
| :-------------- | :------------------------ |
| jpg             | A JPEG image.             |
| pdf             | A PDF document.           |
| zip             | A ZIP file.               |

### `supplier`

Metadata regarding the publisher/supplier of a toponmy resource.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The supplier identifier.  |
| NameEN          | string              | none or one         | The supplier's English-language name. |
| NameGA          | string              | none or one         | The supplier's Irish-language name. |

### `link`

Provides a link to related data in an external resource.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Type            | string              | one                 | The external resource type. External resources include [OSI](https://www.osi.ie/), [Placenames Northern Ireland](http://www.placenamesni.org/), [Wikipedia](https://www.wikipedia.org/), [Geonames](http://www.geonames.org/), etc. |
| Target          | string              | one                 | The link target. This may be a URI, URL, or other identifier, depending on the resource type. |

#### `Type`

This possible values of the link type property are as follows:

| Value           | Description               |
| :-------------- | :------------------------ |
| Geonames        | The link is a URL for a [Geonames](http://www.geonames.org/) entry. |
| Osi             | The link is an [Ordnance Survey Ireland](https://www.osi.ie/) resource identifier. |
| PlacenamesNi    | The link is a [Placenames Northern Ireland](http://www.placenamesni.org/) resource identifier. |
| WikipediaEn     | The link is a URL for an English-language [Wikipedia](https://www.wikipedia.org/) entry. |
| WikipediaGa     | The link is a URL for an Irish-language [Wikipedia](https://www.wikipedia.org/) entry. |

### `biographyLink`

Provides links to biographical data from [ainm.ie](https://www.ainm.ie) for any persons born in a particular place.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The biography's ainm.ie identifier.  |
| Title           | string              | one                 | The biography title.      |
| Uri             | string              | one                 | The URI for the ainm.ie biography. |

### `folkloreLink`

Provides a link to folkloric data from [dúchas.ie](https://www.duchas.ie) associated with a particular place.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Type            | string              | one                 | The external resource type. At present this will always describe resources from the Dúchas project. |
| UriEN           | string              | one                 | The URI for the folkloric data resource (English-language interface). |
| UriGA           | string              | one                 | The URI for the folkloric data resource (Irish-language interface). |

### `sameAs`

Specifies a co-reference to a particular place in data sets other than the Placenames Database of Ireland. Consistent with OWL Web Ontology [SameAs](https://www.w3.org/TR/owl-ref/) definition.

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| Uri             | string              | one                 | The URI of the external resource. |

## `category`

Describes a place category. Categories encompass both [administrative units](https://www.logainm.ie/en/inf/help-categs) and geographical features. One or more categories may be returned as part of a `place` object or a reference list of `category` objects may be obtained from the appropriate API [endpoint](./README.md#resource-paths).

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | string              | one                 | The category identifier.  |
| NameEN          | string              | none or one         | The English-language category name. |
| NameGA          | string              | none or one         | The Irish-language category name. |
| NamePluralEN    | string              | none or one         | The English-language category name plural form. |
| NamePluralGA    | string              | none or one         | The Irish-language category name plural form. |
| Count           | integer             | none or one         | The number of placenames associated with this category, if known. |

## `glossary`

Describes a set of related words commonly found in Irish placenames. One or more glossary entries may be returned as part of a `place` object or a reference list of `glossary` objects may be obtained from the appropriate API [endpoint](./README.md#resource-paths).

| Property name   | Type                | Cardinality         | Description               |
| :-------------- | :------------------ | :------------------ | :------------------------ |
| ID              | integer             | one                 | The glossary entry identifier.  |
| Headword        | string              | one                 | The glossary entry headword. |
| Translation     | string              | none or one         | An English-language translation of the glossary headword. |
| Forms           | string              | none or one or many | Alternate spellings of the glossary headword. |
| Count           | integer             | none or one         | The number of placenames associated with this glossary entry, if known. |
