---
title: "Logfire - Pydantic Logfire Documentation"
source: "https://logfire.pydantic.dev/docs/"
author:
published:
created: 2025-12-29
description: "Pydantic Logfire Documentation"
tags:
  - "clippings"
---
[Skip to content](https://logfire.pydantic.dev/docs/#getting-started)

## Getting Started

## About Pydantic Logfire

From the team behind **Pydantic Validation**, **Pydantic Logfire** is a new type of observability platform built on the same belief as our open source library — that the most powerful tools can be easy to use.

**Logfire** is built on OpenTelemetry, and supports monitoring your application from **any language**, with particularly great support for Python! [Read more](https://logfire.pydantic.dev/docs/why/).

## Overview

This page is a quick walk-through for setting up a Python app:

1. [Set up Logfire](https://logfire.pydantic.dev/docs/#logfire)
2. [Install the SDK](https://logfire.pydantic.dev/docs/#sdk)
3. [Instrument your project](https://logfire.pydantic.dev/docs/#instrument)

## Set up Logfire

1. [Log into Logfire](https://logfire.pydantic.dev/login)
2. Follow the prompts to create your account
3. Once logged in, you'll see the **Welcome to Logfire** prompt. Click **Let's go!** to go to the **starter-project** Setup page.

[![Welcome to Logfire](https://logfire.pydantic.dev/docs/images/logfire-screenshot-welcome-to-logfire.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-welcome-to-logfire.png)

1. You will find how to send data to your **starter-project** there. Also, there are some code snippets to help you get started.

A **Logfire** project is a namespace for organizing your data. All data sent to **Logfire** must be associated with a project.

Ready to create your own projects in UI or CLI?
- In the UI, create projects by navigating to the Organization > Projects page, and click **New project**.
- For CLI check the [SDK CLI documentation](https://logfire.pydantic.dev/docs/reference/cli/#create-projects-new).

## Install the SDK

1. In the terminal, install the **Logfire** SDK (Software Developer Kit):

```bash
pip install logfire
```

```bash
uv add logfire
```

```bash
conda install -c conda-forge logfire
```

1. Once installed, try it out!
```bash
logfire -h
```
1. Next, authenticate your local environment:
```bash
logfire auth
```

Upon successful authentication, credentials are stored in `~/.logfire/default.toml`.

## Instrument your project

Development setup

During development, we recommend using the CLI to configure Logfire. You can also use a [write token](https://logfire.pydantic.dev/docs/how-to-guides/create-write-tokens/).

1. Set your project
```bash
in the terminal:logfire projects use <first-project>
```

Run this command from the root directory of your app, e.g. `~/projects/first-project`

1. Write some basic logs in your Python app
```bash
hello_world.pyimport logfire

logfire.configure()  The configure() method should be called once before logging to initialize Logfire.
logfire.info('Hello, {name}!', name='world')  This will log Hello world! with info level.
```

Other [log levels](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire) are also available to use, including `trace`, `debug`, `notice`, `warn`,`error`, and `fatal`.

1. See your logs in the **Live** view

[![Hello world screenshot](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)

Production setup

In production, we recommend you provide your write token to the Logfire SDK via environment variables.

1. Generate a new write token in the **Logfire** platform
	- Go to Project Settings Write Tokens
	- Follow the prompts to create a new token
2. Configure your **Logfire** environment
```bash
In the terminal:export LOGFIRE_TOKEN=<your-write-token>
```

Running this command stores a Write Token used by the SDK to send data to a file in the current directory, at `.logfire/logfire_credentials.json`

1. Write some basic logs in your Python app
```bash
hello_world.pyimport logfire

logfire.configure()  
logfire.info('Hello, {name}!', name='world')
```
1. The `configure()` method should be called once before logging to initialize **Logfire**.
2. This will log `Hello world!` with `info` level.

Other [log levels](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire) are also available to use, including `trace`, `debug`, `notice`, `warn`,`error`, and `fatal`.

1. See your logs in the **Live** view

[![Hello world screenshot](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)

---

Ready to keep going?

- Read about [Concepts](https://logfire.pydantic.dev/docs/concepts/)
- Complete the [Onboarding Checklist](https://logfire.pydantic.dev/docs/guides/onboarding-checklist/)

More topics to explore...

- Logfire's real power comes from [integrations with many popular libraries](https://logfire.pydantic.dev/docs/integrations/)
- As well as spans, you can [use Logfire to record metrics](https://logfire.pydantic.dev/docs/guides/onboarding-checklist/add-metrics/)
- Logfire doesn't just work with Python, [read more about Language support](https://opentelemetry.io/docs/languages/)
- Compliance requirements (e.g. SOC2)? [See Logfire's certifications](https://logfire.pydantic.dev/docs/compliance/)