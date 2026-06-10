---
title: Developer documentation
shortTitle: For developers
description: How to extend and modify Documental
keywords: documentation, localization, internationalization, Sapper, Svelte, Gaois, Fiontar & Scoil na Gaeilge, DCU
resource: Documental
order: 3
public: true
---

Documental is a [Node.js](https://nodejs.org/) application written in JavaScript. It can run on a server, dynamically serving content, or it can be used as a [static site generator](https://www.staticgen.com/about). This is explained further in the [deployment](../deployment) section. All website content is stored on disk in the form of Markdown files and there are no databases or other types of data store.

The software works on all popular operating systems: the only prerequisite is to install Node.js on your computer. All other dependencies will be detected and installed automatically by the Node.js Package Manager (NPM) during setup. Documental is built using [Svelte](https://svelte.dev/), a component framework similar to [React](https://reactjs.org/), and [Sapper](https://sapper.svelte.dev/), an application framework powered by Svelte. Please consult the documentation for these frameworks as regards any application-level questions you might have, as such information is outside the scope of this article.

## Getting started

### Installation and setup

Clone the Documental repository to your machine:

```cmd
git clone https://github.com/gaois/documental
```

Change directory to your local repository and install the project dependencies:

```cmd
npm install
```

### Start the application

Run the following command to start Documental in development mode:

```cmd
npm run dev
```

Running the application in development mode gives you hot module reloading (changes you make in the editor are reflected in the browser immediately on save), detailed info and error messages in the console. Prior to deploying the application to a server environment, you will need to build the application in production mode. This is discussed in the [deployment](../deployment) section.

## Project structure

Let's take a look at the folder structure within your Documental repository. You are most likely to make changes in the following top-level folders:

- **`docs`**: This contains the Markdown documentation that will be published on your website.
- **`messages`**: This contains the translated strings that will be displayed in the User Interface (UI). See [Localisation](#localisation) below.
- **`src`**: The application source code, including routing and business logic.
- **`static`**: Static files to be served by your application, such as images, favicons or external CSS files.

## Component-based approach

Modern JavaScript frameworks take a component-based approach to constructing an application. If you are used to producing HTML with server-side frameworks in C#, PHP, etc. this may not be immediately intuitive. As regards Documental, components are single files with a **.svelte** extension. They are typically placed in the `src/node_modules/components` folder.* Component files encapsulate the markup, style, state and logic for a particular part of an application. They may also import other components and use them within their markup. **Resource.svelte**, for example, imports a child component called **Article.svelte** and uses the component tag `<Article/>` within its markup. While the `<Article/>` tag looks somewhat like (X)HTML it will not be rendered in the browser as such. Rather, the article component, and all of its child components, will be compiled to standard, valid HTML before being sent to the client. The component-based approach is easy to learn once you start editing .svelte files. More information is available in the Sapper and Svelte documentation referenced above.

\* Note that the .svelte files in the `src/routes` folder are also components, but it is conceptually easier to think of them as corresponding to web pages.

## Concepts

Documental is organised around a few key concepts:

1. **Locales**: This represents the user's localisation/internationalisation preferences, e.g. *Gaeilge* (Irish) or English.
2. **Documentation categories**: In Documental, there are two categories — open data and software — however more can be added.
3. **Resources**: Resources are discrete collections of one or more documents associated with a piece of software, a service or a data artifact.
4. **Resource versions**: Documentation for particular resources may be versioned, usually with reference to the resource's own version number.
5. **Documents**: A single page of documentation, particular to a specific category, locale, resource and, optionally, resource version.

These concepts are reflected in the URLs used by the docs.gaois.ie website:

> `https://docs.gaois.ie/en/data/logainm/v0.9/licence`

- **`en`**: The locale is English.
- **`data`**: The category is Open Data.
- **`logainm`**: The resource is the Logainm API.
- **`v0.9`**: The documentation version number is 0.9.
- **`licence`**: The slug `licence` corresponds to the name of a single document (i.e. a single file in the `docs` directory).

As stated above, not all resources are versioned:

> `https://docs.gaois.ie/ga/software/geonames2sql`

- **`ga`**: The locale is Irish.
- **`software`**: The category is Software.
- **`geonames2sql`**: The resource is GeoNames2Sql.

If there is only one document associated with the resource, a document slug is not required, as is the case in the previous example.

These concepts are also reflected in the naming of svelte files in the `src/routes` directory. Please consult the Sapper documentation for information as regards how routing is handled.

```
- routes
  - [locale]
    - [category]
      - index
      - [version]
        - [slug]
      - [slug]
  - index
```

Furthermore, as you can see in the documentation for [editors](../editors), the Markdown documentation files are largely organised around these concepts.

## Localisation

Documental handles UI localisation via the [svelte-i18n](https://github.com/kaisermann/svelte-i18n) library. This uses the [ICU Message format](http://userguide.icu-project.org/formatparse/messages) to translate user-visible strings.

Translations are stored in JSON files in the top-level `messages` folder. These files are named in the format `[locale].json`. By default, the structure of the `messages` folder is as follows:

```
- messages
  - en.json
  - ga.json
```

Translations can be nested within these JSON files according to any structure you deem fit, e.g.

```json
{
  "navigation": {
    "api": "API",
    "changelog": "Changelog",
    "dataDictionary": "Data dictionary",
    "gettingStarted": "Getting started",
    "licence": "Licence",
    "openData": "Open Data",
    "software": "Software",
    "surnames": "Surnames Index"
  },
  ...
}
```

There is no restriction on the extent to which objects can be nested within the translation file. We call a localised string in the UI using dot notation such as `$_('navigation.openData')` where `navigation.openData` returns `Open Data` for an English-language locale or `Sonraí Oscailte` for an Irish-language locale, etc. 

Of course, for larger blocks of text we can put localised content in separate (Markdown) files, as is the case with the main documentation content of the website which is stored in the top-level `docs` folder.

## Adding a new resource

While editorial team members can [create and edit documents](../editors) within a particular resource, developer input is usually required to add a new resource, or to change how a resource is displayed in the navigation or on the homepage. The instructions below describe how to accomplish this.

### `docs` folder

Each documentation resource requires a corresponding folder within the top-level `docs` directory. If you were creating an open data resource for a new API, for example, you might create a new folder at `docs/data/mynewapi`. If the API was versioned you might add a further subfolder at `docs/data/mynewapi/v1.0`. See the repository for existing examples. Note that this task could be carried out by a content editor provided they have a good understanding of the directory structure. 

### Navigation

The **Navigation.svelte** [component](#component-based-approach) is located in `src/node_modules/components`. Editing this file allows us to modify the list of resources which are accessible on the site (displayed on the left-hand side of the screen on desktop devices).

For example, to add a new software resource we edit the appropriate section of the **Navigation.svelte** file:

```svelte
<h2>{$_('navigation.software')}</h2>
<ul>
  <li>
    <NavigationResource category='software' resource='terminologue' heading='Terminologue' index='intro'/>
  </li>
  <li>
    <NavigationResource category='software' resource='geonames2sql' heading='GeoNames2Sql' singleton/>
  </li>
  ...
</ul>
```

Add a new list item `<li>` and child `<NavigationResource/>` component:

```svelte
<li>
  <NavigationResource
    category='software'
    resource='terminologue'
    heading='Terminologue'
    index='intro'/>
</li>
```

The `<NavigationResource/>` component accepts a number of **props** (properties):

| Prop | Description |
| ---- | ---- |
| **category** | The documentation category `data` or `software`. |
| **resource** | The resource slug. Corresponds to the name of the resource folder under `docs`. |
| **heading**  | The resource title. If the resource has several documents, this will be displayed above them in the navigation. |
| **latestVersion** | If the resource is versioned, specify the latest version number here.  |
| **index**    | The index is the 'homepage' of the resource. Pass the document slug of the first document to be displayed as the index value. Not required if the resource is a singleton. |
| **singleton** | If specified, the resource contains only one document and you do not need to specify an `index` prop. |

Don't forget that unless a document has a YAML header of `public: true` it will not be visible in the navigation.

### Homepage

Optionally, you may wish to add a descriptive blurb about the resource to the website home page. Open the **Home.svelte** component in `src/node_modules/components`.

As with the navigation, we need to add a component that will represent the new resource:

```svelte
<ul>
  <li>
    <HomeResource 
      href={`/${$locale}/software/terminologue/intro`}
      heading='Terminologue'
      blurb={$_('home.sections.terminologueBlurb')}/>
  </li>
  ...
</ul>
```

| Prop | Description |
| ---- | ---- |
| **href** | The relative path or absolute URL of the resource. |
| **heading** | A descriptive heading. |
| **blurb** | A 1-2 sentence description of the resource. |

Note that you may want to pass [localized strings](#localisation) for some of the props.
