---
title: Easpórtáil go TBX
shortTitle: Easpórtáil TBX
description: Conas cnuasach téarmaíochta a easpórtáil as Terminologue go TBX
keywords: téarmaíocht, taighde, bogearraí, foinse oscailte, javascript, Node JS, Fiontar & Scoil na Gaeilge, DCU
resource: Terminologue
github: https://github.com/gaois/terminologue
order: 5
public: true
---

Formáid caighdeánach é TBX (Termbase Exchange) atá aitheanta go forleathan i dtionscal na téarmeolaíochta chun sonraí téarmaíochta a mhalartú idir bogearraí. Is iomaí bogearra atá ábalta sonraí a easpórtáil agus a iompórtáil ó/go dtí an fhormáid seo, agus tá Terminologue ina measc. Déanfaidh muid cur síos sa doiciméad seo ar an dóigh ar féidir sonraí a easpórtáil as Terminologue go TBX.

## Easpórtáil ar líne

Tá áiseanna ar fáil in Terminologue, sa chomhéadan eagarthóireachta, chun cnuasach nó cuid de chnuasach a easpórtáil go TBX:

- Sa scáileán *Cumrú* de gach cnuasach, tá rogha *Easpórtáil TBX* ar fáil. Faoi sin, is féidir an cnuasach iomlán a íoslódáil mar chomhad TBX. Má tá níos mó má 1,000 iontráil sa chnuasach, beidh an íoslódáil le fáil in iliomad comhad TBX, 1,000 iontráil an ceann (beidh na hiontrálacha curtha in ord de réir a ID).

- Ar scáileán eagarthóireachta an chnuasaigh, sa liosta iontrálacha ar chlé, tá cnaipe ag bun an liosta chun gach iontráil ar an liosta sin a íoslódáil i bhformáid TBX. Is féidir leat liosta na n-iontrálacha a shaincheapadh le cuardach ar bith, agus an fothacar sin den chnuasach a íoslódáil ansin. Má tá liosta torthaí níos faide ná leathanach amháin, is é *inneachar an leathanaigh reatha* a íoslódálfar tar éis duit cliceáil ar an chnaipe.

## Easpórtáil as líne

Más fearr leat, is féidir leat cnuasach a íoslódáil go dtí do ríomhaire (ón scáileán *Cumrú*) agus ansin é a easpórtáil go TBX le script. Tá an script le fáil sa stórlann faoi `exportimport/tbx-export.js`. Sa teirminéal (má tá tú ar GNU/Linux) nó sa leid ordaithe (má tá tú ar Microsoft Windows), téigh chuig an bhfochomhadlann `exportimport` agus ansin rith `node tbx-export.js`.

Roimhe sin, áfach, caithfidh tú an script a chumrú. Oscail an script in eagarthóir téacs agus athraigh na hathróga ag tús an chomhaid de réir mar is cuí:

```javascript
const SQLITEFILE="../data/termbases/mytermbase.sqlite";
const TBXFILE="mytermbase.tbx";
const LIMIT=10000;
```

- `SQLITEFILE` is ea an chonair chuig do chóip logánta den chnuasach a d'íoslódáil tú ón scáileán *Cumrú*.
- `TBXFILE` is ea ainm (agus conair) den chomhad TBX a chruthófar.
- `LIMIT` is ea uasteorainn ar líon na n-iontrálacha a easpórtálfar.

## An cineál TBX a easpórtáiltear

