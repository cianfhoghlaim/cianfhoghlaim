---
title: Evidence Dashboard Code
emoji: 📈
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---
(HuggingFace Spaces config syntax)

# Evidence PyPI Popularity Project

* Markdown + SQL page(s) found in pages/

* config + SQL files found in sources/

* sources/connection.yaml needs to access the output results of the DBT Project, expecting a local pypi_analytics.duckdb file or a MotherDuck connection

## Using the CLI

```bash
npm install
npm run sources
npm run dev -- --host 0.0.0.0
```

See [the CLI docs](https://docs.evidence.dev/cli/) for more command information.


## Using VS Code

If you are using this template in Codespaces (auto-installs the Evidence VS Code extension), click the `Start Evidence` button in the bottom status bar. This will install dependencies and open a preview of your project in your browser - you should get a popup prompting you to open in browser.

**Note:** Codespaces is much faster on the Desktop app. After the Codespace has booted, select the hamburger menu → Open in VS Code Desktop.


## Learning More

- [Docs](https://docs.evidence.dev/)
- [Github](https://github.com/evidence-dev/evidence)
- [Slack Community](https://slack.evidence.dev/)
- [Evidence Home Page](https://www.evidence.dev)
