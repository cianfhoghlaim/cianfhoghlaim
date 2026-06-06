---
title: Deployment
description: Deploying Documental to a server environment
keywords: documentation, localization, internationalization, Sapper, Svelte, Gaois, Fiontar & Scoil na Gaeilge, DCU
resource: Documental
order: 4
public: true
---

Documental can be deployed either as (i) a Node.js application or (ii) a static website.

## Deploy as a Node.js application

### Create a production build

The first step is to create a production build of your application. Run the following command. Note that if you are currently running the application in development mode you will need to stop it (`Ctrl`/`Cmd` + `C`) before following this step.

```cmd
npm run build
```

This produces an optimised version of your application that is ready for production deployment. The application code is output to the `__sapper__/build` directory. Run `node __sapper__/build` from the project root to test the production build on your machine.

### Deploy to server

You will then need to place the application on a server, either by FTP, RDP, automated script or whatever your preferred method is.

The following directories need to be deployed to the website root on your server environment:

```
- __sapper__/build
- docs
- node_modules
- static
```

We created the build output folder in the previous step. The `docs` directory contains your Markdown documentation files. The `node_modules` folder is the same as that in your project root, NOT the folder at `src/node_modules`. The `static` directory contains your static assets.

As regards subsequent deployments:

- If only the documentation has been updated (i.e. no application code has changed) you only need to deploy the `docs` folder.
- If you install or update any Node.js modules, you will need to redeploy the `node_modules` directory.
- Because Sapper uses a robust internal versioning system for application code, it is safe to merge subsequent deployments into the `__sapper__/build` folder as opposed to overwriting the folder. This also prevents users who are currently connected to the website from experiencing errors.

### Deploying to IIS with iisnode

On Windows Server environments it is possible to serve Node.js applications using IIS as a reverse proxy. This is facilitated by [iisnode](https://github.com/Azure/iisnode) which you need to install first. A few extra steps need to be followed in this case:

1. Create a new file in the website root directory called **app.js**. The file will contain just a single line that calls Documental's server-side code:

  ```js
  require('./__sapper__/build/index.js');
  ```

2. Create a new **Web.config** file in the website root directory. The Documental repository contains a sample Web.config file with annotations. The most important sections of the config file are as follows:

  ```xml
  <configuration>
    <system.webServer>
      <handlers>
        <add name="iisnode" path="app.js" verb="*" modules="iisnode" />
      </handlers>
      <rewrite>
        <rules>
          <rule name="App">
            <match url="/*" />
            <action type="Rewrite" url="app.js" />
          </rule>
        </rules>
      </rewrite>
    </system.webServer>
  </configuration>
  ```

  These serve to (i) load the iisnode hander and (ii) and redirect all requests to the app.js file where they are handed off to the Documental application code.

## Deploy using static site generation

A static site is a collection of pregenerated HTML, JavaScript and CSS files. This is opposed to a server-generated website where content may be rendered and served to the user on the fly by an application. Static sites can be comparatively low-maintenance and require little-to-no server-side configuration.

Run the following command to output a static site from Documental:

```cmd
npm run export
```

The static files will be output to the `__sapper__/export` directory. Subsequent export commands will automatically overwrite the contents of this directory.

Run `npx serve __sapper__/export` to test your static site.

When ready, deploy the contents of the `__sapper__/export` directory to the website root in your server environment.

See the [Sapper](https://sapper.svelte.dev/) docs for further information.