Sa chuid eile den doiciméad seo mínítear struchtúr na gcomhad TBX a easpórtáiltear as Terminologue. Nuair a easpórtálann tú cnuasach as Terminologue go TBX, tá an comhad géilliúil do TBX leagan 2, de réir chaighdeán [ISO 30042:2008](https://www.gala-global.org/sites/default/files/migrated-pages/docs/tbx_oscar_0.pdf). Tá leagan níos nua ann freisin, TBX leagan 3 ([ISO 30042:2019](https://www.tbxinfo.net/)), ach níl na comhaid a easpórtáiltear as Terminologue géilliúil dó sin.

Má tá a fhios agat gur TBX atá sna comhaid agus cén leagan de TBX, seans gur leor duit an méid eolais sin. Ach:

- Caighdeán leathan go leor é TBX a bhfuil an-cuid rudaí ceadaithe ann. Na comhaid TBX a easpórtáiltear as Terminologue, ní bhaineann siad leas ach as fothacar de na nithe atá ceadaithe in TBX. B'fhéidir gur mhaith leat a thuiscint cad é an fothacar é sin.

- Ní ionann samhail na sonraí in TBX agus samhail na sonraí in Terminologue. Tá a struchtúr féin sna hiontrálacha in Terminologu nach bhfreagraíonn go docht do struchtúr iontrálacha in TBX. Mar sin, b'fhéidir gur mhaith leat tuiscint a fháil ar an mhapáil idir an dá rud, go dtuige tú cá háit ar féidir go gcaillfí rud éigin san aistriú.

## The TBX file

```xml
<?xml version="1.0" encoding="UTF-8"?>
<martif type="TBX" xml:lang="ga">
  <martifHeader>
    <fileDesc>
  	<titleStmt>
  	  <title>My Termbase</title>
  	</titleStmt>
  	<sourceDesc>
  	  <p>This is a sample termbase created in Terminologue and exported into TBX.</p>
  	</sourceDesc>
    </fileDesc>
  </martifHeader>
  <text>
    <body>
  	  <termEntry>...</termEntry>
  	  <termEntry>...</termEntry>
  	  <termEntry>...</termEntry>
    </body>
  </text>
</martif>
```

The value of the `martif@xml:lang` attribute is the abbreviation of the first language listed in your termbase configuration in Terminologue *(Configuration > Languages)*. For the purposes of TBX export, this language is the **termbase language**. Most metadata elements further down the TBX file are in this language.

The title (in the `title` element) is taken from the *name* in the Termbase configuration *(Configuration > Name and blurb)*. Termbase titles in Terminologue can be multilingual: there can be multiple titles, one in each language. The title exported into TBX is the one in the **termbase language**.

The description (in `sourceDesc/p`) is taken from the *blurb* in the termbase configuration and is in the **termbase language**. It may be blank in the TBX file if there is no *blurb*.

## Entries

```xml
<termEntry id="eid-948718">
    <descrip type="subjectField">Law</descrip>
    <langSet xml:lang="en">
        <ntig>
            <termGrp>
                <term>award</term>
                <termNote type="partOfSpeech">s</termNote>
            </termGrp>
        </ntig>
        <descrip type="example">An award may, with the leave of the Court...</descrip>
    </langSet>
    <langSet xml:lang="ga">
        <ntig>
            <termGrp>
                <term>dámhachtain</term>
                <termNote type="partOfSpeech">bain3</termNote>
            </termGrp>
        </ntig>
        <descrip type="definition">cinneadh críochnaitheach eadránaí</descrip>
        <descrip type="example">Féadfar, le cead ón gCúirt, agus ar cibé téarmaí is cóir...</descrip>
    </langSet>
</termEntry>
```

Each entry is enclosed in `termEntry`. Its `@id` consists of the string `eid-` followed by the numerical ID of this entry in Terminologue.

There is a `langSet` element for each language for which the entry has at least one term, definition, example sentence or intro. The `@xml:lang` attribute is the abbreviation of that language in the termbase configuration.

Inside each `langSet` element you will always find one or more terms, encoded as `ntig` elements. Note that the TBX standard allows terms to be encoded either as (simple) `tig` or as (complex) `ntig`. In the TBX exported from Terminologue, terms are always encoded as `ntig` and the actual wording of the term is always found in `ntig/termGrp/term`.

In Terminologue it is possible for a term to be shared by more than one entry. There is no equivalent for term sharing in TBX. So, when a term is shared by two, three or more entries in Terminologue, it will be exported into TBX two, three or more times, inside each of its entries.

All other data, such as domain labels, definitions, example sentences and grammatical annotations, are exported into TBX either as `descrip` elements or as `termNote` elements, and appear in the TBX entry either at the entry level (as children of `termEntry`), at the language level (as children of `langSet`) or at term level (as children of `termGrp`).

The TBX standard allows for many other XML element names in addition to those mentioned here, but Terminologue never exports them.

## Terms

```xml
<ntig>
    <termGrp>
        <term>compulsory purchase order</term>
        <termNote type="partOfSpeech">s</termNote>
    </termGrp>
</ntig>
```

The `ntig` element always contains exactly one child, the `termGrp` element. The `termGrp` always contains exactly one `term` element, and may contain zero, one or more `termNote` elements. The `term` element contains the wording of the term. The language of the term can be found in the `@xml:lang` attribute of the `ntig`'s parent `langSet` element.

### Term annotations

In Terminologue, a *term annotation* is a label (typically: a part-of-speech label) which is attached either to an entire term or to a substring of the term. Term annotations are always exported as `<termNote>` elements and are always children of `<termGrp>` (and therefore siblings of `<term>`).

- Term annotations which are part-of-speech labels or inflection labels are exported as `<termNote type="partOfSpeech">...</termNote>`. The text inside the tags is the label's abbreviation.

- Term annotations which are language-of-origin labels are exported as `<termNote type="etymology">...</termNote>`. The text inside the tags is the language label's abbreviation.

- Term annotations which are trademark labels (™) or registered trademark labels (®) are exported as `<termNote type="proprietaryRestriction">trademark</termNote>`.

- Term annotations which are proper-noun labels (¶) are exported as `<termNote type="partOfSpeech">properNoun</termNote>`.

- Term annotations which put the term (or a substring of the term) in italics are **not** exported into TBX.

In the TBX exported from Terminologue, it is impossible to find out whether a `<termNote>` (and the *term annotation* it originated from) applies to the entire term or to a substring of the term: this information is **not** exported. Theoretically, it would be possible to encode this information in TBX using TBX's notion of term components (`<termComp>`). However, we have decided not to implement this in the TBX files exported from Terminologue because we suspect that this (i.e. attaching labels to substrings of terms as opposed to entire terms) is a rarely used option.

### Inflected forms

In Terminologue it is possible for a term to have a list of inflected forms of itself. There is no equivalent for this in TBX, so inflected forms are **not** exported into TBX. One could probably find a way to encode inflected forms in TBX somehow, for examples as `<termNote>`, but we have decided not to do this.

### Clarifications

In Terminologue, a term can be accompanied by a clarification, which is a short piece of text which clarifies which meaning of the term or which sense of the term is being evoked in that particular entry. This is exported as `<termNote type="transferComment">...</termNote>`. The text inside the tags is the clarification. This `<termNote>` element is a child of the `<termGrp>` element.

### Acceptability labels

In Terminologue, a term inside an entry can be accompanied by an acceptability label, which is typically a label like *deprecated*, *obsolete* or *preferred*. This is exported as `<termNote type="normativeAuthorization">...</termNote>`. The text inside the tags is the acceptability label in the language of the `<langSet>`. This `<termNote>` element is a child of the `<termGrp>` element.

## Definitions

Definitions are exported as `<descrip type="definition">...</descrip>`. The text between the tags is, of course, the text of the definition. This `<descrip>` element is a child of `<langSet>` such that, for each language, all definitions in that language are children of the `<langSet>` for that language.

In Terminologue, it is possible for an entry to have more than one definition. Therefore, in the TBX exported from Terminologue, it is possible for a `<langSet>` to have more than one `<descrip type="definition">`.

In Terminologue, inside a single entry, it is possible for definitions in different languages to grouped up if they are translations of each other (or one another). This grouping is **lost** in the export to TBX.

In Terminologue it is possible for definitions to have domain labels. These are **not** exported to TBX.

## Intros

In addition to definitions, entries in Terminologue can have something called *intros*. These are short informal mini-definitions of the concept. An entry can have up to one of these in each language.

Intros are exported as `<descrip type="explanation">...</descrip>`. The text between the tags is the text of the intro. This `<descript>` element is a child `<langSet>` such that the text of the intro is in the language of the `<langSet>`.

## Examples

Examples (example sentences) are exported as `<descrip type="example">...</descrip>`. The text between the tags is, of course, the text of the example. This `<descrip>` element is a child of `<langSet>` such that, for each language, all examples in that language are children of the `<langSet>` for that language.

In Terminologue, inside a single entry, it is possible for examples in different languages to grouped up if they are translations of each other (or one another). This grouping is **lost** in the export to TBX.

In Terminologue, it is possible for examples in the same language to be grouped up if they are variants of one another. This grouping is **lost** in the export to TBX.

## Domain labels

Domain labels are exported as `<descrip type="subjectField">...</descrip>`. The text between the tags is the domain label in the **termbase language**. This `<descrip>` element is a child of `<termEntry>` (and so it is **not** inside any `<langSet>`).

Domain labels in Terminologue can be hierarchical: a domain label can be a child of another domain label, which in turn can be the child of another domain label, and so on. When exporting domain labels to TBX, the entire hierarchy is given inside the `<desctipt>` element, with levels separated by the `»` character, for example `<descrip type="subjectField">Public safety » Policing » Police violence</descrip>`.

## Everything else

Any Terminologue data elements not mentioned above are **not** exported to TBX. This affects various administrative data (e.g. checking status, publishing status), any source labels attached to terms, definitions etc., notes attached to entries, comments attached to entries, membership of entries in collections, and the labelling of things as non-essential.
