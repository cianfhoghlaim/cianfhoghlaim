# The Data Structure of the National Folklore Collection *Main Manuscript Collection*

The *Main Manuscript Collection* is one of five major collections of folklore held by [Cnuasach Bhéaloideas Éireann/the National Folklore Collection](https://www.ucd.ie/irishfolklore/en/) (NFC), University College Dublin (UCD), and comprises 2,400 bound volumes of material collected since 1932. Full- and part-time collectors compiled the majority of these under the auspices of the Irish Folklore Commission (1935–1971). Approximately two thirds of the material is in Irish and it includes every aspect of the Irish oral tradition.

This collection is currently being digitised as part of the Dúchas project by [Fiontar & Scoil na Gaeilge](http://www.dcu.ie/fiontar_scoilnagaeilge/) (FSG), Dublin City University (DCU), in conjunction with the NFC. The digitisation will produce (1) a collection of scanned images and (2) an XML data set that indexes and annotates the images. This document describes the data structure used in the XML data set.

## Table of Contents  

1. [Introduction](#introduction)  
2. [Volumes](#volumes)  
3. [Pages](#pages)  
4. [Parts](#parts)  
5. [Items](#items)  
6. [Topics](#topics)  
7. [Note types](#notetypes)  
8. [References to persons](#references-to-persons)
9. [Dates](#dates)
10. [Consistency with CBÉS data structure](#consistency-with-cbÉs-data-structure)

## Introduction 

A similar process to digitise the NFC *Schools' Collection* (hereafter referred to as CBÉS) and *Photographic Collection* (hereafter referred to as CBÉG) was previously undertaken during the period 2013–2017, also under the auspices of the Dúchas project. The results of this work have been made publicly available at [www.duchas.ie](https://www.duchas.ie) and are in the process of being archived for preservation by the [UCD Digital Library](https://digital.ucd.ie/).

This present document is heavily indebted to a previous specification of the CBÉS data structure, *The Data Structure of Bailiúchán na Scol*, authored by [Michal Boleslav Měchura](http://www.lexiconista.com) in 2013. There is good reason for this: the data structure of the *Main Manuscript Collection* (hereafter referred to as CBÉ) will be, to a large extent, a more generalised adaptation of the CBÉS data structure. This will aid future developments as part of the Dúchas project (see [Consistency with CBÉS data structure](#consistency-with-cbÉs-data-structure) below).

It should be noted that the data structure outlined in this document represents the internal data structure for the CBÉ database and not an authoritative schema for encoding folkloristic or archival data. Not all elements of the CBÉ data structure will be made publicly available and the data may be variously restructured or transformed for presentation on the dúchas.ie website or for dissemination via the forthcoming Dúchas application programming interface (API). It should also be possible to reconstruct the data according to other specifications, such as the Metadata Object Description Schema (MODS) or those provided by the Text Encoding Initiative (TEI), as required.  

### Changed understandings since developing the CBÉS data structure

#### Developments in relation to the storage, retrieval and dissemination of image media
The CBÉS data structure references individual image files where each page in a volume is associated with a set of images at various sizes:

```xml
<fileNameBig default="CBES_0085\CBES_0085_1A.jpg" />
<fileNameSmall default="CBES_0085\CBES_0085_1A_t.jpg" />
```

This convention may no longer be optimal for the following reasons:

- Images need to be served at a flexible range of sizes. Since September 2017, the dúchas.ie website features a responsive design and it is intended to add to the range of image sizes served in order to better cater for a wide range of user devices. The number and variety of images offered is likely to change over time.
- With [IIIF media standards](http://iiif.io/) and server technology coming on stream, it may soon no longer be necessary or desirable to retain multiple static copies of images in local storage.

Instead, it is proposed that the XML code for CBÉ will reference a single authoritative image file. Paths to derivate images can be constructed at the application level using string replacement operations.

#### Editorial tooling
Editorial work for CBÉS was carried out the Léacslann editorial system previously developed by FSG. As was the case for CBÉG, however, it is proposed to annotate the CBÉ volumes in a newer editorial system, Ardán. While this is an application-level concern, and is thus outside the scope of this document, there is no doubt that the possibilites afforded by Ardán's more flexible data manipulation tools have influenced the data structure design.

#### Additive metadata models
Various aspects of the CBÉS data structure preferred a boolean or either/or approach to certain metadata. For example, stories in CBÉS were marked as being either Irish-language, English-language, or mixed-language texts. In many cases such as this the CBÉ data structure will provide for an additive or tag-based approach where, for instance, one or many or no languages may be assigned to a given item in each volume. This is a function of both the wider scope of the CBÉ collection - which encompasses, to continue from the previous examples, some texts in Manx, Breton, and other languages, as well as non-linguistic materials - and evolving internal editorial practices.

#### Additional metadata
The data structure of the CBÉG collection introduced a number of new annotation options, as compared with CBÉS. These include structured references to international locations via the [Geonames](http://www.geonames.org/) API; more granular date annotations; annotations with reference to the CBÉD database (see [References to persons](#references-to-persons) below); format and other image metadata, as well as; an additional topic/subject taxonomy. It is proposed to port many of these additional metadata features to CBÉ, as well as some others that will be specific to the new collection.

### Overview of the CBÉ data structure

The CBÉ collection consists of stories, accounts, questionnaires, diaries and other materials which have been physically bound into volumes. Clearly, there is a great degree of variabilty in the composition of each volume. Some volumes contain the work of a single collector, while others feature multiple collectors and multiple informants and may be collected in various locations. 

Each volume is represented in the data set by a `pVolume` (GA: *imleabhar*) record, and each page by a `pPage` (GA: *leathanach*) record. Each `pPage` record contains a reference to a `pVolume` record to tell you which volume the page is in. Each `pPage` record also contains a reference that identifies scanned images of the page.

Together, `pVolume` and `pPage` records represent the collection’s **physical structure** (hence the prefix `p`). In parallel to the physical structure, a **logical structure** exists which annotates and indexes the physical structure. It consists of `lPart` records and `lItem` records (notice the prefix `l`).

An `lPart` record (GA: *cuid*) represents a distinct section within a manuscript volume and may have originally been physically separate from the other contents of the volume. It is consonant with the [`msPart`](http://www.tei-c.org/release/doc/tei-p5-doc/en/html/MS.html#mspt) element as specified in the TEI P5 Guidelines. It contains a reference to a `pVolume` record to tell you which volume the manuscript part is in, and a reference to a `pPage` record within that volume that represents the manuscript part’s title page. An `lPart` record may also contain data about the location where the material was collected, the collector(s) who sourced the material, and so on.

An `lItem` (GA: *mír*) record represents a discrete work, such as a story or diary entry. It is consonant with the TEI [`msItem`](http://www.tei-c.org/release/doc/tei-p5-doc/en/html/MS.html#mscoit) element. It contains a reference to its parent `lPart` record and to one or more `pPage` records. Notice that mapping between items and pages is many-to-many: an item can span over several pages and a page can accommodate several items. An `lItem` record also contains detailed data about the people who were involved in its writing, the subject it pertains to and other data.

In addition to the physical and logical structure, several auxiliary record types exist in the data set which serve as look-up lists. These include `person` records, `topic` records and `noteType` records. Their names do not have a prefix.

Each entry in the data set consists of an ID number and an XML document of one of types mentioned above (`pVolume`, `lPart` etc). An element within an XML document may refer to another XML document with its ID number.

Each record type is described in detail below.

### Relationships of inheritance within volumes

In many cases where, for example, all of the parts in a volume were collected in a single location or many of the items in a manuscript part were obtained by the same collector, it may be beneficial to allow `lPart` or `lItem` records to 'inherit' certain metadata from part to which they belong. Such an approach may be an aid to the progress of the editorial annotation work. Relationships of inheritance, as such, are *implicitly* defined within the data structure and are facilitated within the editorial tooling as an application-level concern. For these purposes, the application will assume that pages inherit certain metadata from the items to which they are linked; items are deemed to inherit certain metadata from their parent manuscript part. The following metadata (defined in next section) are inheritable:

- `<locationIreland>`
- `<locationAbroad>`
- `<collectors>`
- `<informants>`
- `<relevantPersons>`
- `<relevantCollections>`
- `<relevantPublications>`

It is necessary to provide for edge cases where, for example, one story in a long series of manuscript items was collected by a person other than the collectors associated with the parent part. Obviously, instances such as this must not be understood to inherit factually incorrect metadata. To this end, an `<override>` element can be placed in either `<lItem>` or `<pPage>` documents. An `<override>` element denotes that a particular property (named in an element attribute) should *not* be inherited from any parent document. This has the disadvantage of introducing what is a non-descriptive or negating element to an otherwise entirely descriptive data structure, but it was deemed to be the least brittle approach and allows for maximum flexibility in terms of future ammendments to the schema.

## Volumes

### Example

Entry ID 231579

```xml
<pVolume>
  <volumeNumber>0109</volumeNumber>
  <status>3</status>
  <owner task="index">26</owner>
  <owner task="check">14</owner>
  <notes></notes>
</pVolume>
```

### `<pVolume>`

Represents a volume.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<volumeNumber>`| exactly one | The volume's number/code |
| `<status>`    | exactly one   | A status code that tells how far advanced annotation on this volume is |
| `<owner>` | one or more | The ID of a user who is charge of annotating this volume |
| `<notes>` | none or one | Internal notes |

### `<notes>`

Stores internal notes.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<note>`      | one or more   | An internal note |

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@task`         | required      | string       | Denotes the editorial task assigned to the volume owner |

## Pages

### Example

Entry ID 331620

```xml
<pPage>
  <image>
    <fileName>CBE_0085\CBE_0085_209.jpg</fileName>
  </image>
  <volume id="4344035"></volume>
  <pageNumber>209</pageNumber>
  <listingOrder>209</listingOrder>
  <condition>
    <conditionDescription>2</conditionDescription>
  </condition>
  <notes></notes>
</pPage>
```

### `<pPage>`

Represents a scanned page.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<image>`     | exactly one   | Data relating to the scanned image file |
| `<volume>`    | exactly one   | Which volume is this page in? |
| `<pageNumber>`| exactly one   | What page number is written on this page? |
| `<listingOrder>` | exactly one | What is the listing order of this page in this volume? This is often, but not always, identical to the page number as written on the page itself || `<languages>` | none or one   | What languages are used in the manuscript part? |
| `<override>`  | none or one or more | Indicates that a property normally inherited from a `<lPart>` or `<lItem>` element should not be applied to the current page  |
| `<locationIreland>` | none or one or more | Represents a place in Ireland that is associated with this page |
| `<locationAbroad>` | none or one or more | Represents a place outside of Ireland that is associated with this page |
| `<collectors>`    | none or one   | Who collected the content on this page? |
| `<informants>` | none or one   | Who provided the content on this page? |
| `<condition>` | none or one   | Description of the page's physical condition |
| `<notes>`     | exactly one   | Internal notes |

### `<image>`

Represents an image file and any associated image metadata.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<fileName>`  | exactly one   | The name of the image file |

### `<volume>`

A reference to the volume with which this page is associated.

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@id`           | required      | integer      | The ID number of a `<pVolume>` entry |

### `<condition>`

Represents the physical condition of the page.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<conditionDescription>` | one or more   | What is the physical condition of the page? |

## Parts

### Example

Entry ID 4667213

```xml
<lPart>
  <volume id="4360513">
    <listingOrder>2</listingOrder>
  </volume>
  <titlePage id="4360522"></titlePage>
  <locationIreland>
    <county>100001</county>
    <georefIreland>103891</georefIreland>
  </locationIreland>
  <locationAbroad>
    <country>BE</country>
    <georefAbroad>2784804</georefAbroad>
  </locationAbroad>
  <collectors>
    <person>80607834</person>
  </collectors>
  <relevantPublications>
    <publication doi="10.2307/20521241">
      Ó Broin, Tomás. "Scéalaí Tíre: Bailiúchán Seanchais ó Ghaillimh." 
      <pubTitle>Béaloideas</pubTitle> 24 (1955): Ii-133.
    </publication>
  </relevantPublications>
  <notes></notes>
</lPart>
```

### `<lPart>`

Represents a distinct section within a manuscript volume.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<volume>`    | exactly one   | Which volume is this part in? |
| `<titlePage>` | one or more   | A reference to the manuscript part's title pages or beginning pages |
| `<languages>` | none or one   | What languages are used in the manuscript part? |
| `<locationIreland>` | none or one or more | Represents a place in Ireland that is associated with this part |
| `<locationAbroad>` | none or one or more | Represents a place outside of Ireland that is associated with this part |
| `<collectors>`    | none or one   | Who collected this content? |
| `<informants>` | none or one   | Who provided this content? |
| `<relevantCollections>` | none or one   | Are any other NFC collections referenced by this content? |
| `<relevantPublications>` | none or one | Has the content of this manuscript part been published or discussed elsewhere? |
| `<notes>` | exactly one | Internal notes |

### `<page>`

A reference to the manuscript part's title page.

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@id`           | required      | integer      | The ID number of a `<pPage>` entry |

### `<languages>`

Stores a list of languages found within particular content.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<language>`      | one or more   | An ISO 639-2 language code |

### `<locationIreland>`

Represents a place in Ireland.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<county>`    | exactly one   | Which county is associated with this place? (Logainm ID) |
| `<georefIreland>`| none or one or more   | The Logainm ID associated with a particular place |

### `<georefAbroad>`

Represents a place outside of Ireland.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<country>`    | exactly one   | Which country is associated with this place? (ISO 3166-1 Alpha-2 code) |
| `<georefAbroad>`| none or one or more   | The Geonames ID associated with a particular place |

### `<collectors>`

Stores a list of folklore collectors.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<person>`    | none or one or more | The ID number of a CBÉD entry |

### `<informants>`

Stores a list of informants.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<person>`    | none or one or more | The ID number of a CBÉD entry |

### `<relevantCollections>`

Stores a list of references to other NFC collections.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<collection>` | one or more   | Reference to another NFC collection |

### `<relevantPublications>`

Stores a list of publications associated an entry.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<publication>` | one or more | Reference citing a publication outside of dúchas.ie |

### `<publication>`

Represents a publication.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<pubTitle>`     | one or more   | Represents a publication title |

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@doi`          | optional      | string       | The [digital object identifier](https://www.doi.org/) (DOI) of a publication, if available |
| `@url`          | optional      | string       | The URL of a publication. If a DOI is available do not provide a URL. |

## Items

### Example

Entry ID 551579

```xml
<lItem>
  <part id="4427865">
    <listingOrder>1</listingOrder>
  </part>
  <pages>
    <page id="4360522"></page>
    <page id="4360523"></page>
  </pages>
  <title>Oíche an tSneachta Mhóir 2018</title>
  <date>
    <year>2018</year>
    <month>03</month>
    <day>01</day>
  </date>
  <languages>
    <language>ga</language>
  </languages>
  <contentDescription type="SEAN">
    <mode>LÁMH</mode>
    <script>LATG</script>
  </contentDescription>
  <topics></topics>
  <collectors>
    <person>80607834</person>
  </collectors>
  <informants>
    <person>80607834</person>
    <person>80607834</person>
  </informants>
  <relevantPersons>
    <person>80607834</person>
  </relevantPersons>
  <extraInfo status="EDIT">
    <text lang="ga"></text>
    <text lang="en"></text>
  </extraInfo>
  <relevantCollections>
    <collection id="cbeg"></collection>
  </relevantCollections>
</lItem>
```

### `<lItem>`

Represents a discrete work within a volume or within a part of a volume.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<part>`      | exactly one   | Which part of the volume is this item in? |
| `<pages>`     | exactly one   | What pages are associated with this item? |
| `<title>`     | none or one   | The title given to the item, if it exists |
| `<item>`      | none or one or more | Is this item linked to another item, i.e. is it part of a series of items such as a story spread over several volumes? |
| `<date>`      | none or one   | The date the item was recorded |
| `<languages>` | none or one   | What languages are used in the item? |
| `<contentDescription>` | exactly one   | Represents specific properties of the item's content |
| `<override>`  | none or one or more | Indicates that a property normally inherited from a `<lPart>` element should not be applied to the current item or its associated pages  |
| `<topics>`    | exactly one   | What topics describe this item's content? |
| `<locationIreland>` | none or one or more | Represents a place in Ireland that is associated with this item |
| `<locationAbroad>` | none or one or more | Represents a place outside of Ireland that is associated with this item |
| `<collectors>` | exactly one   | Who collected this content? |
| `<informants>` | exactly one   | Who provided this content? |
| `<relevantPersons>` | none or one   | Stores a list of persons who are referenced within the item text or who are relevant to the item text. |
| `<extraInfo>` | exactly one   | Additional free-form text or commentary that cannot be captured as structured data |
| `<relevantCollections>` | none or one   | Are any other NFC collections referenced by this content? |
| `<relevantPublications>` | none or one   | Has the content of this manuscript part been published or discussed elsewhere? |
| `<notes>`     | exactly one | Internal notes |

### `<part>`

A reference to the part with which this item is associated.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<listingOrder>` | one or more   | Represents a publication title |

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@id`           | required      | integer      | The ID number of a `<lPart>` entry |

### `<pages>`

Stores a list of pages associated with an item.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<page>`      | one or more   | The ID number of a `<pPage>` entry |

### `<item>`

Represents a linked item.

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@id`           | required      | integer      | The ID number of the linked item |
| `@sequence`     | none or one   | string       | Defines a sequential relationship with the current `<lItem>` |

### `<contentDescription>`

Represents specific properties of the item's content.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<mode>`      | none or one or more | Represents the writing mode, i.e. handwritten or typed |
| `<script>`    | none or one or more | Represents the writing script, i.e. Roman or Gaelic script, according to the ISO 15924 standard |

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@type`         | required      | string       | Denotes a CBÉ content type, such as story, diary entry, questionnaire, etc. |

### `<relevantPersons>`

Stores a list of persons who are referenced within the item text or who are relevant to the item text.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<person>`    | none or one or more | The ID number of a CBÉD entry |

### `<extraInfo>`

Additional free-form text or commentary that cannot be captured as structured data.

#### Child elements

| Name          | Cardinality   | Description  |
| ------------- |---------------|--------------|
| `<text>`      | one or more   | Free-form text |

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@status`       | required      | string       | Is this text suitable for publication? |

### `<text>`

Free-form text.

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@lang`         | required      | string       | An ISO 639-2 language code |

## Topics

Topics metadata is not currently specified as part of the CBÉ data structure. Work is under way to develop the most efficient system to integrate the different topic taxonomies available with the CBÉ data set. It is proposed that CBÉ items will annotated with topics on a second editorial pass.

## Note types

### Example

```xml
<noteTypes>
  <noteType code="ÁBHAR" title="Ceist faoin ábhar" />
</noteTypes>
```

### `<noteType>`

Represents a note type.

#### Attributes

| Name            | Optionality   | Value type   | Description  |
| ----------------|---------------|--------------|--------------|
| `@code`         | required      | string       | The internal system code associated with this note type |
| `@title`        | required      | string       | The user-friendly title ascribed to this note type |


## Dates

Dates may be referenced within the CBÉ data structure for several reasons. To allow the greatest flexibility, the `<date>` element provides for a number of different scenarios.

### Known dates

```xml
<date>
  <year>2002</year>
  <month>01</month>
  <day>18</day>
</date>
```

Known dates may include as few as one element (`<year>`) and as many as three elements.

### Qualified dates

```xml
<date qualifier="INFER">
  <month>02</month>
  <day>09</day>
</date>
```

The `@qualifier` attribute will accept a range of values consistent with the [date qualifiers specified in MODS v3](https://www.loc.gov/standards/mods/v3/mods-userguide-generalapp.html#list). These are `APPROX` (a date that may not be exact), `INFER` (the date has not been transcribed directly from a resource, but is a reasonable assumption), and `QUESTION`(the date is questionable).

### Periods of time

```xml
<date>
  <startDate>
    <year>1940</year>
  </startDate>
  <endDate>
    <year>1949</year>
  </endDate>
</date>
```
This can be used to demarcate a span of time and all standard `<date>` child elements for days, months and years are permitted.

## References to persons

Persons named within the CBÉ metadata will be identified by reference to objects in the *Persons Database* (hereafter CBÉD). Given that many persons appear in several NFC collections - some photographers in CBÉG are also collectors in CBÉ, for example - objects in CBÉD serve as a single source of truth for personal metadata across the entire data set. Persons in CBÉ metadata are referenced by their CBÉD ID, stored in a `<person>` element.

The CBÉD data structure will be expanded to account for the elements described below.

### Example

```xml
<person>
  <name>Seán <surname>Ó hEochaidh</surname></name>
  <bio>1714</bio>
  <viaf>1740563</viaf>
  <gender>m</gender>
  <birthPlace>
    <locationIreland>
      <county>100013</county>
      <georefIreland>14651</georefIreland>
    </locationIreland>
  </birthPlace>
  <birthDate>
    <date>
      <year>1913</year>
      <month>02</month>
      <day>09</day>
    </date>
  </birthDate>
  <deathDate>
    <date>
      <year>2002</year>
      <month>01</month>
      <day>18</day>
    </date>
  </deathDate>
  <address>
    <locationIreland>
      <county>100013</county>
      <georefIreland>14651</georefIreland>
    </locationIreland>
  </address>
  <address>
    <locationIreland>
      <county>100013</county>
      <georefIreland>1416587</georefIreland>
      <text>Gort a' Choirce, Dún na nGall</text>
    </locationIreland>
  </address>
  <index collection="CBE">
    <collectors>
      <collector>315676427</collector>
    </collectors>
    <volumeNumber>1706</volumeNumber>
    <startPage>207</startPage>
    <endPage>268</endPage>
    <age>22</age>
  </index>
  <occupations>
    <occupation>22</occupation>
  </occupations>
  <notes></notes>
</person>
```

### `<person>`

Represents a person.

#### Child elements

| Name            | Cardinality   | Description  |
| ----------------|---------------|--------------|
| `<name>`        | one or more   | The person's full name. The first name in the tree will taken as the person's authoritative name |
| `<bio>`         | none or one   | The person's [Ainm.ie](https://www.ainm.ie) biography ID |
| `<viaf>`        | none or one   | The person's [Virtual International File Authority](http://viaf.org/) ID |
| `<gender>`      | none or one   | The person's gender |
| `<birthPlace>`  | none or one   | The person's place of birth |
| `<birthDate>`   | none or one   | The person's date of birth |
| `<deathDate>`   | none or one   | The person's date of death |
| `<address>`     | none or one or more | A physical address associated with the person |
| `<occupations>` | none or one or more | Any occupations associated with the person |
| `<notes>`       | none or one or more | Any editorial notes |

## Consistency with CBÉS data structure

As stated previously, the CBÉ data structure was designed as a generalised version of the earlier CBÉS data structure. There are two primary reasons for this:

- It is proposed to move the CBÉS collection from FSG's older editorial platform, Léacslann, to our most up-to-date system, Ardán. A consistent data structure between both collections means they can share the same editorial interface.
- A consistent data structure for CBÉ and CBÉS reduces complexity and makes it easier to provide and maintain facilities such as the forthcoming Dúchas API.

It may indeed be possible to programmatically transform the CBÉS XML structure so that it is fully uniform with the generalised CBÉ structure. For example, CBÉS-specific elements such as `<teacherName>` might be mapped onto general CBÉ elements such as `<collectors type="teacher">`. Thus, complexity at the application level could be greatly reduced.
