---
title: Creating and editing documentation
shortTitle: For editors
description: How to create and edit documentation
keywords: documentation, localization, internationalization, Sapper, Svelte, Gaois, Fiontar & Scoil na Gaeilge, DCU
resource: Documental
order: 2
public: true
---

This page contains instructions for content editors writing or translating documents for use in Documental. While the experience of writing technical documentation is somewhat different to using a typical word processor it is not something that requires any in-depth technical knowledge

## Requirements

Documental requires documentation to be written in Markdown. Markdown is just plain text with a few additional symbols that we insert to represent things like headings, bold text, links, etc. Documental uses a particular variation of Markdown known as "GitHub-flavoured Markdown" (GFM) which makes it easier to mix computer code with regular prose. However, it's important to stress that you don't need to understand any programming languages to write Markdown! You can find a quick reference for writing in GFM [here](https://guides.github.com/features/mastering-markdown/) or a more detailed guide [here](https://www.markdownguide.org/). Markdown files are text files with a particular file extension, usually **.md**. You may choose to edit Markdown files via an online platform such as GitHub or using an application on your computer.

## Folder structure

All documentation is contained in the `docs` folder. As an editor, you will be able to complete all of your work here. A typical `docs` folder structure looks something like this:

```
- docs
  - data
    - logainm
      - v0.9
        - api.en.md
        - api.ga.md
  - software
    - terminologue
      - configuration.en.md
      - installation.en.md
      - intro.en.md
```

There is a parent `docs` folder. Within that folder there are two **categories** of documentation, `data` (Open Data) and `software` (Software). Each of these folders contains one or more **resources**. A resource is a collection of one or more **documents** relating to a particular service or piece of software. If we look in the `software` folder we see a resource called `terminologue` (Terminologue) which in turn contains several documents.

If we turn to the `data` folder and the `logainm` (Logainm API) resource, we see its direct child is a **version** folder, `v0.9`. The documents in this folder relate to version 0.9 of the API. Certain resources may have multiple versions and documentation specific to those versions.

Compare the folder structure to the URLs used on the [docs.gaois.ie](https://docs.gaois.ie) website. See how a URL such as `https://docs.gaois.ie/en/software/terminologue/installation` or `https://docs.gaois.ie/ga/data/logainm/v0.9/api` maps to the folder structure.

## File naming

As you might have gathered from the previous section, Markdown files in Documental are named according to a specific format and this affects how the documents are accessed and displayed on the website. This format is:

```
[slug].[locale].md
```

- **.md** is the file extension ('md' for **M**ark**d**own).
- The **locale** uses an ISO language code to represent the language in which the document is written, e.g. `en` for English and `ga` for *Gaeilge* (Irish).
- The **slug** is a unique name for your file.

A **slug** can be the same as a document title but it must follow a number of rules:

1. Use only lowercase letters.
2. Replace spaces with hyphens (`-`).
3. Do not use any accents (á, é, ó, etc.) or special characters such as `!`, `?` or `#`.

Here are some valid filenames in Documental:

- `api.ga.md`
- `deployment.en.md`
- `getting-started.ga.md`

Here are some INVALID documentation filenames:

- `Api.en.md` (uses uppercase letter)
- `deployment.md` (missing locale)
- `getting started!.en.md` (space not replaced with hyphen; uses special character)

## Writing documentation

Now that you have a file prepared, it's time to write some documentation. Each document should contain two parts: (1) metadata and (2) content.

### Writing metadata

As you probably know, metadata is data which describes other data. The metadata in Documental documents describes the content of the document (discussed in the next section). We write metadata at the very top of the document, before anything else, in what we call a "metadata header". Here's an example:

```yaml
---
title: Logainm Application Programming Interface (Version 0.9)
shortTitle: API
description: Developer documentation for the Logainm API
keywords: Logainm, API, placenames, toponymy, onomastics, Irish language
resource: Logainm
order: 1
public: true
---
```

This follows a format called YAML but it's not important to understand this. Let's break it down into a couple of parts:

1. The header starts and ends with sets of triple hyphens `---`. This is how we (and the computer) know that it's not part of the content.
2. Each line within the header contains one piece of metadata.
3. Each line consists of a **key** such as `title` or `order` followed by a **value**. Keys and values are separated by a colon (`:`) and a space.

The last point is important to note as if you have two colons in a single line it may cause an error (the computer thinks you're trying to put two key-value pairs on one line). So what happens if you need to use a second colon? In cases such as this, you can enclose the value in quotes as below. It doesn't matter if you use single- or double-quotation marks:

```yaml
title: "Gaois: Bigger, longer documentation"
```

The full set of possible metadata fields are described below:

```yaml
title:
shortTitle:
description:
keywords:
resource:
github:
npm:
nuget:
order:
toc:
public:
```

| Key | Required | Value |
| --- | -------- | ----- |
| `title` | Yes | The full title of the document. This will be displayed at the top of the document page. |
| `shortTitle` | Yes | A brief title (as few words as possible) that will be displayed in the website navigation. |
| `description` | Yes | A short 1-2 sentence summary of the content. May be displayed in search engine results or social media shares. |
| `keywords` | Yes | A comma-separated list of keywords relating to the document content. |
| `resource` | No | The name of the resource with which the document is associated. Will be displayed before the document title in the browser tab.  |
| `github` | No | The URL of a [GitHub](https://github.com/) repository associated with the document. |
| `npm` | No | The URL of an [NPM](https://www.npmjs.com/) package associated with the document. |
| `nuget` | No | The URL of a [NuGet](https://www.nuget.org/) package associated with the document. |
| `order` | No | A number representing the ascending order in which documents associated with a single resource will be displayed in the navigation. |
| `toc` | No | If this key is given a value of `false`, no table of contents will be displayed with the document. If not set, the value is presumed to be `true`. |
| `public` | Yes | Must be present and must be given a value of `true` in order for the document to be accessible via the public website. |

Note that not all fields are required. However, if you want your document to be available to the public you must add a key-value pair of `public: true`.

### Writing content

The remainder of the document is content written in Markdown. For questions regarding Markdown please consult the resources mentioned above. However, it's worth highlighting a few points:

- Use headings. Headings give structure to content and make it easier to read, particularly in a digital context where there are no pages to subdivide the text.
- Provided that the `toc` metadatum has not been set to `false` (see above), Documental will use the headings in a given document to automatically generate a table of contents. This table of contents is displayed on the right-hand side of the page on desktop screens and is accessible by pressing a button on mobile devices.
- Computer code, as well as values consumed by or output from computer programs, is usually represented in Markdown by enclosing it in backticks (<code>`</code>). Typically, you do not translate text in code blocks as, while the text might use English-language words or phrases, it is usually specific to the  vocabulary and syntax of the programming language in question.

Finally, probably the best way to learn is by looking at pre-existing examples. Take a look at the files in the `docs` folder and see how they are displayed on the [docs.gaois.ie](https://docs.gaois.ie) website.

### Using images

Images can be included in any document using normal Markdown syntax:

```md
![GeoNames2Sql Command-line Interface](/images/geonames2sql.jpg)
```

There are just two things to bear in mind as regards images:

1. Image files should be placed in the `static/images` directory in your Documental project.
2. As is clear from the example above, you must refer to image files using the `/images/` path, e.g. `/images/myimagefilename.jpg`.
