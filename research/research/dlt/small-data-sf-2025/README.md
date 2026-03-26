# Keep It Simple and Scalable

> This repository hosts the material for a workshop given at [Small Data SF 2025]([https://www.smalldatasf.com/](https://www.smalldatasf.com/#agenda-hands-on-workshops-keep-it-simple-and-scalable-pythonic-extract-load-transform-elt-using-dlthub)).

During this workshop, you will use the Python library [dlt](https://github.com/dlt-hub/dlt) to build an extract, load, transform (ELT) pipeline for the [official GitHub REST API](https://docs.github.com/en/rest?apiVersion=2022-11-28).

We'll go through the full lifecyle of a data project:
1. Load data from a REST API
2. Ensure data quality via manual exploration and checks
3. Transform raw data into clean data and metrics 
4. Build a data product (e.g., report, web app)
5. Deploy the pipeline and data product

We'll introduce and suggest several tools throughout the workshop: dlt, [LLM scaffolding](https://dlthub.com/workspace), [Continue](https://github.com/continuedev/continue), [duckdb](https://github.com/duckdb/duckdb), [Motherduck](https://motherduck.com/), [marimo](https://github.com/marimo-team/marimo/tree/main), [ibis](https://github.com/ibis-project/ibis), and more!

## Workshop format

This workshop will alternate between:
- **Tutorial**: speakers explain and demonstrate concepts
- **Exercise**: participants code to solve a task

Most exercises are open-ended and participants are invited to explore their own path (e.g., ingest data from different endpoints). It's also possible to follow along the speaker during exercise segments.

To avoid getting stuck, this repository includes several checkpoints to resume from.

## Repository structure

All of the workshop material is in this repository. A brief overview:

- `README.md` contains all of the written instructions for the workshop. See the `## Setup` section for installation instructions 
- `pyproject.toml` and `uv.lock` define Python dependencies
- `.continue/` contains MCP configuration for the Continue IDE extension
- `.cursor/` contains MCP configuration for the Cursor IDE
- `.vscode/` contains MCP configuration for the GitHub Copilot extension


## Setup
1. Start by cloning this repository on your local machine

  ```shell
  git clone https://github.com/dlt-hub/small-data-sf-2025
  ```

2. Move to the repository directory

  ```shell
  cd small-data-sf-2025
  ```

### Python environment
1. Create a virtual Python environment and active it

    ```shell
    # on Linux & MacOS
    python -m venv .venv && .venv/bin/activate
    ```

    ```shell
    # on Windows
    python -m venv .venv && .venv/Scripts/activate
    ```

2. Install Python dependencies

    ```shell
    pip install -r requirements.txt
    ```

### dltHub
During the workshop, we will use the Python library [dlt](https://github.com/dlt-hub/dlt). It is open source and under the Apache 2.0 license. We will also use the Python library dlthub, which includes paid features. A 30-day trial license can be self-issued anonymously for development, education, and CI operations purposes.

0. Setup the Python environment, which includes `dlt` and `dlthub`
1. Self-issue a license for `dlthub` and the specified features: 
  ```shell
  dlt license issue dlthub.transformation
  ```
2. It should automatically store the token. If it prints a warning, follow the instructions.
3. Verify the token is properly set: `dlt license info`. The result should look like
   ```shell
   Searching dlt license in environment or secrets toml
   License found

   License Id: 736xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx
   Licensee: machine:4366xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Issuer: dltHub Inc.
   License Type: self-issued-trial
   Issued: 2025-11-xx xx:xx:xx
   Scopes: dlthub.transformation
   Valid Until: 2025-12-xx xx:xx:xx
   ```

### GitHub REST API
The workshop will focus on using public data from the official [GitHub REST API](https://docs.github.com/en/rest?apiVersion=2022-11-28). The REST API is free to use, but you need a GitHub token to make requests to most endpoints.

1. Login on GitHub
2. Go to [https://github.com/settings/apps](https://github.com/settings/apps)
3. Select `Personal access tokens > Tokens (classic)`
4. Click `Generate new token > Generate new token (classic)`
5. Set a `note`. You don't need to select any `scope`.
6. Click `Generate token`
7. Store the token value securely. We will add it to `.dlt/secrets.toml` during the workshop.

References:
- [Authenticating with a personal token](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28#authenticating-with-a-personal-access-token)

### Motherduck
The vast majority of the workshop will be happening on your local machine. We'll be using [Motherduck](https://motherduck.com/) during the later steps to show how to go from local development to production. You can signup via email, Google, or GitHub. The free tier is sufficient for the workshop (you might receive a free business trial on first signup).

1. Login / signup to Motherduck [https://app.motherduck.com/](https://app.motherduck.com/)
2. (on signup) Go through onboarding flow. Look out for the `Skip` button.
3. Go to [https://app.motherduck.com/settings/tokens](https://app.motherduck.com/settings/tokens)
4. Click `Create token` to generate a `Read/Write Token`
5. Store the token value securely. We will add it to `.dlt/secrets.toml` during the workshop.

### Continue
During the workshop, we will use the [VSCode](https://code.visualstudio.com/) extension [Continue](https://github.com/continuedev/continue) to build data pipelines using `dlt`, LLMs, and MCP servers. It is open source and under the Apache 2.0 license. You will need an LLM API key to use it (OpenAI, Anthropic, Mistral, etc.). Using self-hosted LLMs is also possible.

> Note. If you already have a subscription with Cursor, Copilot, Windsurf, etc., you will be able to follow along with these tools. The interface and configuration will differ slightly though.

1. Install VSCode [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Inside VSCode, go to the `Extensions` tab
3. Search for `continue` and install the extension (by `continue.dev`, identifier is `continue.continue`)
4. Go to the Continue chat panel. You can find it by doing `CTRL + P` (command palette) and execute `Continue: Focus Continue Chat`
5. Under `Models`, set your LLM API key. We suggest select models X or Y `TODO complete steps`
6. Under `Tools`, you should see the MCP server loaded with some tools if you properly setup your Python environment.
