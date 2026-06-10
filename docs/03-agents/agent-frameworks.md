# agent frameworks

> Auto-merged from subdirectory .md files on 2026-06-06

---


## File: docs/agents/agno/agno/.github/pull_request_template.md

## Description

Describe key changes, mention related issues or motivation for the changes.

**Note:** Your PR title must follow conventional commit format (e.g., `docs: add auth guide`, `fix: correct broken links`, `style: update formatting`). See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Type of Change

- [ ] Bug fix (errors, broken links, outdated info)
- [ ] New content
- [ ] Content improvement
- [ ] Other: \_\_\_\_

## Related Issues/PRs (if applicable)

<!-- Link any related issues or PRs -->

- Closes #\_\_\_\_
- Related SDK PR: agno-agi/agno#\_\_\_\_

## Checklist

- [ ] Content is accurate and up-to-date
- [ ] All links tested and working
- [ ] Code examples verified (if applicable)
- [ ] Spelling and grammar checked
- [ ] Screenshots updated (if applicable)

---


## File: docs/agents/agno/agno/CONTRIBUTING.md

# Contributing to Agno Documentation

Agno is an open-source project and we welcome contributions to our documentation.

## 🚀 Quick Start for Contributors

1. Fork the repository and clone it locally
2. Install Mintlify CLI: `npm i -g mintlify`
3. Run the docs locally: `mint dev` (from the root directory where `docs.json` is)
4. Create a new branch: `git checkout -b [type]/short-description` (e.g., `docs/add-auth-guide`)
5. Make your changes and test with `mint dev`
6. Run `mint build` to check for errors
7. Commit and push your changes
8. Open a pull request with the proper title format (see below)

## 👩‍💻 How to contribute

Please follow the [fork and pull request](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) workflow:

- Fork the repository.
- Create a new branch for your feature.
  - **Branch Naming:** Use the format `[type]/short-description` (e.g., `docs/add-quickstart-guide`, `fix/broken-links`, `style/format-code-examples`)
  - Add your documentation improvements or new content.
  - **Ensure your Pull Request follows our guidelines (see below).**
  - Send a pull request.
  - We appreciate your support & input!

## Pull Request Guidelines

To maintain a clear and organized project history, please adhere to the following guidelines when submitting Pull Requests:

1.  **Title Format:** Your PR title must follow conventional commit format with a type, followed by a colon and a concise subject.
    - Example: `docs: add authentication guide`
    - Common types for documentation:
      - `docs:` - Documentation content changes (new pages, updates, improvements)
      - `fix:` - Fixes to documentation (broken links, typos, incorrect information)
      - `style:` - Formatting changes (no content changes)
    - Other valid types: `feat:`, `test:`, `refactor:`, `build:`, `ci:`, `chore:`, `perf:`, `revert:`.
2.  **Link to Issue:** The PR description should ideally reference the issue it addresses using keywords like `fixes #<issue_number>`, `closes #<issue_number>`, or `resolves #<issue_number>`.
    - Example: `This PR fixes #42 by adding documentation for the new feature.`

## Documentation Structure

The documentation is organized into the following main sections:

- **introduction/** - Getting started guides and overview
- **tutorials/** - Step-by-step tutorials
- **how-to/** - Task-oriented guides
- **concepts/** - Conceptual explanations
- **integrations/** - Guides for external integrations
- **reference/** - Reference documentation
- **reference-api/** - API reference (auto-generated)
- **examples/** - Example code and use cases
- **templates/** - Our code templates and how to use them
- **agent-os/** - AgentOS-specific documentation
- **deploy/** - Introduction to deploying Agno agents/agentOS
- **evals/** - Evaluation documentation
- **faq/** - Frequently asked questions
- **videos/** - Video assets for the docs
- **_snippets/** - Reusable code snippets

## Writing Guidelines

1. **Use clear, concise language** - Write for developers who may be new to the framework.
2. **Include code examples** - Show, don't just tell. Use code snippets to illustrate concepts.
3. **Follow MDX format** - All documentation uses MDX (Markdown with JSX support).
4. **Use consistent formatting** - Follow the existing style in the documentation.
5. **Test your changes** - Always run `mint dev` to preview your changes before submitting.
6. **Link to related content** - Help users navigate by linking to related documentation.

### Code Examples

Use standard markdown code blocks with language tags:

```python
from agno.agent import Agent

agent = Agent(name="MyAgent")
agent.print_response("Hello, world!")
```

For runnable code snippets, you can reference them with filename:

```python hackernews_agent.py
from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools

agent = Agent(tools=[HackerNewsTools()])
```

For multi-platform code examples, use the `<CodeGroup>` component with separate code blocks for each platform:

- Wrap multiple code blocks in `<CodeGroup>` tags
- Each code block should specify the platform (e.g., `bash Mac`, `bash Windows`)
- Include a blank line between code blocks

The `_snippets/` directory contains reusable MDX components (like common setup steps) that can be referenced across multiple documentation pages for consistency.

### Adding New Pages

1. Create a new `.mdx` file in the appropriate directory.
2. Add frontmatter at the top of the file:
   ```mdx
   ---
   title: "Your Page Title"
   description: "Brief description of the page content"
   ---
   ```
3. Update `docs.json` to include the new page in the navigation structure.
4. Test the page appears correctly in local preview.

## Updating API Reference

The API reference in `reference-api/` is auto-generated from the AgentOS OpenAPI schema. For instructions on how to update it, see the [README.md](README.md#how-to-generate-a-new-api-reference).

## Local Testing

Before submitting a pull request, test your changes locally:

1. Run `mint dev` in the root directory.
2. Navigate through your changes in the browser.
3. Run `mint build` to catch any build errors before submitting.
4. Verify all pages load correctly, code examples are properly formatted, links work as expected, and images display correctly.

## Formatting and Validation

Ensure your documentation meets our quality standards:

- Check for broken links and review all internal and external links.
- Validate code examples and make sure all code snippets are syntactically correct.
- Run `mint build` to catch any build errors.
- Preview your changes locally to ensure proper formatting.

Message us on [Discord](https://discord.gg/4MtYHHrgA8) or post on [Discourse](https://community.agno.com/) if you have any questions or need help with your contribution.

## 📚 Resources

- <a href="https://docs.agno.com/introduction" target="_blank" rel="noopener noreferrer">Documentation</a>
- <a href="https://discord.gg/4MtYHHrgA8" target="_blank" rel="noopener noreferrer">Discord</a>
- <a href="https://community.agno.com/" target="_blank" rel="noopener noreferrer">Discourse</a>

---


## File: docs/agents/agno/agno/README.md

# Agno Docs

## Contributing

We welcome contributions to improve the Agno documentation! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- How to set up your development environment
- Pull request and branch naming conventions
- Documentation structure and writing guidelines
- Testing and validation procedures

## Development

Install the [Mintlify CLI](https://www.npmjs.com/package/mintlify) to run documentation site locally:

```
npm i -g mint
```

Run the following command at the root of your documentation (where `docs.json` is)

```
mint dev
```

## Publishing Changes

Publish changes by pushing to the main branch

```
git add .
git commit -m "update message"
git push
```

## How to generate a new API reference

1. In your local `agno` repo, run the `AgentOS` cookbook containing all supported interfaces, using the latest version of Agno.
   ```bash
   python cookbook/agent_os/all_interfaces.py
   ```

2. Download the latest API reference files:
   ```bash
   curl -o reference-api/openapi.json http://localhost:7777/openapi.json
   ```      
   Using swagger-cli: 
   ```bash
   swagger-cli bundle reference-api/openapi.json --outfile reference-api/openapi.yaml --type yaml
   ```
   
3. Delete all files in the `reference-api/schema/` folder (the auto-generated files)
4. Run `npx @mintlify/scraping@latest openapi-file reference-api/openapi.json -o reference-api/schema` to generate the new API reference
5. Update the `docs.json` file to include any new pages.
6. Run `mint dev` to see the changes

## Troubleshooting

- Mintlify dev isn't running - Run `mint update` it'll update dependencies.
- Page loads as a 404 - Make sure you are running in a folder with `docs.json`

---


## File: docs/agents/agno/agno/SKILL_CONTEXT.md

# Agno Docs — Skill Context

**Upstream:** [agno-agi/agno-docs](https://github.com/agno-agi/agno-docs)  
**Purpose:** Mintlify-based documentation site for the Agno agent framework.

## How We Use Agno

Agno is one of our **two primary agent frameworks** (alongside Google ADK). We use it for:
- Multi-agent orchestration with tool calling
- AgentOS stateless execution
- Full async knowledge base queries
- Celtic language agent pipelines

## Preserved Sections

- `introduction.mdx` — framework overview
- `concepts/` — core agent concepts (memory, tools, knowledge, teams)
- `examples/` — agent implementation examples
- `integrations/` — framework integrations (LangChain, LlamaIndex, etc.)
- `reference/` — API reference
- `reference-api/` — programmatic API documentation
- `docs.json` — Mintlify navigation structure

## Related Docs

- `.agents/skills/agno/SKILL.md` — agent skill for Agno development
- `docs/agents/` — our Agno research papers
- `docs/agents/agno/` — research on Agno architecture and patterns

---


## File: docs/agents/agno/github_repo_analyzer/README.md

# GitHub Repository Analyzer

**GitHub Repository Analyzer** is a chat application that provides an interface to analyze GitHub repositories using AI.
It allows users to explore code, review pull requests, analyze project structures, and get insights about repository activity through natural language queries.

> Note: Fork and clone this repository if needed

### 1. Create a virtual environment

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```shell
pip install -r cookbook/examples/streamlit_apps/github_repo_analyzer/requirements.txt
```

### 3. Configure API Keys

Required:

```bash
export OPENAI_API_KEY=your_openai_key_here
```

Optional (for additional models):

```bash
export ANTHROPIC_API_KEY=your_anthropic_key_here
export GOOGLE_API_KEY=your_google_key_here
export GROQ_API_KEY=your_groq_key_here
```

Optional (for enhanced GitHub access):

```bash
export GITHUB_ACCESS_TOKEN=your_github_token_here
```

### 4. Run GitHub Repository Analyzer App

```shell
streamlit run cookbook/examples/streamlit_apps/github_repo_analyzer/app.py
```

## 🔧 Customization

### Model Selection

The application supports multiple model providers:

- OpenAI (o3-mini, gpt-4o)
- Anthropic (claude-3-5-sonnet)
- Google (gemini-2.0-flash-exp)
- Groq (llama-3.3-70b-versatile)

### How to Use

- Open [localhost:8501](http://localhost:8501) in your browser.
- Optionally configure your GitHub Personal Access Token for enhanced access to private repositories.
- Enter repository queries in the chat interface:
  - "Analyze the repository 'owner/repo'"
  - "Show me the latest issues in 'microsoft/vscode'"
  - "Review the latest pull request in 'facebook/react'"
  - "What programming languages are used in 'kubernetes/kubernetes'?"
- The AI will analyze repositories, code, and provide detailed insights.

### Key Features

- **Repository Analysis**: Get comprehensive overviews of any public GitHub repository
- **Code Review**: Analyze pull requests and code changes with detailed feedback
- **Issue Tracking**: Explore and summarize repository issues and discussions
- **Code Search**: Find specific functions, patterns, or implementations across repositories
- **Statistics**: View repository metrics like stars, forks, languages, and activity
- **File Navigation**: Browse repository structure and read file contents
- **Session Management**: Maintain conversation context across sessions

## 📚 Documentation

For more detailed information:

- [Agno Documentation](https://docs.agno.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [GitHub API Documentation](https://docs.github.com/en/rest)

## 🤝 Support

Need help? Join our [Discord community](https://agno.link/discord)

---


## File: docs/agents/agno/KCG_SUMMARY.md

# MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md

This file's content has been merged into `AGNO_COMPREHENSIVE_REFERENCE.md`.

---


## File: docs/agents/agno/python/examples/README.md

# Agno Finance Agent

An Agno Agent with Finance tools for AG-UI that researches stock prices, analyst recommendations, and stock fundamentals.

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Prerequisites

1. Install uv: `pip install uv`
2. Set your OpenAI API key: `export OPENAI_API_KEY="your-api-key"`

### Installation

```bash
# Install dependencies
uv sync

# Activate the virtual environment
uv shell
```

### Running the Agent

```bash
# Run the agent
uv run python agent.py
```

The agent will be available at `http://localhost:9001` (or the port specified by the `PORT` environment variable).

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8 .
```

## Features

- Stock price lookup
- Analyst recommendations
- Stock fundamentals analysis
- AG-UI compatible interface
---


## File: docs/agents/agno/typescript/README.md

# @ag-ui/agno

Implementation of the AG-UI protocol for Agno.

Connects Agno agents to frontend applications via the AG-UI protocol using HTTP communication.

## Installation

```bash
npm install @ag-ui/agno
pnpm add @ag-ui/agno
yarn add @ag-ui/agno
```

## Usage

```ts
import { AgnoAgent } from "@ag-ui/agno";

// Create an AG-UI compatible agent
const agent = new AgnoAgent({
  url: "https://your-agno-server.com/agent",
  headers: { Authorization: "Bearer your-token" },
});

// Run with streaming
const result = await agent.runAgent({
  messages: [{ role: "user", content: "Hello from Agno!" }],
});
```

## Features

- **HTTP connectivity** – Direct connection to Agno agent servers
- **Multi-agent support** – Works with Agno's multi-agent system architecture
- **Streaming responses** – Real-time communication with full AG-UI event support

---


## File: docs/agents/google-adk/deployment/README.md

# Deployment

This directory contains the Terraform configurations for provisioning the necessary Google Cloud infrastructure for your agent.

The recommended way to deploy the infrastructure and set up the CI/CD pipeline is by using the `agent-starter-pack setup-cicd` command from the root of your project.

However, for a more hands-on approach, you can always apply the Terraform configurations manually for a do-it-yourself setup.

For detailed information on the deployment process, infrastructure, and CI/CD pipelines, please refer to the official documentation:

**[Agent Starter Pack Deployment Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment.html)**
---


## File: docs/agents/google-adk/examples/academic-research/README.md

# Academic Research


## Overview

AI-driven agent designed to facilitate the exploration of the academic landscape surrounding seminal research works. Recognizing the challenge researchers face in navigating the expanding body of literature influenced by foundational studies, this agent offers a streamlined approach. By accepting a seminal paper identified provided as file input, the agent first analyzes the core contributions of the specified work.

1. It then leverages specialized Agent tools to identify and retrieve via Google Search recent academic publications that cite this seminal paper, mapping its contemporary influence.
2. Finally, synthesizing the analysis of the original paper with the findings from recent citing literature, and again utilizing specialized analytical tools, the agent proposes potential future research directions.

This capability aims to provide researchers with valuable insights into the ongoing impact of seminal research and to highlight promising avenues for novel investigation, thereby accelerating the research discovery process.

## Agent Details

The key features of the Academic Research include:

| Feature | Description |
| --- | --- |
| **Interaction Type** | Conversational |
| **Complexity**  | Easy |
| **Agent Type**  | Multi Agent |
| **Components**  | Tools: built-in Google Search |
| **Vertical**  | Education |



### Agent architecture:

This diagram shows the detailed architecture of the agents and tools used
to implement this workflow.
<img src="academic-research.svg" alt="academic researcher" width="800"/>

## Setup and Installation

1.  **Prerequisites**

    *   Python 3.10+
    *   uv
        *   For dependency management and packaging. Please follow the
            instructions on the official
            [uv website](https://docs.astral.sh/uv/) for installation.

        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

    * A project on Google Cloud Platform
    * Google Cloud CLI
        *   For installation, please follow the instruction on the official
            [Google Cloud website](https://cloud.google.com/sdk/docs/install).

2.  **Installation**

    ```bash
    # Clone this repository.
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/academic-research
    # Install the package and dependencies.
    uv sync
    ```

3.  **Configuration**

    *   Set up Google Cloud credentials.

        *   You may set the following environment variables in your shell, or in
            a `.env` file instead.

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  # Only required for deployment on Agent Engine
        ```

    *   Authenticate your GCloud account.

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

## Running the Agent

**Using `adk`**

ADK provides convenient ways to bring up agents locally and interact with them.
You may talk to the agent using the CLI:

```bash
adk run academic_research
```

Or on a web interface:

```bash
 adk web
```

The command `adk web` will start a web server on your machine and print the URL.
You may open the URL, select "academic_research" in the top-left drop-down menu, and
a chatbot interface will appear on the right. The conversation is initially
blank. Here are some example requests you may ask the Academic Research to verify:

```
who are you
```

Sampled responses of these requrests are shown below in the [Example
Interaction](#example-interaction) section.

```
Hello! I am an AI Research Assistant.

My purpose is to help you explore the academic landscape related to a seminal paper you're interested in. I can:

Analyze a seminal paper you provide (Title/Authors, DOI, or URL).
Find recent academic papers that cite the seminal work using specialized tools.
Suggest potential future research directions based on the analysis and recent findings, again using specialized tools.
How can I help you today? Would you like to provide a seminal paper for analysis?
```

### Example Interaction

Below is an example interaction with the Academic Research. Note that the exact output
of the agent may be different every time. Not that the user provides a pdf with the seminal paper to analyze

```
 * user: who are you

Hello! I am an AI Research Assistant.

My purpose is to help you explore the academic landscape related to a seminal paper you're interested in. I can:

Analyze a seminal paper you provide (Title/Authors, DOI, or URL).
Find recent academic papers that cite the seminal work using specialized tools.
Suggest potential future research directions based on the analysis and recent findings, again using specialized tools.
How can I help you today? Would you like to provide a seminal paper for analysis?

 * user: 1706.03762v7.pdf
 * user: enclosed

Okay, I have received the paper "Attention Is All You Need". Thank you for providing it.

First, I will analyze the seminal paper to establish the context.

Seminal Paper Analysis

Seminal Paper: Attention Is All You Need, Vaswani et al., 2017 (Published at NIPS 2017)

Authors:

Ashish Vaswani (Google Brain)
Noam Shazeer (Google Brain)
Niki Parmar (Google Research)
Jakob Uszkoreit (Google Research)
Llion Jones (Google Research)
Aidan N. Gomez (University of Toronto / Google Brain)
Łukasz Kaiser (Google Brain)
Illia Polosukhin (Google Research)
Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.

Summary: This paper introduces the Transformer, a novel neural network architecture designed for sequence transduction tasks, particularly machine translation. It marks a significant departure from previous state-of-the-art models which relied heavily on recurrent neural networks (RNNs) or convolutional neural networks (CNNs) within their encoder-decoder structures. The Transformer's core innovation is its complete reliance on attention mechanisms, specifically self-attention (or intra-attention), eliminating the need for sequential processing inherent in RNNs. This allows for significantly greater parallelization during training. The architecture features an encoder and decoder, each composed of stacks of layers containing multi-head self-attention mechanisms and position-wise feed-forward networks. The paper demonstrates that the Transformer achieves superior results on English-to-German and English-to-French translation benchmarks while requiring substantially less training time than previous models. It also shows the model's applicability to other tasks like English constituency parsing.

Key Topics/Keywords:

Transformer model
Attention Mechanism
Self-Attention / Intra-Attention
Multi-Head Attention
Sequence Transduction
Machine Translation
Encoder-Decoder Architecture
Parallelization
Positional Encoding
Natural Language Processing (NLP)
Key Innovations:

Proposed the Transformer architecture based entirely on attention mechanisms, removing recurrence and convolutions for sequence-to-sequence tasks.
Introduced Multi-Head Attention to allow the model to jointly attend to information from different representation subspaces at different positions.
Utilized Scaled Dot-Product Attention as an efficient attention mechanism.
Incorporated positional encodings to provide sequence order information without relying on recurrence.
Achieved state-of-the-art performance on machine translation with significantly improved training efficiency and parallelizability.
References Cited Within Seminal Paper:

Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.
Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. CoRR, abs/1409.0473, 2014.
Denny Britz, Anna Goldie, Minh-Thang Luong, and Quoc V. Le. Massive exploration of neural machine translation architectures. CoRR, abs/1703.03906, 2017.
Jianpeng Cheng, Li Dong, and Mirella Lapata. Long short-term memory-networks for machine reading. arXiv preprint arXiv:1601.06733, 2016.
Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations using rnn encoder-decoder for statistical machine translation. CoRR, abs/1406.1078, 2014.
Francois Chollet. Xception: Deep learning with depthwise separable convolutions. arXiv preprint arXiv:1610.02357, 2016.
Junyoung Chung, Çaglar Gülçehre, Kyunghyun Cho, and Yoshua Bengio. Empirical evaluation of gated recurrent neural networks on sequence modeling. CoRR, abs/1412.3555, 2014.
Chris Dyer, Adhiguna Kuncoro, Miguel Ballesteros, and Noah A. Smith. Recurrent neural network grammars. In Proc. of NAACL, 2016.
Jonas Gehring, Michael Auli, David Grangier, Denis Yarats, and Yann N. Dauphin. Convolutional sequence to sequence learning. arXiv preprint arXiv:1705.03122v2, 2017.
Alex Graves. Generating sequences with recurrent neural networks. arXiv preprint arXiv:1308.0850, 2013.
Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pages 770–778, 2016.
Sepp Hochreiter, Yoshua Bengio, Paolo Frasconi, and Jürgen Schmidhuber. Gradient flow in recurrent nets: the difficulty of learning long-term dependencies, 2001.
Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. Neural computation, 9(8):1735–1780, 1997.
Zhongqiang Huang and Mary Harper. Self-training PCFG grammars with latent annotations across languages. In Proceedings of the 2009 Conference on Empirical Methods in Natural Language Processing, pages 832–841. ACL, August 2009.
Rafal Jozefowicz, Oriol Vinyals, Mike Schuster, Noam Shazeer, and Yonghui Wu. Exploring the limits of language modeling. arXiv preprint arXiv:1602.02410, 2016.
Łukasz Kaiser and Samy Bengio. Can active memory replace attention? In Advances in Neural Information Processing Systems, (NIPS), 2016.
Łukasz Kaiser and Ilya Sutskever. Neural GPUs learn algorithms. In International Conference on Learning Representations (ICLR), 2016.
Nal Kalchbrenner, Lasse Espeholt, Karen Simonyan, Aaron van den Oord, Alex Graves, and Koray Kavukcuoglu. Neural machine translation in linear time. arXiv preprint arXiv:1610.10099v2, 2017.
Yoon Kim, Carl Denton, Luong Hoang, and Alexander M. Rush. Structured attention networks. In International Conference on Learning Representations, 2017.
Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In ICLR, 2015.
Oleksii Kuchaiev and Boris Ginsburg. Factorization tricks for LSTM networks. arXiv preprint arXiv:1703.10722, 2017.
Zhouhan Lin, Minwei Feng, Cicero Nogueira dos Santos, Mo Yu, Bing Xiang, Bowen Zhou, and Yoshua Bengio. A structured self-attentive sentence embedding. arXiv preprint arXiv:1703.03130, 2017.
Minh-Thang Luong, Quoc V. Le, Ilya Sutskever, Oriol Vinyals, and Lukasz Kaiser. Multi-task sequence to sequence learning. arXiv preprint arXiv:1511.06114, 2015.
Minh-Thang Luong, Hieu Pham, and Christopher D Manning. Effective approaches to attention-based neural machine translation. arXiv preprint arXiv:1508.04025, 2015.
Mitchell P Marcus, Mary Ann Marcinkiewicz, and Beatrice Santorini. Building a large annotated corpus of english: The penn treebank. Computational linguistics, 19(2):313–330, 1993.
David McClosky, Eugene Charniak, and Mark Johnson. Effective self-training for parsing. In Proceedings of the Human Language Technology Conference of the NAACL, Main Conference, pages 152–159. ACL, June 2006.
Ankur Parikh, Oscar Täckström, Dipanjan Das, and Jakob Uszkoreit. A decomposable attention model. In Empirical Methods in Natural Language Processing, 2016.
Romain Paulus, Caiming Xiong, and Richard Socher. A deep reinforced model for abstractive summarization. arXiv preprint arXiv:1705.04304, 2017.
Slav Petrov, Leon Barrett, Romain Thibaux, and Dan Klein. Learning accurate, compact, and interpretable tree annotation. In Proceedings of the 21st International Conference on Computational Linguistics and 44th Annual Meeting of the ACL, pages 433–440. ACL, July 2006.
Ofir Press and Lior Wolf. Using the output embedding to improve language models. arXiv preprint arXiv:1608.05859, 2016.
Rico Sennrich, Barry Haddow, and Alexandra Birch. Neural machine translation of rare words with subword units. arXiv preprint arXiv:1508.07909, 2015.
Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey Hinton, and Jeff Dean. Outrageously large neural networks: The sparsely-gated mixture-of-experts layer. arXiv preprint arXiv:1701.06538, 2017.
Nitish Srivastava, Geoffrey E Hinton, Alex Krizhevsky, Ilya Sutskever, and Ruslan Salakhutdinov. Dropout: a simple way to prevent neural networks from overfitting. Journal of Machine Learning Research, 15(1):1929–1958, 2014.
Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, and Rob Fergus. End-to-end memory networks. In C. Cortes, N. D. Lawrence, D. D. Lee, M. Sugiyama, and R. Garnett, editors, Advances in Neural Information Processing Systems 28, pages 2440–2448. Curran Associates, Inc., 2015.
Ilya Sutskever, Oriol Vinyals, and Quoc VV Le. Sequence to sequence learning with neural networks. In Advances in Neural Information Processing Systems, pages 3104–3112, 2014.
Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jonathon Shlens, and Zbigniew Wojna. Rethinking the inception architecture for computer vision. CoRR, abs/1512.00567, 2015.
Vinyals & Kaiser, Koo, Petrov, Sutskever, and Hinton. Grammar as a foreign language. In Advances in Neural Information Processing Systems, 2015.
Yonghui Wu, Mike Schuster, Zhifeng Chen, Quoc V Le, Mohammad Norouzi, Wolfgang Macherey, Maxim Krikun, Yuan Cao, Qin Gao, Klaus Macherey, et al. Google's neural machine translation system: Bridging the gap between human and machine translation. arXiv preprint arXiv:1609.08144, 2016.
Jie Zhou, Ying Cao, Xuguang Wang, Peng Li, and Wei Xu. Deep recurrent models with fast-forward connections for neural machine translation. CoRR, abs/1606.04199, 2016.
Muhua Zhu, Yue Zhang, Wenliang Chen, Min Zhang, and Jingbo Zhu. Fast and accurate shift-reduce constituent parsing. In Proceedings of the 51st Annual Meeting of the ACL (Volume 1: Long Papers), pages 434–443. ACL, August 2013.
Now that I have analyzed the seminal paper, I will search for recent papers citing this work. I will look for papers published since January 2023 (covering roughly the last year and a bit).

* user: ok

Okay, here are the recent papers found citing "Attention Is All You Need" (Vaswani et al., 2017), published since January 2023, based on the tool's search:

Recent Papers Citing "Attention Is All You Need"

(Note: The list includes preprints and some non-peer-reviewed articles/blog posts identified by the search tool.)

2025 Publications/Preprints

Title: Tensor Product Attention Is All You Need
Author(s): Yifan Zhang, Mengxuan Fu, Ximing Xiang, Zhiyuan Zhang, Yuexiang Xie, Dongsheng Li, Dawei Yin
Publication Year: 2025 (v3 submitted April 9, 2025)
Source: arXiv
Link: https://arxiv.org/abs/2501.06425
Title: TransMLA: Multi-head Latent Attention Is All You Need
Author(s): Mengxuan Fu, Yifan Zhang, Zhiyuan Zhang, Xiaogang Chen, Dongsheng Li, Dawei Yin
Publication Year: 2025 (v1 submitted Feb 11, 2025)
Source: arXiv
Link: https://arxiv.org/abs/2502.06816 (Link inferred)
Title: Attention is All You Need Until You Need Retention
Author(s): M. Murat Yaslioglu
Publication Year: 2025 (v1 submitted Jan 15, 2025)
Source: arXiv
Link: https://arxiv.org/abs/2501.09166
Title: Transferable-guided Attention Is All You Need for Video Domain Adaptation
Author(s): André Sacilotti, Samuel Felipe dos Santos, Nicu Sebe, Jurandy Almeida
Publication Year: 2025 (Accepted to WACV'25)
Source: IEEE/CVF WACV'25 / arXiv
Link: https://arxiv.org/abs/2407.01375
Title: Moral Attention Is All You Need
Author(s): Mark Graves
Publication Year: 2025 (Published online Mar 17, 2025)
Source: Theology and Science
Link: https://doi.org/10.1080/14746700.2025.2472118
Title: "Attention", "Transformers", in Neural Network "Large Language Models" (Essay referencing recent work)
Author(s): Cosma Shalizi (referencing Farrell et al., 2025)
Publication Year: 2025 (Essay updated March/April 2025)
Source: Author's Website/Blog
Link: https://www.stat.cmu.edu/~cshalizi/notebooks/attention-is-all-you-need.html
2024 Publications/Preprints/Articles

Title: ATFF: Advanced Transformer with Multiscale Contextual Fusion for Medical Image Segmentation
Author(s): Xinping Guo, Lei Wang, Zizhen Huang, Yukun Zhang, Yaolong Han
Publication Year: 2024 (Published March 29, 2024)
Source: Journal of Computer and Communications, Vol.12 No.3
Link: https://www.scirp.org/reference/referencespapers?referenceid=3338278 (Citation page)
Title: Multimodal Attention is all you need
Author(s): Marco Saioni, Cristina Giannone
Publication Year: 2024 (CEUR Workshop Proceedings, paper dated Dec 4, 2024)
Source: CEUR Workshop Proceedings (Evalita 2023)
Link: https://ceur-ws.org/Vol-3616/paper34.pdf (Link inferred)
Title: Attention is all you need: utilizing attention in AI-enabled drug discovery
Author(s): Yang Zhang, Caiqi Liu, Mujiexin Liu, Tianyuan Liu, Hao Lin, Cheng-Bing Huang, Lin Ning
Publication Year: 2024 (Published Jan 6, 2024)
Source: Briefings in Bioinformatics, Volume 25, Issue 1
Link: https://doi.org/10.1093/bib/bbad467
Title: HIERARCHICAL ENCODING AND CONDITIONAL ATTENTION IN NEURAL MACHINE TRANSLATION
Publication Year: 2024 (Published September 2024)
Source: The American Journal of Engineering and Technology, 6(09)
Link: https://doi.org/10.37547/tajet/Volume06Issue09-07
Title: Measurements With A Quantum Vision Transformer: A Naive Approach
Publication Year: 2024 (Proceedings published 2024)
Source: EPJ Web of Conferences, Volume 295 (ICHEP 2022)
Link: https://www.epj-conferences.org/articles/epjconf/ref/2024/01/epjconf_ichep2022_12003/epjconf_ichep2022_12003.html
Title: Attention is all you need: discovering the Transformer paper (Article/Blog Post)
Author(s): Luis Serrano
Publication Year: 2024
Source: Towards Data Science
Link: https://towardsdatascience.com/attention-is-all-you-need-discovering-the-transformer-paper-731ad0737c6d
Title: Paper Walkthrough: Attention Is All You Need (Article/Blog Post)
Author(s): Muhammad Ardi
Publication Year: 2024 (Published Nov 3, 2024)
Source: Towards Data Science
Link: https://towardsdatascience.com/paper-walkthrough-attention-is-all-you-need-69388903b711
Title: Attention is all you need – Transformers (Article/Blog Post)
Author(s): Strahinja Zivkovic
Publication Year: 2024 (Published Nov 28, 2024)
Source: Master Data Science (Blog)
Link: https://masterdatascience.com/attention-is-all-you-need-transformers/
Title: The Groundbreaking Transformer Paper: “Attention is All You Need” (Article/Blog Post)
Author(s): Brian Carter
Publication Year: 2024 (Published Oct 5, 2024)
Source: The Brian Carter Group (Blog)
Link: https://briancartergroup.com/the-groundbreaking-transformer-paper-attention-is-all-you-need/
Now, based on the seminal paper "Attention Is All You Need" and these recent citing works, I will use a specialized tool to suggest potential future research directions.

* user: ok

Okay, here are the potential future research directions suggested by the tool, based on the seminal "Attention Is All You Need" paper and the recent citing works:

Potential Future Research Directions

Beyond Dot-Product Attention: Exploring Non-Linear and Learnable Similarity Metrics: Instead of just scaled dot-product, research different, perhaps non-linear or fully learned, ways to measure similarity within the attention mechanism. This could capture more complex relationships and lead to more robust or efficient models.
Intrinsically Graph-Aware Attention Mechanisms: Develop attention mechanisms that naturally understand and operate on graph structures (like molecules or social networks) without needing to force them into sequences first.
Physics-Informed and Constraint-Driven Attention: Design attention mechanisms that incorporate known physical laws, rules, or constraints directly into their structure. This could lead to more accurate and efficient models for scientific discovery and simulation.
Hybrid Neuro-Symbolic Attention Architectures: Create attention mechanisms that can interact with symbolic knowledge bases or reasoning engines, combining the strengths of deep learning and traditional AI for better reasoning and fact-checking.
Dynamic Sparsity and Adaptive Computation in Attention: Explore attention mechanisms that dynamically adjust which elements attend to each other based on context (sparse attention) or adapt the amount of computation used per element or layer, making Transformers more efficient for very long sequences or limited resources.
Biologically Plausible Attention and Memory Integration: Investigate attention architectures inspired by how biological brains handle attention and memory, potentially leading to novel models with different capabilities.
Meta-Attention for Interpretability and Controllability: Develop attention mechanisms that can observe their own attention patterns ("meta-attention"). This could improve our understanding of why the model makes certain decisions and potentially allow for more control over its focus.
Attention Mechanisms for Fundamentally Non-Sequential Data Structures: Design attention mechanisms specifically for data that doesn't have a natural order, such as sets of items or point clouds, without imposing artificial sequences.
Temporally Continuous Attention for Streaming Data: Create attention mechanisms suited for continuous, real-time data streams where the idea of a fixed sequence length doesn't apply, crucial for real-time monitoring or control.
Cross-Modal Associative Attention Kernels: Develop new attention "kernels" that can directly compute similarity between elements from different modalities (e.g., image regions and text concepts) without needing to project them into a common space first, enabling tighter multimodal integration.
This analysis provides a starting point for exploring the evolution of Transformer architectures and attention mechanisms.

Would you like to dive deeper into any of these specific research directions, or perhaps explore another seminal paper?

```

## Running Tests

For running tests and evaluation, install the extra dependencies:

```bash
uv sync --dev
```

Then the tests and evaluation can be run from the `academic-research` directory using
the `pytest` module:

```bash
uv run pytest tests
uv run pytest eval
```

`tests` runs the agent on a sample request, and makes sure that every component
is functional. `eval` is a demonstration of how to evaluate the agent, using the
`AgentEvaluator` in ADK. It sends a couple requests to the agent and expects
that the agent's responses match a pre-defined response reasonablly well.


## Deployment

The Academic Co-Research can be deployed to Vertex AI Agent Engine using the following
commands:

```bash
uv sync --group deployment
uv run deployment/deploy.py --create
```

When the deployment finishes, it will print a line like this:

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

If you forgot the AGENT_ENGINE_ID, you can list existing agents using:

```bash
uv run deployment/deploy.py --list
```

The output will be like:

```
All remote agents:

123456789 ("academic_research")
- Create time: 2025-05-10 09:33:46.188760+00:00
- Update time: 2025-05-10 09:34:32.763434+00:00

```

You may interact with the deployed agent using the `test_deployment.py` script
```bash
$ export USER_ID=<any string>
$ uv run deployment/test_deployment.py --resource_id=${AGENT_ENGINE_ID} --user_id=${USER_ID}
Found agent with resource ID: ...
Created session for user ID: ...
Type 'quit' to exit.
Input: Hello. What can you do for me?
Response: Hello! I'm an AI Research Assistant. I can help you analyze a seminal academic paper.

To get started, please provide the seminal paper you wish to analyze as a PDF.
```

To delete the deployed agent, you may run the following command:

```bash
uv run deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

### Alternative: Using Agent Starter Pack

You can also use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready version of this agent with additional deployment options:

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-academic-research -a adk@academic-research
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-academic-research -a adk@academic-research
```
This command handles creating the project without needing to pre-install the package into a virtual environment.

</details>

The starter pack will prompt you to select deployment options and provides additional production-ready features including automated CI/CD deployment scripts.

## Customization

The Academic Research can be customized to better suit your requirements. For example:

 1. Integrate Specialized Search Tools: Augment the agent's discovery capabilities by incorporating additional academic search functionalities, such as an ArXiv-specific search tool, to complement or replace the default search mechanism, allowing for more targeted retrieval from specialized databases and preprint archives.
 2. Implement Output Visualization: Enhance the presentation of research findings by adding modules to visualize the network of cited papers or to graphically represent suggested future research topics, thereby offering a more intuitive and interconnected understanding of the academic landscape.
3. Customize Agent Instructions: Modify the prompts guiding the academic_websearch and academic_newresearch sub-agents. This allows you to direct their analytical focus (e.g., by specifying the depth of citation analysis, emphasizing interdisciplinary connections for future research, or ensuring adherence to particular academic writing conventions) or to refine the structure and detail of their outputs.
4. Download the seminal paper via DOI or URL:  Augment the agent's capabilities by enabling direct download of seminal papers. This feature would allow the agent to:
* Resolve DOI to PDF: Given a Digital Object Identifier (DOI), the agent could leverage APIs or web scraping techniques to locate and download the corresponding PDF of the paper. This streamlines the process of accessing primary sources, especially when the DOI is already known.
* Download from URL: If a direct URL to the paper's PDF or an academic repository page is provided, the agent could be configured to navigate to that URL and initiate the download. This would be particularly useful for papers available on institutional repositories, personal academic websites, or preprint servers that might not have a readily resolvable DOI.
* Integration with Reference Managers: The downloaded papers could then be automatically imported into a specified reference manager (e.g., Zotero, Mendeley, EndNote), along with their metadata, facilitating seamless organization and citation management for the user's research library. This integration would significantly enhance the efficiency of literature review and research compilation.

---


## File: docs/agents/google-adk/examples/deep-search/README.md

# Deep Search Agent Development Kit (ADK) Quickstart

> **Note:** This agent was previously named `gemini-fullstack` and has been renamed to `deep-search`. If you're looking for the old `gemini-fullstack` agent, you're in the right place! All functionality remains the same.

The **Deep Search Agent Development Kit (ADK) Quickstart** is a production-ready blueprint for building a sophisticated, fullstack research agent with Gemini. It's built to demonstrate how the ADK helps structure complex agentic workflows, build modular agents, and incorporate critical Human-in-the-Loop (HITL) steps.

<table>
  <thead>
    <tr>
      <th colspan="2">Key Features</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🏗️</td>
      <td><strong>Fullstack & Production-Ready:</strong> A complete React frontend and ADK-powered FastAPI backend, with deployment options for <a href="https://cloud.google.com/run">Google Cloud Run</a> and <a href="https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview">Vertex AI Agent Engine</a>.</td>
    </tr>
    <tr>
      <td>🧠</td>
      <td><strong>Advanced Agentic Workflow:</strong> The agent uses Gemini to <strong>strategize</strong> a multi-step plan, <strong>reflect</strong> on findings to identify gaps, and <strong>synthesize</strong> a final, comprehensive report.</td>
    </tr>
    <tr>
      <td>🔄</td>
      <td><strong>Iterative & Human-in-the-Loop Research:</strong> Involves the user for plan approval, then autonomously loops through searching (via Gemini function calling) and refining its results until it has gathered sufficient information.</td>
    </tr>
  </tbody>
</table>

Here is the agent in action:

<img src="https://github.com/GoogleCloudPlatform/agent-starter-pack/blob/main/docs/images/adk_gemini_fullstack.gif?raw=true" width="80%" alt="Gemini Fullstack ADK Preview">

This project adapts concepts from the [Gemini FullStack LangGraph Quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) for the frontend app. 

## 🚀 Getting Started: From Zero to Running Agent in 1 Minute
**Prerequisites:** **[Python 3.10+](https://www.python.org/downloads/)**, **[Node.js](https://nodejs.org/)**, **[uv](https://github.com/astral-sh/uv)**

You have two options to get started. Choose the one that best fits your setup:

*   A. **[Google AI Studio (Recommended)](#a-google-ai-studio-recommended)**: The quickest way to get started using a **Google AI Studio API key**. This method involves cloning the sample repository.
*   B. **[Google Cloud Vertex AI](#b-google-cloud-vertex-ai)**: Choose this path if you want to use an existing **Google Cloud project** for authentication and deployment. This method generates a new, prod-ready project using the [agent-starter-pack](https://goo.gle/agent-starter-pack) including all the deployment scripts required.

---

### A. Google AI Studio (Recommended)

You'll need a **[Google AI Studio API Key](https://aistudio.google.com/app/apikey)**.

#### Step 1: Clone Repository
Clone the repository and `cd` into the project directory.

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/deep-search
```

#### Step 2: Set Environment Variables
Create a `.env` file in the `app` folder with your API key (see `.env.example` for reference):

```bash
echo "GOOGLE_API_KEY=YOUR_AI_STUDIO_API_KEY" >> app/.env
```

#### Step 3: Install & Run
From the `deep-search` directory, install dependencies and start the servers.

```bash
make install && make dev
```
Your agent is now running at `http://localhost:5173`.

---

### B. Google Cloud Vertex AI (via Agent Starter Pack)

Use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready project with deployment scripts. This is ideal for cloud deployment scenarios.

You'll need: **[Google Cloud SDK](https://cloud.google.com/sdk/docs/install)** and a **Google Cloud Project** with the **Vertex AI API** enabled.

<details>
<summary>📁 Alternative: Using the cloned repository with Vertex AI</summary>

If you've already cloned the repository (as in Option A) and want to use Vertex AI instead of AI Studio, create a `.env` file in the `app` folder with:

```bash
echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> app/.env
echo "GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" >> app/.env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> app/.env
```

Make sure you're authenticated with Google Cloud:
```bash
gcloud auth application-default login
```

Then run `make install && make dev` to start the agent.
</details>

#### Step 1: Create Project from Template
This command uses the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a new directory (`my-fullstack-agent`) with all the necessary code.
```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-fullstack-agent -a adk@deep-search
```
<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-fullstack-agent -a adk@deep-search
```
This command handles creating the project without needing to pre-install the package into a virtual environment.
</details>

You'll be prompted to select a deployment option (Agent Engine or Cloud Run) and verify your Google Cloud credentials.

#### Step 2: Install & Run
Navigate into your **newly created project folder**, then install dependencies and start the servers.
```bash
cd my-fullstack-agent && make install && make dev
```
Your agent is now running at `http://localhost:5173`.

## ☁️ Cloud Deployment

> **Note:** Cloud deployment applies only to projects created with **agent-starter-pack** (Option B).

**Prerequisites:**
```bash
gcloud components update
gcloud config set project YOUR_PROJECT_ID
```

#### Option 1: Deploy with ADK Web UI (Default)

For a quick deployment using the built-in [adk-web](https://github.com/google/adk-web) interface:

```bash
make deploy IAP=true
```

#### Option 2: Deploy with Custom UI (React Frontend)

This agent includes a custom React frontend. To deploy it:

1. **Configure the Dockerfile** - See the [Deploy UI Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deploy-ui.html) for the required Dockerfile changes.

2. **Deploy with the frontend port:**
```bash
make deploy IAP=true PORT=5173
```

#### After Deployment

Once deployed, grant users access to your IAP-protected service by following the [Manage User Access](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access) documentation.

For production deployments with CI/CD, see the [Agent Starter Pack Development Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html#b-production-ready-deployment-with-ci-cd).

## Agent Details

| Attribute | Description |
| :--- | :--- |
| **Interaction Type** | Workflow |
| **Complexity** | Advanced |
| **Agent Type** | Multi Agent |
| **Components** | Multi-agent, Function calling, Web search, React frontend, Human-in-the-Loop |
| **Vertical** | Horizontal |

## How the Agent Thinks: A Two-Phase Workflow

The backend agent, defined in `app/agent.py`, follows a sophisticated workflow to move from a simple topic to a fully-researched report.

The following diagram illustrates the agent's architecture and workflow:

![ADK Gemini Fullstack Architecture](https://github.com/GoogleCloudPlatform/agent-starter-pack/blob/main/docs/images/adk_gemini_fullstack_architecture.png?raw=true)

This process is broken into two main phases:

### Phase 1: Plan & Refine (Human-in-the-Loop)

This is the collaborative brainstorming phase.

1.  **You provide a research topic.**
2.  The agent generates a high-level research plan with several key goals (e.g., "Analyze the market impact," "Identify key competitors").
3.  The plan is presented to **you**. You can approve it, or chat with the agent to add, remove, or change goals until you're satisfied. Nothing happens without your explicit approval.

The plan will contains following tags as a signal to downstream agents,
  - Research Plan Tags

    - [RESEARCH]: Guides info gathering via search.
    - [DELIVERABLE]: Guides creation of final outputs (e.g., tables, reports).
  
  - Plan Refinement Tags

    - [MODIFIED]: Goal was updated.
    - [NEW]: New goal added per user.
    - [IMPLIED]: Deliverable proactively added by AI.

### Phase 2: Execute Autonomous Research

Once you approve the plan, the agent's `research_pipeline` takes over and works autonomously.

1.  **Outlining:** It first converts the approved plan into a structured report outline (like a table of contents).
2.  **Iterative Research & Critique Loop:** For each section of the outline, it repeats a cycle:
    *   **Search:** It performs web searches to gather information.
    *   **Critique:** A "critic" model evaluates the findings for gaps or weaknesses.
    *   **Refine:** If the critique finds weaknesses, the agent generates more specific follow-up questions and searches again. This loop continues until the research meets a high-quality bar.
3.  **Compose Final Report:** After the research loop is complete, a final agent takes all the verified findings and writes a polished report, automatically adding inline citations that link back to the original sources.

You can edit key parameters (Gemini models, research loop iterations) in the `ResearchConfiguration` dataclass within `app/config.py`.

## Customization

You can modify and extend this agent's behavior by editing the backend code.

*   **Modifying Agent Logic:** The core logic for all sub-agents (planner, researcher, critic, composer) is defined in `app/agent.py`. You can change the prompts, tools, or reasoning steps by modifying the agent definitions here.
*   **Adjusting Research Parameters:** Key parameters, such as the Gemini models used or the number of research loop iterations, can be adjusted in the `ResearchConfiguration` dataclass within `app/config.py`.
*   **Syncing with Frontend:** The frontend UI integrates with the backend through specific agent names that process outputs differently (e.g., research findings vs. final report), update the activity timeline with appropriate titles/icons, and track research metrics like website counts. 
    Important agent names include:
    * `section_researcher` & `enhanced_search_executor` - track websites consulted
    * `report_composer_with_citations` - processes final report
    * `interactive_planner_agent` - updates AI messages during planning
    * `plan_generator` and `section_planner` - used for timeline labels
    
    If you rename agents in `app/agent.py`, you must update their names in the frontend code (`/ui`) to maintain functionality.


### Example Interaction

> **User:** A report on the last Google I/O
>
> **Agent:** Here's a research plan for a report on the last Google I/O:
>
> *   Analyze the key announcements and product updates made at Google I/O 2025.
> *   Identify the central themes and strategic directions emphasized by Google during the event, particularly concerning AI, Android, and other emerging technologies like Android XR.
> *   Investigate the reception and industry impact of the major product unveilings and feature enhancements.
> *   Examine any significant shifts or continuities in Google's developer strategy as presented at the conference.
> *   Assess the implications of the announced technologies and initiatives for developers, consumers, and the broader tech landscape.
>
> Does this plan look good, or would you like to refine it further? Once approved, I can initiate the research.
>
> **User:** Looks good!
> *(The agent proceeds to autonomously execute the research, showing its progress on the timeline.)*
>
> **Agent:**
> 
> Google I/O 2025: Key Announcements and Highlights
> ....

## Troubleshooting

If you encounter issues while setting up or running this agent, here are some resources to help you troubleshoot:
- [ADK Documentation](https://google.github.io/adk-docs/): Comprehensive documentation for the Agent Development Kit
- [Vertex AI Authentication Guide](https://cloud.google.com/vertex-ai/docs/authentication): Detailed instructions for setting up authentication
- [Agent Starter Pack Troubleshooting](https://googlecloudplatform.github.io/agent-starter-pack/guide/troubleshooting.html): Common issues


## 🛠️ Technologies Used

### Backend
*   [**Agent Development Kit (ADK)**](https://github.com/google/adk-python): The core framework for building the stateful, multi-turn agent.
*   [**FastAPI**](https://fastapi.tiangolo.com/): High-performance web framework for the backend API.
*   [**Google Gemini**](https://cloud.google.com/vertex-ai/generative-ai/docs): Used for planning, reasoning, search query generation, and final synthesis.

### Frontend
*   [**React**](https://reactjs.org/) (with [Vite](https://vitejs.dev/)): For building the interactive user interface.
*   [**Tailwind CSS**](https://tailwindcss.com/): For utility-first styling.
*   [**Shadcn UI**](https://ui.shadcn.com/): A set of beautifully designed, accessible components.

## Disclaimer

This agent sample is provided for illustrative purposes only. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.

---


## File: docs/agents/google-adk/examples/firecrawl/app/README.md

# ChatGPT Agentic Clone

This project demonstrates a versatile agentic AI assistant built using Google's Agent Development Kit (ADK). It implements a ChatGPT-like clone with additional capabilities:

- Answer general knowledge questions using the LLM's training
- Search the web for real-time information using Firecrawl
- Extract and analyze content from web pages
- Perform deep research on complex topics with source citations
- Generate images based on text descriptions via Gemini's image generation models

## Project Structure

```
app/
├── .env                       # API key configuration
├── main.py                    # Runner application
├── requirements.txt           # Dependencies
└── chatgpt_agentic_clone/     # Agent package
    ├── __init__.py            # Package marker
    └── agent.py               # Agent definitions and tools
```

## Prerequisites

- Python 3.9+
- [Google AI Studio API Key](https://aistudio.google.com/app/apikey) for both Gemini models and image generation
- [Firecrawl API Key](https://www.firecrawl.dev) for web search, extraction, and research

## Setup Instructions

1. Create a virtual environment (recommended):

   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Configure your API keys:
   - Edit the `.env` file and add your actual API keys:

     ```
     # Gemini API Key
     GOOGLE_API_KEY=your_google_api_key_here
     
     # Firecrawl API Key (if required)
     FIRECRAWL_API_KEY=your_firecrawl_api_key_here
     ```

## Running the Agent

### Using the CLI

Run the main application to start an interactive CLI session:

```
python main.py
```

You can specify custom session and user IDs:

```
python main.py --session-id custom_session --user-id custom_user
```

### Using the ADK Web UI

Alternatively, you can run the agent using ADK's built-in web UI:

```
cd ..  # Move to parent directory
adk web
```

Then open the URL (typically <http://localhost:8000>) in your browser and select "chatgpt_agentic_clone" from the dropdown.

## Testing the Agent

Try the following types of queries:

- **General knowledge**: "Who was Marie Curie?", "How does photosynthesis work?"
- **Web search**: "What's the weather in London right now?", "Latest news about AI"
- **Web extraction**: "Extract content from <https://github.com/trending>"
- **Structured extraction**: "Extract the trending repositories from <https://github.com/trending>"
- **Deep research**: "Do deep research on quantum computing advances"
- **Image generation**: "Generate an image of a cat playing piano"

## Agent Components

The system is composed of multiple specialized agents:

1. **Root Agent**: Coordinates everything and handles general knowledge queries
2. **Search Agent**: Searches the web for real-time information
3. **Web Extraction Agent**: Extracts content from web pages
4. **Research Agent**: Conducts deep research with multiple sources
5. **Image Generation Agent**: Creates images from text descriptions

## Tools & Capabilities

- **web_search**: Searches the web using Firecrawl
- **scrape_webpage**: Extracts content from a URL in various formats (markdown, HTML, links)
- **extract_structured_data**: Extracts specific structured data from a webpage
- **deep_research**: Researches a topic in-depth using multiple sources
- **generate_image**: Creates images using Gemini's image generation model

## Safety Features

The agent includes content filtering via the `content_filter_callback` to prevent harmful requests.

## License

This project is for educational purposes.

---


## File: docs/agents/google-adk/examples/firecrawl/docs/agent-team.md

[Skip to content](https://google.github.io/adk-docs/tutorials/agent-team/#build-your-first-intelligent-agent-team-a-progressive-weather-bot-with-adk)

# Build Your First Intelligent Agent Team: A Progressive Weather Bot with ADK [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#build-your-first-intelligent-agent-team-a-progressive-weather-bot-with-adk "Permanent link")

[![Google Colaboratory logo](https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg)Open in Colab](https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb)

Share to: [![LinkedIn logo](https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg)](https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on LinkedIn") [![Bluesky logo](https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg)](https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on Bluesky") [![X logo](https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg)](https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on X (Twitter)") [![Reddit logo](https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png)](https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on Reddit") [![Facebook logo](https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg)](https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on Facebook")

This tutorial extends from the [Quickstart example](https://google.github.io/adk-docs/get-started/quickstart/) for [Agent Development Kit](https://google.github.io/adk-docs/get-started/). Now, you're ready to dive deeper and construct a more sophisticated, **multi-agent system**.

We'll embark on building a **Weather Bot agent team**, progressively layering advanced features onto a simple foundation. Starting with a single agent that can look up weather, we will incrementally add capabilities like:

- Leveraging different AI models (Gemini, GPT, Claude).
- Designing specialized sub-agents for distinct tasks (like greetings and farewells).
- Enabling intelligent delegation between agents.
- Giving agents memory using persistent session state.
- Implementing crucial safety guardrails using callbacks.

**Why a Weather Bot Team?**

This use case, while seemingly simple, provides a practical and relatable canvas to explore core ADK concepts essential for building complex, real-world agentic applications. You'll learn how to structure interactions, manage state, ensure safety, and orchestrate multiple AI "brains" working together.

**What is ADK Again?**

As a reminder, ADK is a Python framework designed to streamline the development of applications powered by Large Language Models (LLMs). It offers robust building blocks for creating agents that can reason, plan, utilize tools, interact dynamically with users, and collaborate effectively within a team.

**In this advanced tutorial, you will master:**

- ✅ **Tool Definition & Usage:** Crafting Python functions ( `tools`) that grant agents specific abilities (like fetching data) and instructing agents on how to use them effectively.
- ✅ **Multi-LLM Flexibility:** Configuring agents to utilize various leading LLMs (Gemini, GPT-4o, Claude Sonnet) via LiteLLM integration, allowing you to choose the best model for each task.
- ✅ **Agent Delegation & Collaboration:** Designing specialized sub-agents and enabling automatic routing ( `auto flow`) of user requests to the most appropriate agent within a team.
- ✅ **Session State for Memory:** Utilizing `Session State` and `ToolContext` to enable agents to remember information across conversational turns, leading to more contextual interactions.
- ✅ **Safety Guardrails with Callbacks:** Implementing `before_model_callback` and `before_tool_callback` to inspect, modify, or block requests/tool usage based on predefined rules, enhancing application safety and control.

**End State Expectation:**

By completing this tutorial, you will have built a functional multi-agent Weather Bot system. This system will not only provide weather information but also handle conversational niceties, remember the last city checked, and operate within defined safety boundaries, all orchestrated using ADK.

**Prerequisites:**

- ✅ **Solid understanding of Python programming.**
- ✅ **Familiarity with Large Language Models (LLMs), APIs, and the concept of agents.**
- ❗ **Crucially: Completion of the ADK Quickstart tutorial(s) or equivalent foundational knowledge of ADK basics (Agent, Runner, SessionService, basic Tool usage).** This tutorial builds directly upon those concepts.
- ✅ **API Keys** for the LLMs you intend to use (e.g., Google AI Studio for Gemini, OpenAI Platform, Anthropic Console).

* * *

**Note on Execution Environment:**

This tutorial is structured for interactive notebook environments like Google Colab, Colab Enterprise, or Jupyter notebooks. Please keep the following in mind:

- **Running Async Code:** Notebook environments handle asynchronous code differently. You'll see examples using `await` (suitable when an event loop is already running, common in notebooks) or `asyncio.run()` (often needed when running as a standalone `.py` script or in specific notebook setups). The code blocks provide guidance for both scenarios.
- **Manual Runner/Session Setup:** The steps involve explicitly creating `Runner` and `SessionService` instances. This approach is shown because it gives you fine-grained control over the agent's execution lifecycle, session management, and state persistence.

**Alternative: Using ADK's Built-in Tools (Web UI / CLI / API Server)**

If you prefer a setup that handles the runner and session management automatically using ADK's standard tools, you can find the equivalent code structured for that purpose [here](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial). That version is designed to be run directly with commands like `adk web` (for a web UI), `adk run` (for CLI interaction), or `adk api_server` (to expose an API). Please follow the `README.md` instructions provided in that alternative resource.

* * *

**Ready to build your agent team? Let's dive in!**

```md-code__content
# @title Step 0: Setup and Installation
# Install ADK and LiteLLM for multi-model support

!pip install google-adk -q
!pip install litellm -q

print("Installation complete.")

```

```md-code__content
# @title Import necessary libraries
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")

```

```md-code__content
# @title Configure API Keys (Replace with your actual keys!)

# --- IMPORTANT: Replace placeholders with your real API keys ---

# Gemini API Key (Get from Google AI Studio: https://aistudio.google.com/app/apikey)
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY" # <--- REPLACE

# [Optional]
# OpenAI API Key (Get from OpenAI Platform: https://platform.openai.com/api-keys)
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY' # <--- REPLACE

# [Optional]
# Anthropic API Key (Get from Anthropic Console: https://console.anthropic.com/settings/keys)
os.environ['ANTHROPIC_API_KEY'] = 'YOUR_ANTHROPIC_API_KEY' # <--- REPLACE

# --- Verify Keys (Optional Check) ---
print("API Keys Set:")
print(f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

# Configure ADK to use API keys directly (not Vertex AI for this multi-model setup)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# @markdown **Security Note:** It's best practice to manage API keys securely (e.g., using Colab Secrets or environment variables) rather than hardcoding them directly in the notebook. Replace the placeholder strings above.

```

```md-code__content
# --- Define Model Constants for easier use ---

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# Note: Specific model names might change. Refer to LiteLLM/Provider documentation.
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"

print("\nEnvironment configured.")

```

* * *

## Step 1: Your First Agent - Basic Weather Lookup [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#step-1-your-first-agent-basic-weather-lookup "Permanent link")

Let's begin by building the fundamental component of our Weather Bot: a single agent capable of performing a specific task – looking up weather information. This involves creating two core pieces:

1. **A Tool:** A Python function that equips the agent with the _ability_ to fetch weather data.
2. **An Agent:** The AI "brain" that understands the user's request, knows it has a weather tool, and decides when and how to use it.

* * *

**1\. Define the Tool ( `get_weather`)**

In ADK, **Tools** are the building blocks that give agents concrete capabilities beyond just text generation. They are typically regular Python functions that perform specific actions, like calling an API, querying a database, or performing calculations.

Our first tool will provide a _mock_ weather report. This allows us to focus on the agent structure without needing external API keys yet. Later, you could easily swap this mock function with one that calls a real weather service.

**Key Concept: Docstrings are Crucial!** The agent's LLM relies heavily on the function's **docstring** to understand:

- _What_ the tool does.
- _When_ to use it.
- _What arguments_ it requires ( `city: str`).
- _What information_ it returns.

**Best Practice:** Write clear, descriptive, and accurate docstrings for your tools. This is essential for the LLM to use the tool correctly.

```md-code__content
# @title Define the get_weather Tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# Example tool usage (optional test)
print(get_weather("New York"))
print(get_weather("Paris"))

```

* * *

**2\. Define the Agent ( `weather_agent`)**

Now, let's create the **Agent** itself. An `Agent` in ADK orchestrates the interaction between the user, the LLM, and the available tools.

We configure it with several key parameters:

- `name`: A unique identifier for this agent (e.g., "weather\_agent\_v1").
- `model`: Specifies which LLM to use (e.g., `MODEL_GEMINI_2_0_FLASH`). We'll start with a specific Gemini model.
- `description`: A concise summary of the agent's overall purpose. This becomes crucial later when other agents need to decide whether to delegate tasks to _this_ agent.
- `instruction`: Detailed guidance for the LLM on how to behave, its persona, its goals, and specifically _how and when_ to utilize its assigned `tools`.
- `tools`: A list containing the actual Python tool functions the agent is allowed to use (e.g., `[get_weather]`).

**Best Practice:** Provide clear and specific `instruction` prompts. The more detailed the instructions, the better the LLM can understand its role and how to use its tools effectively. Be explicit about error handling if needed.

**Best Practice:** Choose descriptive `name` and `description` values. These are used internally by ADK and are vital for features like automatic delegation (covered later).

```md-code__content
# @title Define the Weather Agent
# Use one of the model constants defined earlier
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Starting with Gemini

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather], # Pass the function directly
)

print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")

```

* * *

**3\. Setup Runner and Session Service**

To manage conversations and execute the agent, we need two more components:

- `SessionService`: Responsible for managing conversation history and state for different users and sessions. The `InMemorySessionService` is a simple implementation that stores everything in memory, suitable for testing and simple applications. It keeps track of the messages exchanged. We'll explore state persistence more in Step 4.
- `Runner`: The engine that orchestrates the interaction flow. It takes user input, routes it to the appropriate agent, manages calls to the LLM and tools based on the agent's logic, handles session updates via the `SessionService`, and yields events representing the progress of the interaction.

```md-code__content
# @title Setup Session Service and Runner

# --- Session Management ---
# Key Concept: SessionService stores conversation history & state.
# InMemorySessionService is simple, non-persistent storage for this tutorial.
session_service = InMemorySessionService()

# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- Runner ---
# Key Concept: Runner orchestrates the agent execution loop.
runner = Runner(
    agent=weather_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")

```

* * *

**4\. Interact with the Agent**

We need a way to send messages to our agent and receive its responses. Since LLM calls and tool executions can take time, ADK's `Runner` operates asynchronously.

We'll define an `async` helper function ( `call_agent_async`) that:

1. Takes a user query string.
2. Packages it into the ADK `Content` format.
3. Calls `runner.run_async`, providing the user/session context and the new message.
4. Iterates through the **Events** yielded by the runner. Events represent steps in the agent's execution (e.g., tool call requested, tool result received, intermediate LLM thought, final response).
5. Identifies and prints the **final response** event using `event.is_final_response()`.

**Why `async`?** Interactions with LLMs and potentially tools (like external APIs) are I/O-bound operations. Using `asyncio` allows the program to handle these operations efficiently without blocking execution.

```md-code__content
# @title Define Agent Interaction Function

from google.genai import types # For creating message Content/Parts

async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  print(f"<<< Agent Response: {final_response_text}")

```

* * *

**5\. Run the Conversation**

Finally, let's test our setup by sending a few queries to the agent. We wrap our `async` calls in a main `async` function and run it using `await`.

Watch the output:

- See the user queries.
- Notice the `--- Tool: get_weather called... ---` logs when the agent uses the tool.
- Observe the agent's final responses, including how it handles the case where weather data isn't available (for Paris).

```md-code__content
# @title Run the Initial Conversation

# We need an async function to await our interaction helper
async def run_conversation():
    await call_agent_async("What is the weather like in London?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # Expecting the tool's error message

    await call_agent_async("Tell me the weather in New York",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# Execute the conversation using await in an async context (like Colab/Jupyter)
await run_conversation()

# --- OR ---

# Uncomment the following lines if running as a standard Python script (.py file):
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")

```

* * *

Congratulations! You've successfully built and interacted with your first ADK agent. It understands the user's request, uses a tool to find information, and responds appropriately based on the tool's result.

In the next step, we'll explore how to easily switch the underlying Language Model powering this agent.

## Step 2: Going Multi-Model with LiteLLM \[Optional\] [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#step-2-going-multi-model-with-litellm-optional "Permanent link")

In Step 1, we built a functional Weather Agent powered by a specific Gemini model. While effective, real-world applications often benefit from the flexibility to use _different_ Large Language Models (LLMs). Why?

- **Performance:** Some models excel at specific tasks (e.g., coding, reasoning, creative writing).
- **Cost:** Different models have varying price points.
- **Capabilities:** Models offer diverse features, context window sizes, and fine-tuning options.
- **Availability/Redundancy:** Having alternatives ensures your application remains functional even if one provider experiences issues.

ADK makes switching between models seamless through its integration with the [**LiteLLM**](https://github.com/BerriAI/litellm) library. LiteLLM acts as a consistent interface to over 100 different LLMs.

**In this step, we will:**

1. Learn how to configure an ADK `Agent` to use models from providers like OpenAI (GPT) and Anthropic (Claude) using the `LiteLlm` wrapper.
2. Define, configure (with their own sessions and runners), and immediately test instances of our Weather Agent, each backed by a different LLM.
3. Interact with these different agents to observe potential variations in their responses, even when using the same underlying tool.

* * *

**1\. Import `LiteLlm`**

We imported this during the initial setup (Step 0), but it's the key component for multi-model support:

```md-code__content
# @title 1. Import LiteLlm
from google.adk.models.lite_llm import LiteLlm

```

**2\. Define and Test Multi-Model Agents**

Instead of passing only a model name string (which defaults to Google's Gemini models), we wrap the desired model identifier string within the `LiteLlm` class.

- **Key Concept: `LiteLlm` Wrapper:** The `LiteLlm(model="provider/model_name")` syntax tells ADK to route requests for this agent through the LiteLLM library to the specified model provider.

Make sure you have configured the necessary API keys for OpenAI and Anthropic in Step 0. We'll use the `call_agent_async` function (defined earlier, which now accepts `runner`, `user_id`, and `session_id`) to interact with each agent immediately after its setup.

Each block below will:
\\*Define the agent using a specific LiteLLM model ( `MODEL_GPT_4O` or `MODEL_CLAUDE_SONNET`).
\\* Create a _new, separate_ `InMemorySessionService` and session specifically for that agent's test run. This keeps the conversation histories isolated for this demonstration.
\\*Create a `Runner` configured for the specific agent and its session service.
\\* Immediately call `call_agent_async` to send a query and test the agent.

**Best Practice:** Use constants for model names (like `MODEL_GPT_4O`, `MODEL_CLAUDE_SONNET` defined in Step 0) to avoid typos and make code easier to manage.

**Error Handling:** We wrap the agent definitions in `try...except` blocks. This prevents the entire code cell from failing if an API key for a specific provider is missing or invalid, allowing the tutorial to proceed with the models that _are_ configured.

First, let's create and test the agent using OpenAI's GPT-4o.

```md-code__content
# @title Define and Test GPT Agent

# Make sure 'get_weather' function from Step 1 is defined in your environment.
# Make sure 'call_agent_async' is defined from earlier.

# --- Agent using GPT-4o ---
weather_agent_gpt = None # Initialize to None
runner_gpt = None      # Initialize runner to None

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # Key change: Wrap the LiteLLM model identifier
        model=LiteLlm(model=MODEL_GPT_4O),
        description="Provides weather information (using GPT-4o).",
        instruction="You are a helpful weather assistant powered by GPT-4o. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Clearly present successful reports or polite error messages based on the tool's output status.",
        tools=[get_weather], # Re-use the same tool
    )
    print(f"Agent '{weather_agent_gpt.name}' created using model '{MODEL_GPT_4O}'.")

    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    session_service_gpt = InMemorySessionService() # Create a dedicated service

    # Define constants for identifying the interaction context
    APP_NAME_GPT = "weather_tutorial_app_gpt" # Unique app name for this test
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session_gpt = session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"Session created: App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")

    # Create a runner specific to this agent and its session service
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # Use the specific app name
        session_service=session_service_gpt # Use the specific session service
        )
    print(f"Runner created for agent '{runner_gpt.agent.name}'.")

    # --- Test the GPT Agent ---
    print("\n--- Testing GPT Agent ---")
    # Ensure call_agent_async uses the correct runner, user_id, session_id
    await call_agent_async(query = "What's the weather in Tokyo?",
                           runner=runner_gpt,
                           user_id=USER_ID_GPT,
                           session_id=SESSION_ID_GPT)
    # --- OR ---

    # Uncomment the following lines if running as a standard Python script (.py file):
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "What's the weather in Tokyo?",
    #                      runner=runner_gpt,
    #                       user_id=USER_ID_GPT,
    #                       session_id=SESSION_ID_GPT)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

except Exception as e:
    print(f"❌ Could not create or run GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")

```

Next, we'll do the same for Anthropic's Claude Sonnet.

```md-code__content
# @title Define and Test Claude Agent

# Make sure 'get_weather' function from Step 1 is defined in your environment.
# Make sure 'call_agent_async' is defined from earlier.

# --- Agent using Claude Sonnet ---
weather_agent_claude = None # Initialize to None
runner_claude = None      # Initialize runner to None

try:
    weather_agent_claude = Agent(
        name="weather_agent_claude",
        # Key change: Wrap the LiteLLM model identifier
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="Provides weather information (using Claude Sonnet).",
        instruction="You are a helpful weather assistant powered by Claude Sonnet. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Analyze the tool's dictionary output ('status', 'report'/'error_message'). "
                    "Clearly present successful reports or polite error messages.",
        tools=[get_weather], # Re-use the same tool
    )
    print(f"Agent '{weather_agent_claude.name}' created using model '{MODEL_CLAUDE_SONNET}'.")

    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    session_service_claude = InMemorySessionService() # Create a dedicated service

    # Define constants for identifying the interaction context
    APP_NAME_CLAUDE = "weather_tutorial_app_claude" # Unique app name
    USER_ID_CLAUDE = "user_1_claude"
    SESSION_ID_CLAUDE = "session_001_claude" # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session_claude = session_service_claude.create_session(
        app_name=APP_NAME_CLAUDE,
        user_id=USER_ID_CLAUDE,
        session_id=SESSION_ID_CLAUDE
    )
    print(f"Session created: App='{APP_NAME_CLAUDE}', User='{USER_ID_CLAUDE}', Session='{SESSION_ID_CLAUDE}'")

    # Create a runner specific to this agent and its session service
    runner_claude = Runner(
        agent=weather_agent_claude,
        app_name=APP_NAME_CLAUDE,       # Use the specific app name
        session_service=session_service_claude # Use the specific session service
        )
    print(f"Runner created for agent '{runner_claude.agent.name}'.")

    # --- Test the Claude Agent ---
    print("\n--- Testing Claude Agent ---")
    # Ensure call_agent_async uses the correct runner, user_id, session_id
    await call_agent_async(query = "Weather in London please.",
                           runner=runner_claude,
                           user_id=USER_ID_CLAUDE,
                           session_id=SESSION_ID_CLAUDE)

    # --- OR ---

    # Uncomment the following lines if running as a standard Python script (.py file):
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "Weather in London please.",
    #                      runner=runner_claude,
    #                       user_id=USER_ID_CLAUDE,
    #                       session_id=SESSION_ID_CLAUDE)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

except Exception as e:
    print(f"❌ Could not create or run Claude agent '{MODEL_CLAUDE_SONNET}'. Check API Key and model name. Error: {e}")

```

Observe the output carefully from both code blocks. You should see:

1. Each agent ( `weather_agent_gpt`, `weather_agent_claude`) is created successfully (if API keys are valid).
2. A dedicated session and runner are set up for each.
3. Each agent correctly identifies the need to use the `get_weather` tool when processing the query (you'll see the `--- Tool: get_weather called... ---` log).
4. The _underlying tool logic_ remains identical, always returning our mock data.
5. However, the **final textual response** generated by each agent might differ slightly in phrasing, tone, or formatting. This is because the instruction prompt is interpreted and executed by different LLMs (GPT-4o vs. Claude Sonnet).

This step demonstrates the power and flexibility ADK + LiteLLM provide. You can easily experiment with and deploy agents using various LLMs while keeping your core application logic (tools, fundamental agent structure) consistent.

In the next step, we'll move beyond a single agent and build a small team where agents can delegate tasks to each other!

* * *

## Step 3: Building an Agent Team - Delegation for Greetings & Farewells [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#step-3-building-an-agent-team-delegation-for-greetings-farewells "Permanent link")

In Steps 1 and 2, we built and experimented with a single agent focused solely on weather lookups. While effective for its specific task, real-world applications often involve handling a wider variety of user interactions. We _could_ keep adding more tools and complex instructions to our single weather agent, but this can quickly become unmanageable and less efficient.

A more robust approach is to build an **Agent Team**. This involves:

1. Creating multiple, **specialized agents**, each designed for a specific capability (e.g., one for weather, one for greetings, one for calculations).
2. Designating a **root agent** (or orchestrator) that receives the initial user request.
3. Enabling the root agent to **delegate** the request to the most appropriate specialized sub-agent based on the user's intent.

**Why build an Agent Team?**

- **Modularity:** Easier to develop, test, and maintain individual agents.
- **Specialization:** Each agent can be fine-tuned (instructions, model choice) for its specific task.
- **Scalability:** Simpler to add new capabilities by adding new agents.
- **Efficiency:** Allows using potentially simpler/cheaper models for simpler tasks (like greetings).

**In this step, we will:**

1. Define simple tools for handling greetings ( `say_hello`) and farewells ( `say_goodbye`).
2. Create two new specialized sub-agents: `greeting_agent` and `farewell_agent`.
3. Update our main weather agent ( `weather_agent_v2`) to act as the **root agent**.
4. Configure the root agent with its sub-agents, enabling **automatic delegation**.
5. Test the delegation flow by sending different types of requests to the root agent.

* * *

**1\. Define Tools for Sub-Agents**

First, let's create the simple Python functions that will serve as tools for our new specialist agents. Remember, clear docstrings are vital for the agents that will use them.

```md-code__content
# @title Define Tools for Greeting and Farewell Agents

# Ensure 'get_weather' from Step 1 is available if running this step independently.
# def get_weather(city: str) -> dict: ... (from Step 1)

def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

print("Greeting and Farewell tools defined.")

# Optional self-test
print(say_hello("Alice"))
print(say_goodbye())

```

* * *

**2\. Define the Sub-Agents (Greeting & Farewell)**

Now, create the `Agent` instances for our specialists. Notice their highly focused `instruction` and, critically, their clear `description`. The `description` is the primary information the _root agent_ uses to decide _when_ to delegate to these sub-agents.

**Best Practice:** Sub-agent `description` fields should accurately and concisely summarize their specific capability. This is crucial for effective automatic delegation.

**Best Practice:** Sub-agent `instruction` fields should be tailored to their limited scope, telling them exactly what to do and _what not_ to do (e.g., "Your _only_ task is...").

```md-code__content
# @title Define Greeting and Farewell Sub-Agents

# If you want to use models other than Gemini, Ensure LiteLlm is imported and API keys are set (from Step 0/2)
# from google.adk.models.lite_llm import LiteLlm
# MODEL_GPT_4O, MODEL_CLAUDE_SONNET etc. should be defined
# Or else, continue to use: model = MODEL_GEMINI_2_0_FLASH

# --- Greeting Agent ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")

# --- Farewell Agent ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # Can use the same or a different model
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")

```

* * *

**3\. Define the Root Agent (Weather Agent v2) with Sub-Agents**

Now, we upgrade our `weather_agent`. The key changes are:

- Adding the `sub_agents` parameter: We pass a list containing the `greeting_agent` and `farewell_agent` instances we just created.
- Updating the `instruction`: We explicitly tell the root agent _about_ its sub-agents and _when_ it should delegate tasks to them.

**Key Concept: Automatic Delegation (Auto Flow)** By providing the `sub_agents` list, ADK enables automatic delegation. When the root agent receives a user query, its LLM considers not only its own instructions and tools but also the `description` of each sub-agent. If the LLM determines that a query aligns better with a sub-agent's described capability (e.g., "Handles simple greetings"), it will automatically generate a special internal action to _transfer control_ to that sub-agent for that turn. The sub-agent then processes the query using its own model, instructions, and tools.

**Best Practice:** Ensure the root agent's instructions clearly guide its delegation decisions. Mention the sub-agents by name and describe the conditions under which delegation should occur.

```md-code__content
# @title Define the Root Agent with Sub-Agents

# Ensure sub-agents were created successfully before defining the root agent.
# Also ensure the original 'get_weather' tool is defined.
root_agent = None
runner_root = None # Initialize runner

if greeting_agent and farewell_agent and 'get_weather' in globals():
    # Let's use a capable Gemini model for the root agent to handle orchestration
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2", # Give it a new version name
        model=root_agent_model,
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_weather], # Root agent still needs the weather tool for its core task
        # Key change: Link the sub-agents here!
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
    if not greeting_agent: print(" - Greeting Agent is missing.")
    if not farewell_agent: print(" - Farewell Agent is missing.")
    if 'get_weather' not in globals(): print(" - get_weather function is missing.")

```

* * *

**4\. Interact with the Agent Team**

Now that we've defined our root agent ( `weather_agent_team` \- _Note: Ensure this variable name matches the one defined in the previous code block, likely `# @title Define the Root Agent with Sub-Agents`, which might have named it `root_agent`_) with its specialized sub-agents, let's test the delegation mechanism.

The following code block will:

1. Define an `async` function `run_team_conversation`.
2. Inside this function, create a _new, dedicated_ `InMemorySessionService` and a specific session ( `session_001_agent_team`) just for this test run. This isolates the conversation history for testing the team dynamics.
3. Create a `Runner` ( `runner_agent_team`) configured to use our `weather_agent_team` (the root agent) and the dedicated session service.
4. Use our updated `call_agent_async` function to send different types of queries (greeting, weather request, farewell) to the `runner_agent_team`. We explicitly pass the runner, user ID, and session ID for this specific test.
5. Immediately execute the `run_team_conversation` function.

We expect the following flow:

1. The "Hello there!" query goes to `runner_agent_team`.
2. The root agent ( `weather_agent_team`) receives it and, based on its instructions and the `greeting_agent`'s description, delegates the task.
3. `greeting_agent` handles the query, calls its `say_hello` tool, and generates the response.
4. The "What is the weather in New York?" query is _not_ delegated and is handled directly by the root agent using its `get_weather` tool.
5. The "Thanks, bye!" query is delegated to the `farewell_agent`, which uses its `say_goodbye` tool.

```md-code__content
# @title Interact with the Agent Team
import asyncio # Ensure asyncio is imported

# Ensure the root agent (e.g., 'weather_agent_team' or 'root_agent' from the previous cell) is defined.
# Ensure the call_agent_async function is defined.

# Check if the root agent variable exists before defining the conversation function
root_agent_var_name = 'root_agent' # Default name from Step 3 guide
if 'weather_agent_team' in globals(): # Check if user used this name instead
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
    # Assign a dummy value to prevent NameError later if the code block runs anyway
    root_agent = None # Or set a flag to prevent execution

# Only define and run if the root agent exists
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # Define the main async function for the conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_team_conversation():
        print("\n--- Testing Agent Team Delegation ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # Or use InMemoryRunner
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{actual_root_agent.name}'.")

        # --- Interactions using await (correct within async def) ---
        await call_agent_async(query = "Hello there!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "What is the weather in New York?",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "Thanks, bye!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # --- Execute the `run_team_conversation` async function ---
    # Choose ONE of the methods below based on your environment.
    # Note: This may require API keys for the models used!

    # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
    # If your environment supports top-level await (like Colab/Jupyter notebooks),
    # it means an event loop is already running, so you can directly await the function.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_team_conversation()

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.
    # To use this method:
    # 1. Comment out the `await run_team_conversation()` line above.
    # 2. Uncomment the following block:
    """
    import asyncio
    if __name__ == "__main__": # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

else:
    # This message prints if the root agent variable wasn't found earlier
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")

```

* * *

Look closely at the output logs, especially the `--- Tool: ... called ---` messages. You should observe:

- For "Hello there!", the `say_hello` tool was called (indicating `greeting_agent` handled it).
- For "What is the weather in New York?", the `get_weather` tool was called (indicating the root agent handled it).
- For "Thanks, bye!", the `say_goodbye` tool was called (indicating `farewell_agent` handled it).

This confirms successful **automatic delegation**! The root agent, guided by its instructions and the `description` s of its `sub_agents`, correctly routed user requests to the appropriate specialist agent within the team.

You've now structured your application with multiple collaborating agents. This modular design is fundamental for building more complex and capable agent systems. In the next step, we'll give our agents the ability to remember information across turns using session state.

## Step 4: Adding Memory and Personalization with Session State [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#step-4-adding-memory-and-personalization-with-session-state "Permanent link")

So far, our agent team can handle different tasks through delegation, but each interaction starts fresh – the agents have no memory of past conversations or user preferences within a session. To create more sophisticated and context-aware experiences, agents need **memory**. ADK provides this through **Session State**.

**What is Session State?**

- It's a Python dictionary ( `session.state`) tied to a specific user session (identified by `APP_NAME`, `USER_ID`, `SESSION_ID`).
- It persists information _across multiple conversational turns_ within that session.
- Agents and Tools can read from and write to this state, allowing them to remember details, adapt behavior, and personalize responses.

**How Agents Interact with State:**

1. **`ToolContext` (Primary Method):** Tools can accept a `ToolContext` object (automatically provided by ADK if declared as the last argument). This object gives direct access to the session state via `tool_context.state`, allowing tools to read preferences or save results _during_ execution.
2. **`output_key` (Auto-Save Agent Response):** An `Agent` can be configured with an `output_key="your_key"`. ADK will then automatically save the agent's final textual response for a turn into `session.state["your_key"]`.

**In this step, we will enhance our Weather Bot team by:**

1. Using a **new** `InMemorySessionService` to demonstrate state in isolation.
2. Initializing session state with a user preference for `temperature_unit`.
3. Creating a state-aware version of the weather tool ( `get_weather_stateful`) that reads this preference via `ToolContext` and adjusts its output format (Celsius/Fahrenheit).
4. Updating the root agent to use this stateful tool and configuring it with an `output_key` to automatically save its final weather report to the session state.
5. Running a conversation to observe how the initial state affects the tool, how manual state changes alter subsequent behavior, and how `output_key` persists the agent's response.

* * *

**1\. Initialize New Session Service and State**

To clearly demonstrate state management without interference from prior steps, we'll instantiate a new `InMemorySessionService`. We'll also create a session with an initial state defining the user's preferred temperature unit.

```md-code__content
# @title 1. Initialize New Session Service and State

# Import necessary session components
from google.adk.sessions import InMemorySessionService

# Create a NEW session service instance for this state demonstration
session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")

# Define a NEW session ID for this part of the tutorial
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# Define initial state data - user prefers Celsius initially
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# Create the session, providing the initial state
session_stateful = session_service_stateful.create_session(
    app_name=APP_NAME, # Use the consistent app name
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< Initialize state during creation
)
print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

# Verify the initial state was set correctly
retrieved_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- Initial Session State ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("Error: Could not retrieve session.")

```

* * *

**2\. Create State-Aware Weather Tool ( `get_weather_stateful`)**

Now, we create a new version of the weather tool. Its key feature is accepting `tool_context: ToolContext` which allows it to access `tool_context.state`. It will read the `user_preference_temperature_unit` and format the temperature accordingly.

- **Key Concept: `ToolContext`** This object is the bridge allowing your tool logic to interact with the session's context, including reading and writing state variables. ADK injects it automatically if defined as the last parameter of your tool function.

- **Best Practice:** When reading from state, use `dictionary.get('key', default_value)` to handle cases where the key might not exist yet, ensuring your tool doesn't crash.

```md-code__content
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")

```

* * *

**3\. Redefine Sub-Agents and Update Root Agent**

To ensure this step is self-contained and builds correctly, we first redefine the `greeting_agent` and `farewell_agent` exactly as they were in Step 3. Then, we define our new root agent ( `weather_agent_v4_stateful`):

- It uses the new `get_weather_stateful` tool.
- It includes the greeting and farewell sub-agents for delegation.
- **Crucially**, it sets `output_key="last_weather_report"` which automatically saves its final weather response to the session state.

```md-code__content
# @title 3. Redefine Sub-Agents and Update Root Agent with output_key

# Ensure necessary imports: Agent, LiteLlm, Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# Ensure tools 'say_hello', 'say_goodbye' are defined (from Step 3)
# Ensure model constants MODEL_GPT_4O, MODEL_GEMINI_2_0_FLASH etc. are defined

# --- Redefine Greeting Agent (from Step 3) ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Error: {e}")

# --- Redefine Farewell Agent (from Step 3) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")

# --- Define the Updated Root Agent ---
root_agent_stateful = None
runner_root_stateful = None # Initialize runner

# Check prerequisites before creating the root agent
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # Choose orchestration model

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # New version name
        model=root_agent_model,
        description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful], # Use the state-aware tool
        sub_agents=[greeting_agent, farewell_agent], # Include sub-agents
        output_key="last_weather_report" # <<< Auto-save agent's final weather response
    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")

    # --- Create Runner for this Root Agent & NEW Session Service ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # Use the NEW stateful session service
    )
    print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")

else:
    print("❌ Cannot create stateful root agent. Prerequisites missing.")
    if not greeting_agent: print(" - greeting_agent definition missing.")
    if not farewell_agent: print(" - farewell_agent definition missing.")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful tool missing.")

```

* * *

**4\. Interact and Test State Flow**

Now, let's execute a conversation designed to test the state interactions using the `runner_root_stateful` (associated with our stateful agent and the `session_service_stateful`). We'll use the `call_agent_async` function defined earlier, ensuring we pass the correct runner, user ID ( `USER_ID_STATEFUL`), and session ID ( `SESSION_ID_STATEFUL`).

The conversation flow will be:

1. **Check weather (London):** The `get_weather_stateful` tool should read the initial "Celsius" preference from the session state initialized in Section 1. The root agent's final response (the weather report in Celsius) should get saved to `state['last_weather_report']` via the `output_key` configuration.
2. **Manually update state:** We will _directly modify_ the state stored within the `InMemorySessionService` instance ( `session_service_stateful`).
   - **Why direct modification?** The `session_service.get_session()` method returns a _copy_ of the session. Modifying that copy wouldn't affect the state used in subsequent agent runs. For this testing scenario with `InMemorySessionService`, we access the internal `sessions` dictionary to change the _actual_ stored state value for `user_preference_temperature_unit` to "Fahrenheit". _Note: In real applications, state changes are typically triggered by tools or agent logic returning `EventActions(state_delta=...)`, not direct manual updates._
3. **Check weather again (New York):** The `get_weather_stateful` tool should now read the updated "Fahrenheit" preference from the state and convert the temperature accordingly. The root agent's _new_ response (weather in Fahrenheit) will overwrite the previous value in `state['last_weather_report']` due to the `output_key`.
4. **Greet the agent:** Verify that delegation to the `greeting_agent` still works correctly alongside the stateful operations. This interaction will become the _last_ response saved by `output_key` in this specific sequence.
5. **Inspect final state:** After the conversation, we retrieve the session one last time (getting a copy) and print its state to confirm the `user_preference_temperature_unit` is indeed "Fahrenheit", observe the final value saved by `output_key` (which will be the greeting in this run), and see the `last_city_checked_stateful` value written by the tool.

```md-code__content
# @title 4. Interact to Test State Flow and output_key
import asyncio # Ensure asyncio is imported

# Ensure the stateful runner (runner_root_stateful) is available from the previous cell
# Ensure call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME are defined

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # Define the main async function for the stateful conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_stateful_conversation():
        print("\n--- Testing State: Temp Unit Conversion & output_key ---")

        # 1. Check weather (Uses initial state: Celsius)
        print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
        await call_agent_async(query= "What's the weather in London?",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
        print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
        try:
            # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
            # NOTE: In production with persistent services (Database, VertexAI), you would
            # typically update state via agent actions or specific service APIs if available,
            # not by direct manipulation of internal storage.
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # Optional: You might want to update the timestamp as well if any logic depends on it
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---") # Added .get for safety
        except KeyError:
            print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
        except Exception as e:
             print(f"--- Error updating internal session state: {e} ---")

        # 3. Check weather again (Tool should now use Fahrenheit)
        # This will also update 'last_weather_report' via output_key
        print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
        await call_agent_async(query= "Tell me the weather in New York.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. Test basic delegation (should still work)
        # This will update 'last_weather_report' again, overwriting the NY weather report
        print("\n--- Turn 3: Sending a greeting ---")
        await call_agent_async(query= "Hi!",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # --- Execute the `run_stateful_conversation` async function ---
    # Choose ONE of the methods below based on your environment.

    # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
    # If your environment supports top-level await (like Colab/Jupyter notebooks),
    # it means an event loop is already running, so you can directly await the function.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_stateful_conversation()

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.
    # To use this method:
    # 1. Comment out the `await run_stateful_conversation()` line above.
    # 2. Uncomment the following block:
    """
    import asyncio
    if __name__ == "__main__": # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- Inspect final session state after the conversation ---
    # This block runs after either execution method completes.
    print("\n--- Inspecting Final Session State ---")
    final_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id= USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # Use .get() for safer access to potentially missing keys
        print(f"Final Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}")
        print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}")
        # Print full state for detailed view
        # print(f"Full State Dict: {final_session.state.as_dict()}") # Use as_dict() for clarity
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")

```

* * *

By reviewing the conversation flow and the final session state printout, you can confirm:

- **State Read:** The weather tool ( `get_weather_stateful`) correctly read `user_preference_temperature_unit` from state, initially using "Celsius" for London.
- **State Update:** The direct modification successfully changed the stored preference to "Fahrenheit".
- **State Read (Updated):** The tool subsequently read "Fahrenheit" when asked for New York's weather and performed the conversion.
- **Tool State Write:** The tool successfully wrote the `last_city_checked_stateful` ("New York" after the second weather check) into the state via `tool_context.state`.
- **Delegation:** The delegation to the `greeting_agent` for "Hi!" functioned correctly even after state modifications.
- **`output_key`:** The `output_key="last_weather_report"` successfully saved the root agent's _final_ response for _each turn_ where the root agent was the one ultimately responding. In this sequence, the last response was the greeting ("Hello, there!"), so that overwrote the weather report in the state key.
- **Final State:** The final check confirms the preference persisted as "Fahrenheit".

You've now successfully integrated session state to personalize agent behavior using `ToolContext`, manually manipulated state for testing `InMemorySessionService`, and observed how `output_key` provides a simple mechanism for saving the agent's last response to state. This foundational understanding of state management is key as we proceed to implement safety guardrails using callbacks in the next steps.

* * *

## Step 5: Adding Safety - Input Guardrail with `before_model_callback` [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#step-5-adding-safety-input-guardrail-with-before_model_callback "Permanent link")

Our agent team is becoming more capable, remembering preferences and using tools effectively. However, in real-world scenarios, we often need safety mechanisms to control the agent's behavior _before_ potentially problematic requests even reach the core Large Language Model (LLM).

ADK provides **Callbacks** – functions that allow you to hook into specific points in the agent's execution lifecycle. The `before_model_callback` is particularly useful for input safety.

**What is `before_model_callback`?**

- It's a Python function you define that ADK executes _just before_ an agent sends its compiled request (including conversation history, instructions, and the latest user message) to the underlying LLM.
- **Purpose:** Inspect the request, modify it if necessary, or block it entirely based on predefined rules.

**Common Use Cases:**

- **Input Validation/Filtering:** Check if user input meets criteria or contains disallowed content (like PII or keywords).
- **Guardrails:** Prevent harmful, off-topic, or policy-violating requests from being processed by the LLM.
- **Dynamic Prompt Modification:** Add timely information (e.g., from session state) to the LLM request context just before sending.

**How it Works:**

1. Define a function accepting `callback_context: CallbackContext` and `llm_request: LlmRequest`.
2. `callback_context`: Provides access to agent info, session state ( `callback_context.state`), etc.
3. `llm_request`: Contains the full payload intended for the LLM ( `contents`, `config`).
4. Inside the function:
5. **Inspect:** Examine `llm_request.contents` (especially the last user message).
6. **Modify (Use Caution):** You _can_ change parts of `llm_request`.
7. **Block (Guardrail):** Return an `LlmResponse` object. ADK will send this response back immediately, _skipping_ the LLM call for that turn.
8. **Allow:** Return `None`. ADK proceeds to call the LLM with the (potentially modified) request.

**In this step, we will:**

1. Define a `before_model_callback` function ( `block_keyword_guardrail`) that checks the user's input for a specific keyword ("BLOCK").
2. Update our stateful root agent ( `weather_agent_v4_stateful` from Step 4) to use this callback.
3. Create a new runner associated with this updated agent but using the _same stateful session service_ to maintain state continuity.
4. Test the guardrail by sending both normal and keyword-containing requests.

* * *

**1\. Define the Guardrail Callback Function**

This function will inspect the last user message within the `llm_request` content. If it finds "BLOCK" (case-insensitive), it constructs and returns an `LlmResponse` to block the flow; otherwise, it returns `None`.

```md-code__content
# @title 1. Define the before_model_callback Guardrail

# Ensure necessary imports are available
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # For creating response content
from typing import Optional

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # Found the last user message text

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # Log first 100 chars

    # --- Guardrail Logic ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # Case-insensitive check
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        # Optionally, set a flag in state to record the block event
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        # Construct and return an LlmResponse to stop the flow and send this back instead
        return LlmResponse(
            content=types.Content(
                role="model", # Mimic a response from the agent's perspective
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
            # Note: You could also set an error_message field here if needed
        )
    else:
        # Keyword not found, allow the request to proceed to the LLM
        print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None # Returning None signals ADK to continue normally

print("✅ block_keyword_guardrail function defined.")

```

* * *

**2\. Update Root Agent to Use the Callback**

We redefine the root agent, adding the `before_model_callback` parameter and pointing it to our new guardrail function. We'll give it a new version name for clarity.

_Important:_ We need to redefine the sub-agents ( `greeting_agent`, `farewell_agent`) and the stateful tool ( `get_weather_stateful`) within this context if they are not already available from previous steps, ensuring the root agent definition has access to all its components.

```md-code__content
# @title 2. Update Root Agent with before_model_callback

# --- Redefine Sub-Agents (Ensures they exist in this context) ---
greeting_agent = None
try:
    # Use a defined model constant
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # Keep original name for consistency
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    # Use a defined model constant
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # Keep original name
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")

# --- Define the Root Agent with the Callback ---
root_agent_model_guardrail = None
runner_root_model_guardrail = None

# Check all components before proceeding
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():

    # Use a defined model constant
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # New version name for clarity
        model=root_agent_model,
        description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather],
        sub_agents=[greeting_agent, farewell_agent], # Reference the redefined sub-agents
        output_key="last_weather_report", # Keep output_key from Step 4
        before_model_callback=block_keyword_guardrail # <<< Assign the guardrail callback
    )
    print(f"✅ Root Agent '{root_agent_model_guardrail.name}' created with before_model_callback.")

    # --- Create Runner for this Agent, Using SAME Stateful Session Service ---
    # Ensure session_service_stateful exists from Step 4
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME, # Use consistent APP_NAME
            session_service=session_service_stateful # <<< Use the service from Step 4
        )
        print(f"✅ Runner created for guardrail agent '{runner_root_model_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4 is missing.")

else:
    print("❌ Cannot create root agent with model guardrail. One or more prerequisites are missing or failed initialization:")
    if not greeting_agent: print("   - Greeting Agent")
    if not farewell_agent: print("   - Farewell Agent")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' tool")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' callback")

```

* * *

**3\. Interact to Test the Guardrail**

Let's test the guardrail's behavior. We'll use the _same session_ ( `SESSION_ID_STATEFUL`) as in Step 4 to show that state persists across these changes.

1. Send a normal weather request (should pass the guardrail and execute).
2. Send a request containing "BLOCK" (should be intercepted by the callback).
3. Send a greeting (should pass the root agent's guardrail, be delegated, and execute normally).

```md-code__content
# @title 3. Interact to Test the Model Input Guardrail
import asyncio # Ensure asyncio is imported

# Ensure the runner for the guardrail agent is available
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
    # Define the main async function for the guardrail test conversation.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_guardrail_test_conversation():
        print("\n--- Testing Model Input Guardrail ---")

        # Use the runner for the agent with the callback and the existing stateful session ID
        # Define a helper lambda for cleaner interaction calls
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_model_guardrail,
                                                         USER_ID_STATEFUL, # Use existing user ID
                                                         SESSION_ID_STATEFUL # Use existing session ID
                                                        )
        # 1. Normal request (Callback allows, should use Fahrenheit from previous state change)
        print("--- Turn 1: Requesting weather in London (expect allowed, Fahrenheit) ---")
        await interaction_func("What is the weather in London?")

        # 2. Request containing the blocked keyword (Callback intercepts)
        print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
        await interaction_func("BLOCK the request for weather in Tokyo") # Callback should catch "BLOCK"

        # 3. Normal greeting (Callback allows root agent, delegation happens)
        print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
        await interaction_func("Hello again")

    # --- Execute the `run_guardrail_test_conversation` async function ---
    # Choose ONE of the methods below based on your environment.

    # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
    # If your environment supports top-level await (like Colab/Jupyter notebooks),
    # it means an event loop is already running, so you can directly await the function.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_guardrail_test_conversation()

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.
    # To use this method:
    # 1. Comment out the `await run_guardrail_test_conversation()` line above.
    # 2. Uncomment the following block:
    """
    import asyncio
    if __name__ == "__main__": # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_guardrail_test_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- Inspect final session state after the conversation ---
    # This block runs after either execution method completes.
    # Optional: Check state for the trigger flag set by the callback
    print("\n--- Inspecting Final Session State (After Guardrail Test) ---")
    # Use the session service instance associated with this stateful session
    final_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # Use .get() for safer access
        print(f"Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered', 'Not Set (or False)')}")
        print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}") # Should be London weather if successful
        print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}") # Should be Fahrenheit
        # print(f"Full State Dict: {final_session.state.as_dict()}") # For detailed view
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping model guardrail test. Runner ('runner_root_model_guardrail') is not available.")

```

* * *

Observe the execution flow:

1. **London Weather:** The callback runs for `weather_agent_v5_model_guardrail`, inspects the message, prints "Keyword not found. Allowing LLM call.", and returns `None`. The agent proceeds, calls the `get_weather_stateful` tool (which uses the "Fahrenheit" preference from Step 4's state change), and returns the weather. This response updates `last_weather_report` via `output_key`.
2. **BLOCK Request:** The callback runs again for `weather_agent_v5_model_guardrail`, inspects the message, finds "BLOCK", prints "Blocking LLM call!", sets the state flag, and returns the predefined `LlmResponse`. The agent's underlying LLM is _never called_ for this turn. The user sees the callback's blocking message.
3. **Hello Again:** The callback runs for `weather_agent_v5_model_guardrail`, allows the request. The root agent then delegates to `greeting_agent`. _Note: The `before_model_callback` defined on the root agent does NOT automatically apply to sub-agents._ The `greeting_agent` proceeds normally, calls its `say_hello` tool, and returns the greeting.

You have successfully implemented an input safety layer! The `before_model_callback` provides a powerful mechanism to enforce rules and control agent behavior _before_ expensive or potentially risky LLM calls are made. Next, we'll apply a similar concept to add guardrails around tool usage itself.

## Step 6: Adding Safety - Tool Argument Guardrail ( `before_tool_callback`) [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#step-6-adding-safety-tool-argument-guardrail-before_tool_callback "Permanent link")

In Step 5, we added a guardrail to inspect and potentially block user input _before_ it reached the LLM. Now, we'll add another layer of control _after_ the LLM has decided to use a tool but _before_ that tool actually executes. This is useful for validating the _arguments_ the LLM wants to pass to the tool.

ADK provides the `before_tool_callback` for this precise purpose.

**What is `before_tool_callback`?**

- It's a Python function executed just _before_ a specific tool function runs, after the LLM has requested its use and decided on the arguments.
- **Purpose:** Validate tool arguments, prevent tool execution based on specific inputs, modify arguments dynamically, or enforce resource usage policies.

**Common Use Cases:**

- **Argument Validation:** Check if arguments provided by the LLM are valid, within allowed ranges, or conform to expected formats.
- **Resource Protection:** Prevent tools from being called with inputs that might be costly, access restricted data, or cause unwanted side effects (e.g., blocking API calls for certain parameters).
- **Dynamic Argument Modification:** Adjust arguments based on session state or other contextual information before the tool runs.

**How it Works:**

1. Define a function accepting `tool: BaseTool`, `args: Dict[str, Any]`, and `tool_context: ToolContext`.
2. `tool`: The tool object about to be called (inspect `tool.name`).
3. `args`: The dictionary of arguments the LLM generated for the tool.
4. `tool_context`: Provides access to session state ( `tool_context.state`), agent info, etc.
5. Inside the function:
6. **Inspect:** Examine the `tool.name` and the `args` dictionary.
7. **Modify:** Change values within the `args` dictionary _directly_. If you return `None`, the tool runs with these modified args.
8. **Block/Override (Guardrail):** Return a **dictionary**. ADK treats this dictionary as the _result_ of the tool call, completely _skipping_ the execution of the original tool function. The dictionary should ideally match the expected return format of the tool it's blocking.
9. **Allow:** Return `None`. ADK proceeds to execute the actual tool function with the (potentially modified) arguments.

**In this step, we will:**

1. Define a `before_tool_callback` function ( `block_paris_tool_guardrail`) that specifically checks if the `get_weather_stateful` tool is called with the city "Paris".
2. If "Paris" is detected, the callback will block the tool and return a custom error dictionary.
3. Update our root agent ( `weather_agent_v6_tool_guardrail`) to include _both_ the `before_model_callback` and this new `before_tool_callback`.
4. Create a new runner for this agent, using the same stateful session service.
5. Test the flow by requesting weather for allowed cities and the blocked city ("Paris").

* * *

**1\. Define the Tool Guardrail Callback Function**

This function targets the `get_weather_stateful` tool. It checks the `city` argument. If it's "Paris", it returns an error dictionary that looks like the tool's own error response. Otherwise, it allows the tool to run by returning `None`.

```md-code__content
# @title 1. Define the before_tool_callback Guardrail

# Ensure necessary imports are available
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # For type hints

def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Checks if 'get_weather_stateful' is called for 'Paris'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # Agent attempting the tool call
    print(f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- Guardrail Logic ---
    target_tool_name = "get_weather_stateful" # Match the function name used by FunctionTool
    blocked_city = "paris"

    # Check if it's the correct tool and the city argument matches the blocked city
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # Safely get the 'city' argument
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
            # Optionally update state
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- Callback: Set state 'guardrail_tool_block_triggered': True ---")

            # Return a dictionary matching the tool's expected output format for errors
            # This dictionary becomes the tool's result, skipping the actual tool run.
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail."
            }
        else:
             print(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
    else:
        print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")

    # If the checks above didn't return a dictionary, allow the tool to execute
    print(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
    return None # Returning None allows the actual tool function to run

print("✅ block_paris_tool_guardrail function defined.")

```

* * *

**2\. Update Root Agent to Use Both Callbacks**

We redefine the root agent again ( `weather_agent_v6_tool_guardrail`), this time adding the `before_tool_callback` parameter alongside the `before_model_callback` from Step 5.

_Self-Contained Execution Note:_ Similar to Step 5, ensure all prerequisites (sub-agents, tools, `before_model_callback`) are defined or available in the execution context before defining this agent.

```md-code__content
# @title 2. Update Root Agent with BOTH Callbacks (Self-Contained)

# --- Ensure Prerequisites are Defined ---
# (Include or ensure execution of definitions for: Agent, LiteLlm, Runner, ToolContext,
#  MODEL constants, say_hello, say_goodbye, greeting_agent, farewell_agent,
#  get_weather_stateful, block_keyword_guardrail, block_paris_tool_guardrail)

# --- Redefine Sub-Agents (Ensures they exist in this context) ---
greeting_agent = None
try:
    # Use a defined model constant
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # Keep original name for consistency
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    # Use a defined model constant
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # Keep original name
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")

# --- Define the Root Agent with Both Callbacks ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # New version name
        model=root_agent_model,
        description="Main agent: Handles weather, delegates, includes input AND tool guardrails.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # Keep model guardrail
        before_tool_callback=block_paris_tool_guardrail # <<< Add tool guardrail
    )
    print(f"✅ Root Agent '{root_agent_tool_guardrail.name}' created with BOTH callbacks.")

    # --- Create Runner, Using SAME Stateful Session Service ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< Use the service from Step 4/5
        )
        print(f"✅ Runner created for tool guardrail agent '{runner_root_tool_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4/5 is missing.")

else:
    print("❌ Cannot create root agent with tool guardrail. Prerequisites missing.")

```

* * *

**3\. Interact to Test the Tool Guardrail**

Let's test the interaction flow, again using the same stateful session ( `SESSION_ID_STATEFUL`) from the previous steps.

1. Request weather for "New York": Passes both callbacks, tool executes (using Fahrenheit preference from state).
2. Request weather for "Paris": Passes `before_model_callback`. LLM decides to call `get_weather_stateful(city='Paris')`. `before_tool_callback` intercepts, blocks the tool, and returns the error dictionary. Agent relays this error.
3. Request weather for "London": Passes both callbacks, tool executes normally.

```md-code__content
# @title 3. Interact to Test the Tool Argument Guardrail
import asyncio # Ensure asyncio is imported

# Ensure the runner for the tool guardrail agent is available
if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
    # Define the main async function for the tool guardrail test conversation.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_tool_guardrail_test():
        print("\n--- Testing Tool Argument Guardrail ('Paris' blocked) ---")

        # Use the runner for the agent with both callbacks and the existing stateful session
        # Define a helper lambda for cleaner interaction calls
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_tool_guardrail,
                                                         USER_ID_STATEFUL, # Use existing user ID
                                                         SESSION_ID_STATEFUL # Use existing session ID
                                                        )
        # 1. Allowed city (Should pass both callbacks, use Fahrenheit state)
        print("--- Turn 1: Requesting weather in New York (expect allowed) ---")
        await interaction_func("What's the weather in New York?")

        # 2. Blocked city (Should pass model callback, but be blocked by tool callback)
        print("\n--- Turn 2: Requesting weather in Paris (expect blocked by tool guardrail) ---")
        await interaction_func("How about Paris?") # Tool callback should intercept this

        # 3. Another allowed city (Should work normally again)
        print("\n--- Turn 3: Requesting weather in London (expect allowed) ---")
        await interaction_func("Tell me the weather in London.")

    # --- Execute the `run_tool_guardrail_test` async function ---
    # Choose ONE of the methods below based on your environment.

    # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
    # If your environment supports top-level await (like Colab/Jupyter notebooks),
    # it means an event loop is already running, so you can directly await the function.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_tool_guardrail_test()

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.
    # To use this method:
    # 1. Comment out the `await run_tool_guardrail_test()` line above.
    # 2. Uncomment the following block:
    """
    import asyncio
    if __name__ == "__main__": # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_tool_guardrail_test())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- Inspect final session state after the conversation ---
    # This block runs after either execution method completes.
    # Optional: Check state for the tool block trigger flag
    print("\n--- Inspecting Final Session State (After Tool Guardrail Test) ---")
    # Use the session service instance associated with this stateful session
    final_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id= SESSION_ID_STATEFUL)
    if final_session:
        # Use .get() for safer access
        print(f"Tool Guardrail Triggered Flag: {final_session.state.get('guardrail_tool_block_triggered', 'Not Set (or False)')}")
        print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}") # Should be London weather if successful
        print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}") # Should be Fahrenheit
        # print(f"Full State Dict: {final_session.state.as_dict()}") # For detailed view
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping tool guardrail test. Runner ('runner_root_tool_guardrail') is not available.")

```

* * *

Analyze the output:

1. **New York:** The `before_model_callback` allows the request. The LLM requests `get_weather_stateful`. The `before_tool_callback` runs, inspects the args ( `{'city': 'New York'}`), sees it's not "Paris", prints "Allowing tool..." and returns `None`. The actual `get_weather_stateful` function executes, reads "Fahrenheit" from state, and returns the weather report. The agent relays this, and it gets saved via `output_key`.
2. **Paris:** The `before_model_callback` allows the request. The LLM requests `get_weather_stateful(city='Paris')`. The `before_tool_callback` runs, inspects the args, detects "Paris", prints "Blocking tool execution!", sets the state flag, and returns the error dictionary `{'status': 'error', 'error_message': 'Policy restriction...'}`. The actual `get_weather_stateful` function is **never executed**. The agent receives the error dictionary _as if it were the tool's output_ and formulates a response based on that error message.
3. **London:** Behaves like New York, passing both callbacks and executing the tool successfully. The new London weather report overwrites the `last_weather_report` in the state.

You've now added a crucial safety layer controlling not just _what_ reaches the LLM, but also _how_ the agent's tools can be used based on the specific arguments generated by the LLM. Callbacks like `before_model_callback` and `before_tool_callback` are essential for building robust, safe, and policy-compliant agent applications.

* * *

## Conclusion: Your Agent Team is Ready! [¶](https://google.github.io/adk-docs/tutorials/agent-team/\#conclusion-your-agent-team-is-ready "Permanent link")

Congratulations! You've successfully journeyed from building a single, basic weather agent to constructing a sophisticated, multi-agent team using the Agent Development Kit (ADK).

**Let's recap what you've accomplished:**

- You started with a **fundamental agent** equipped with a single tool ( `get_weather`).
- You explored ADK's **multi-model flexibility** using LiteLLM, running the same core logic with different LLMs like Gemini, GPT-4o, and Claude.
- You embraced **modularity** by creating specialized sub-agents ( `greeting_agent`, `farewell_agent`) and enabling **automatic delegation** from a root agent.
- You gave your agents **memory** using **Session State**, allowing them to remember user preferences ( `temperature_unit`) and past interactions ( `output_key`).
- You implemented crucial **safety guardrails** using both `before_model_callback` (blocking specific input keywords) and `before_tool_callback` (blocking tool execution based on arguments like the city "Paris").

Through building this progressive Weather Bot team, you've gained hands-on experience with core ADK concepts essential for developing complex, intelligent applications.

**Key Takeaways:**

- **Agents & Tools:** The fundamental building blocks for defining capabilities and reasoning. Clear instructions and docstrings are paramount.
- **Runners & Session Services:** The engine and memory management system that orchestrate agent execution and maintain conversational context.
- **Delegation:** Designing multi-agent teams allows for specialization, modularity, and better management of complex tasks. Agent `description` is key for auto-flow.
- **Session State ( `ToolContext`, `output_key`):** Essential for creating context-aware, personalized, and multi-turn conversational agents.
- **Callbacks ( `before_model`, `before_tool`):** Powerful hooks for implementing safety, validation, policy enforcement, and dynamic modifications _before_ critical operations (LLM calls or tool execution).
- **Flexibility ( `LiteLlm`):** ADK empowers you to choose the best LLM for the job, balancing performance, cost, and features.

**Where to Go Next?**

Your Weather Bot team is a great starting point. Here are some ideas to further explore ADK and enhance your application:

1. **Real Weather API:** Replace the `mock_weather_db` in your `get_weather` tool with a call to a real weather API (like OpenWeatherMap, WeatherAPI).
2. **More Complex State:** Store more user preferences (e.g., preferred location, notification settings) or conversation summaries in the session state.
3. **Refine Delegation:** Experiment with different root agent instructions or sub-agent descriptions to fine-tune the delegation logic. Could you add a "forecast" agent?
4. **Advanced Callbacks:**
   - Use `after_model_callback` to potentially reformat or sanitize the LLM's response _after_ it's generated.
   - Use `after_tool_callback` to process or log the results returned by a tool.
   - Implement `before_agent_callback` or `after_agent_callback` for agent-level entry/exit logic.
5. **Error Handling:** Improve how the agent handles tool errors or unexpected API responses. Maybe add retry logic within a tool.
6. **Persistent Session Storage:** Explore alternatives to `InMemorySessionService` for storing session state persistently (e.g., using databases like Firestore or Cloud SQL – requires custom implementation or future ADK integrations).
7. **Streaming UI:** Integrate your agent team with a web framework (like FastAPI, as shown in the ADK Streaming Quickstart) to create a real-time chat interface.

The Agent Development Kit provides a robust foundation for building sophisticated LLM-powered applications. By mastering the concepts covered in this tutorial – tools, state, delegation, and callbacks – you are well-equipped to tackle increasingly complex agentic systems.

Happy building!

Back to top

---


## File: docs/agents/google-adk/examples/firecrawl/docs/quickstart-streaming.md

[Skip to content](https://google.github.io/adk-docs/get-started/quickstart-streaming/#adk-streaming-quickstart)

# ADK Streaming Quickstart [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#adk-streaming-quickstart "Permanent link")

With this quickstart, you'll learn to create a simple agent and use ADK Streaming to enable voice and video communication with it that is low-latency and bidirectional. We will install ADK, set up a basic "Google Search" agent, try running the agent with Streaming with `adk web` tool, and then explain how to build a simple asynchronous web app by yourself using ADK Streaming and [FastAPI](https://fastapi.tiangolo.com/).

**Note:** This guide assumes you have experience using a terminal in Windows, Mac, and Linux environments.

## Supported models for voice/video streaming [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#supported-models "Permanent link")

In order to use voice/video streaming in ADK, you will need to use Gemini models that support the Live API. You can find the **model ID(s)** that supports the Gemini Live API in the documentation:

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1\. Setup Environment & Install ADK [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#1.-setup-installation "Permanent link")

Create & Activate Virtual Environment (Recommended):

```md-code__content
# Create
python -m venv .venv
# Activate (each new terminal)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1

```

Install ADK:

```md-code__content
pip install google-adk

```

## 2\. Project Structure [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#2.-project-structure "Permanent link")

Create the following folder structure with empty files:

```md-code__content
adk-streaming/  # Project folder
└── app/ # the web app folder
    ├── .env # Gemini API key
    └── google_search_agent/ # Agent folder
        ├── __init__.py # Python package
        └── agent.py # Agent definition

```

### agent.py [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#agentpy "Permanent link")

Copy-paste the following code block to the [`agent.py`](http://agent.py/).

For `model`, please double check the model ID as described earlier in the [Models section](https://google.github.io/adk-docs/get-started/quickstart-streaming/#supported-models).

```md-code__content
from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

root_agent = Agent(
   # A unique name for the agent.
   name="basic_search_agent",
   # The Large Language Model (LLM) that agent will use.
   model="gemini-2.0-flash-exp", # Google AI Studio
   #model="gemini-2.0-flash-live-preview-04-09" # Vertex AI Studio
   # A short description of the agent's purpose.
   description="Agent to answer questions using Google Search.",
   # Instructions to set the agent's behavior.
   instruction="You are an expert researcher. You always stick to the facts.",
   # Add google_search tool to perform grounding with Google search.
   tools=[google_search]
)

```

**Note:** To enable both text and audio/video input, the model must support the generateContent (for text) and bidiGenerateContent methods. Verify these capabilities by referring to the [List Models Documentation](https://ai.google.dev/api/models#method:-models.list). This quickstart utilizes the gemini-2.0-flash-exp model for demonstration purposes.

`agent.py` is where all your agent(s)' logic will be stored, and you must have a `root_agent` defined.

Notice how easily you integrated [grounding with Google Search](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search) capabilities. The `Agent` class and the `google_search` tool handle the complex interactions with the LLM and grounding with the search API, allowing you to focus on the agent's _purpose_ and _behavior_.

![intro_components.png](https://google.github.io/adk-docs/assets/quickstart-streaming-tool.png)

Copy-paste the following code block to `__init__.py` and `main.py` files.

\_\_init\_\_.py

```md-code__content
from . import agent

```

## 3\. Set up the platform [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#3.-set-up-the-platform "Permanent link")

To run the agent, choose a platform from either Google AI Studio or Google Cloud Vertex AI:

[Gemini - Google AI Studio](https://google.github.io/adk-docs/get-started/quickstart-streaming/#gemini---google-ai-studio)[Gemini - Google Cloud Vertex AI](https://google.github.io/adk-docs/get-started/quickstart-streaming/#gemini---google-cloud-vertex-ai)

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Open the **`.env`** file located inside ( `app/`) and copy-paste the following code.

.env

```md-code__content
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE

```

3. Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your actual `API KEY`.


1. You need an existing
    [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) account and a
    project.   - Set up a
         [Google Cloud project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
   - Set up the
      [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
   - Authenticate to Google Cloud, from the terminal by running
      `gcloud auth login`.
   - [Enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
2. Open the **`.env`** file located inside ( `app/`). Copy-paste
    the following code and update the project ID and location.

.env

```md-code__content
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1

```


## 4\. Try the agent with `adk web` [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#4.-try-it-adk-web "Permanent link")

Now it's ready to try the agent. Run the following command to launch the **dev UI**. First, make sure to set the current directory to `app`:

```md-code__content
cd app

```

Also, set `SSL_CERT_FILE` variable with the following command. This is required for the voice and video tests later.

```md-code__content
export SSL_CERT_FILE=$(python -m certifi)

```

Then, run the dev UI:

```md-code__content
adk web

```

Open the URL provided (usually `http://localhost:8000` or
`http://127.0.0.1:8000`) **directly in your browser**. This connection stays
entirely on your local machine. Select `google_search_agent`.

### Try with text [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#try-with-text "Permanent link")

Try the following prompts by typing them in the UI.

- What is the weather in New York?
- What is the time in New York?
- What is the weather in Paris?
- What is the time in Paris?

The agent will use the google\_search tool to get the latest information to answer those questions.

### Try with voice and video [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#try-with-voice-and-video "Permanent link")

To try with voice, reload the web browser, click the microphone button to enable the voice input, and ask the same question in voice. You will hear the answer in voice in real-time.

To try with video, reload the web browser, click the camera button to enable the video input, and ask questions like "What do you see?". The agent will answer what they see in the video input.

### Stop the tool [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#stop-the-tool "Permanent link")

Stop `adk web` by pressing `Ctrl-C` on the console.

### Note on ADK Streaming [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#note-on-adk-streaming "Permanent link")

The following features will be supported in the future versions of the ADK Streaming: Callback, LongRunningTool, ExampleTool, and Shell agent (e.g. SequentialAgent).

## 5\. Building a Custom Streaming App (Optional) [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#5.-build-custom-app "Permanent link")

In the previous section, we have checked that our basic search agent works with the ADK Streaming using `adk web` tool. In the this section, we will learn how to build your own web application capable of the streaming communication using [FastAPI](https://fastapi.tiangolo.com/).

Add `static` directory under `app`, and add `main.py` and `index.html` as empty files, as in the following structure:

```md-code__content
adk-streaming/  # Project folder
└── app/ # the web app folder
    ├── main.py # FastAPI web app
    └── static/ # Static content folder
        └── index.html # The web client page

```

By adding the directories and files above, the entire directory structure and files will look like:

```md-code__content
adk-streaming/  # Project folder
└── app/ # the web app folder
    ├── main.py # FastAPI web app
    ├── static/ # Static content folder
    |   └── index.html # The web client page
    ├── .env # Gemini API key
    └── google_search_agent/ # Agent folder
        ├── __init__.py # Python package
        └── agent.py # Agent definition

```

**main.py**

Copy-paste the following code block to the main.py file.

```md-code__content
import os
import json
import asyncio

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
)

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google_search_agent.agent import root_agent

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "ADK Streaming example"
session_service = InMemorySessionService()

def start_agent_session(session_id: str):
    """Starts an agent session"""

    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality = TEXT
    run_config = RunConfig(response_modalities=["TEXT"])

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            # turn_complete
            if event.turn_complete:
                await websocket.send_text(json.dumps({"turn_complete": True}))
                print("[TURN COMPLETE]")

            if event.interrupted:
                await websocket.send_text(json.dumps({"interrupted": True}))
                print("[INTERRUPTED]")

            # Read the Content and its first Part
            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part or not event.partial:
                continue

            # Get the text
            text = event.content and event.content.parts and event.content.parts[0].text
            if not text:
                continue

            # Send the text to the client
            await websocket.send_text(json.dumps({"message": text}))
            print(f"[AGENT TO CLIENT]: {text}")
            await asyncio.sleep(0)

async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    while True:
        text = await websocket.receive_text()
        content = Content(role="user", parts=[Part.from_text(text=text)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {text}")
        await asyncio.sleep(0)

#
# FastAPI web app
#

app = FastAPI()

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    """Client websocket endpoint"""

    # Wait for client connection
    await websocket.accept()
    print(f"Client #{session_id} connected")

    # Start agent session
    session_id = str(session_id)
    live_events, live_request_queue = start_agent_session(session_id)

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)

    # Disconnected
    print(f"Client #{session_id} disconnected")

```

This code creates a real-time chat application using ADK and FastAPI. It sets up a WebSocket endpoint where clients can connect and interact with a Google Search Agent.

Key functionalities:

- Loads the Gemini API key.
- Uses ADK to manage agent sessions and run the \`google\_search\_agent\`.
- \`start\_agent\_session\` initializes an agent session with a live request queue for real-time communication.
- \`agent\_to\_client\_messaging\` asynchronously streams the agent's text responses and status updates (turn complete, interrupted) to the connected WebSocket client.
- \`client\_to\_agent\_messaging\` asynchronously receives text messages from the WebSocket client and sends them as user input to the agent.
- FastAPI serves a static frontend and handles WebSocket connections at \`/ws/{session\_id}\`.
- When a client connects, it starts an agent session and creates concurrent tasks for bidirectional communication between the client and the agent via WebSockets.

Copy-paste the following code block to the `index.html` file.

index.html

```md-code__content
<!doctype html>
<html>
  <head>
    <title>ADK Streaming Test</title>
  </head>

  <body>
    <h1>ADK Streaming Test</h1>
    <div
      id="messages"
      style="height: 300px; overflow-y: auto; border: 1px solid black"></div>
    <br />

    <form id="messageForm">
      <label for="message">Message:</label>
      <input type="text" id="message" name="message" />
      <button type="submit" id="sendButton" disabled>Send</button>
    </form>
  </body>

  <script>
    // Connect the server with a WebSocket connection
    const sessionId = Math.random().toString().substring(10);
    const ws_url = "ws://" + window.location.host + "/ws/" + sessionId;
    let ws = new WebSocket(ws_url);

    // Get DOM elements
    const messageForm = document.getElementById("messageForm");
    const messageInput = document.getElementById("message");
    const messagesDiv = document.getElementById("messages");
    let currentMessageId = null;

    // WebSocket handlers
    function addWebSocketHandlers(ws) {
      ws.onopen = function () {
        console.log("WebSocket connection opened.");
        document.getElementById("sendButton").disabled = false;
        document.getElementById("messages").textContent = "Connection opened";
        addSubmitHandler(this);
      };

      ws.onmessage = function (event) {
        // Parse the incoming message
        const packet = JSON.parse(event.data);
        console.log(packet);

        // Check if the turn is complete
        // if turn complete, add new message
        if (packet.turn_complete && packet.turn_complete == true) {
          currentMessageId = null;
          return;
        }

        // add a new message for a new turn
        if (currentMessageId == null) {
          currentMessageId = Math.random().toString(36).substring(7);
          const message = document.createElement("p");
          message.id = currentMessageId;
          // Append the message element to the messagesDiv
          messagesDiv.appendChild(message);
        }

        // Add message text to the existing message element
        const message = document.getElementById(currentMessageId);
        message.textContent += packet.message;

        // Scroll down to the bottom of the messagesDiv
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      };

      // When the connection is closed, try reconnecting
      ws.onclose = function () {
        console.log("WebSocket connection closed.");
        document.getElementById("sendButton").disabled = true;
        document.getElementById("messages").textContent = "Connection closed";
        setTimeout(function () {
          console.log("Reconnecting...");
          ws = new WebSocket(ws_url);
          addWebSocketHandlers(ws);
        }, 5000);
      };

      ws.onerror = function (e) {
        console.log("WebSocket error: ", e);
      };
    }
    addWebSocketHandlers(ws);

    // Add submit handler to the form
    function addSubmitHandler(ws) {
      messageForm.onsubmit = function (e) {
        e.preventDefault();
        const message = messageInput.value;
        if (message) {
          const p = document.createElement("p");
          p.textContent = "> " + message;
          messagesDiv.appendChild(p);
          ws.send(message);
          messageInput.value = "";
        }
        return false;
      };
    }
  </script>
</html>

```

This HTML file sets up a basic webpage with:

- A form (\`messageForm\`) with an input field for typing messages and a "Send" button.
- JavaScript that:
- Connects to a WebSocket server at \`wss://\[current host\]/ws/\[random session ID\]\`.
- Enables the "Send" button upon successful connection.
- Appends received messages from the WebSocket to the \`messages\` div, handling streaming responses and turn completion.
- Sends the text entered in the input field to the WebSocket server when the form is submitted.
- Attempts to reconnect if the WebSocket connection closes.

## 6\. Interact with Your Streaming app [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#4.-interact-with-your-streaming-app "Permanent link")

1\. **Navigate to the Correct Directory:**

To run your agent effectively, you need to be in the **app folder ( `adk-streaming/app`)**

2\. **Start the Fast API**: Run the following command to start CLI interface with

```md-code__content
uvicorn main:app --reload

```

3\. **Access the UI:** Once the UI server starts, the terminal will display a local URL (e.g., [http://localhost:8000](http://localhost:8501/)). Click this link to open the UI in your browser.

Now you should see the UI like this:

![ADK Streaming Test](https://google.github.io/adk-docs/assets/adk-streaming.png)

Try asking a question `What is Gemini?`. The agent will use Google Search to respond to your queries. You would notice that the UI shows the agent's response as streaming text. You can also send messages to the agent at any time, even while the agent is still responding. This demonstrates the bidirectional communication capability of ADK Streaming.

Benefits over conventional synchronous web apps:

- Real-time two-way communication: Seamless interaction.
- More responsive and engaging: No need to wait for full responses or constant refreshing. Feels like a live conversation.
- Can be extended to multimodal apps with audio, image and video streaming support.

Congratulations! You've successfully created and interacted with your first Streaming agent using ADK!

## Next steps [¶](https://google.github.io/adk-docs/get-started/quickstart-streaming/\#next-steps "Permanent link")

- **Add audio/image modality:** with the Streaming, you can also have real-time communication with the agent using audio and image. We will add more samples for the multimodal support in the future. Stay tuned!

Back to top
---


## File: docs/agents/google-adk/examples/firecrawl/docs/tool-usage-examples.md

```python
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

app = FirecrawlApp()
```

## Web extraction

```python
url = "https://github.com/trending"

# It is possible to pass a list of URLs to the extract method
result = app.extract([url], prompt="Extract the top 10 trending repositories")
```

```python
result.data
```

```
{'trending_repositories': [{'name': 'Deep-Live-Cam',
   'owner': 'hacksider',
   'stars': 55338,
   'language': 'Python',
   'description': 'real time face swap and one-click video deepfake with only a single image'},
  {'name': 'ai-engineering-hub',
   'owner': 'patchy631',
   'stars': 8753,
   'language': 'Jupyter Notebook',
   'description': 'In-depth tutorials on LLMs, RAGs and real-world AI agent applications.'},
  {'name': 'Qwen-Agent',
   'owner': 'QwenLM',
   'stars': 7444,
   'language': 'Python',
   'description': 'Agent framework and applications built upon Qwen>=2.0, featuring Function Calling, Code Interpreter, RAG, and Chrome extension.'},
  {'name': 'Qwen3',
   'owner': 'QwenLM',
   'stars': 19682,
   'language': 'Shell',
   'description': 'Qwen3 is the large language model series developed by Qwen team, Alibaba Cloud.'},
  {'name': 'hyperswitch',
   'owner': 'juspay',
   'stars': 17069,
   'language': 'Rust',
   'description': 'An open source payments switch written in Rust to make payments fast, reliable and affordable'},
  {'name': 'daytona',
   'owner': 'daytonaio',
   'stars': 17395,
   'language': 'TypeScript',
   'description': 'Daytona is a Secure and Elastic Infrastructure for Running AI-Generated Code'},
  {'name': 'vllm',
   'owner': 'vllm-project',
   'stars': 46340,
   'language': 'Python',
   'description': 'A high-throughput and memory-efficient inference and serving engine for LLMs'},
  {'name': 'Agent-S',
   'owner': 'simular-ai',
   'stars': 3619,
   'language': 'Python',
   'description': 'Agent S: an open agentic framework that uses computers like a human'},
  {'name': 'generative-ai-for-beginners',
   'owner': 'microsoft',
   'stars': 81829,
   'language': 'Jupyter Notebook',
   'description': '21 Lessons, Get Started Building with Generative AI 🔗 https://microsoft.github.io/generative-ai-for-beginners/'},
  {'name': 'ladybird',
   'owner': 'LadybirdBrowser',
   'stars': 38045,
   'language': 'C++',
   'description': 'Truly independent web browser'}]}
```

## Turning any webpage to either clean markdown or HTML or find the links

```python
result = app.scrape_url(url, formats=["markdown", "html", "links"])

result
```

```python
result.markdown[:100]
```

```
'[Skip to content](https://github.com/trending#start-of-content)\n\nYou signed in with another tab or w'
```

```python
result.html[:100]
```

```
'<!DOCTYPE html><html lang="en" data-color-mode="auto" data-light-theme="light" data-dark-theme="dark'
```

```python
result.links[:10]
```

```
['https://github.com/trending#start-of-content',
 'https://github.com/trending',
 'https://github.com/trending?spoken_language_code=ab',
 'https://github.com/trending?spoken_language_code=aa',
 'https://github.com/trending?spoken_language_code=af',
 'https://github.com/trending?spoken_language_code=ak',
 'https://github.com/trending?spoken_language_code=sq',
 'https://github.com/trending?spoken_language_code=am',
 'https://github.com/trending?spoken_language_code=ar',
 'https://github.com/trending?spoken_language_code=an']
```

```python
result.metadata
```

```
{'og:title': 'Build software better, together',
 'ogUrl': 'https://github.com',
 'request-id': '7217:1355EC:27020D:357687:68133B54',
 'release': 'c7cada2ceb24d5ad3fc39b2db01e5afedeed299c',
 'color-scheme': 'light dark',
 'og:description': 'GitHub is where people build software. More than 150 million people use GitHub to discover, fork, and contribute to over 420 million projects.',
 'ogImage': 'https://github.githubassets.com/assets/github-logo-55c5b9a1fe52.png',
 'current-catalog-service-hash': '047de2aa31687506697d59851c60a89162ffacfdbae2bc21df7cf2e253362bdb',
 'theme-color': '#1e2327',
 'title': 'Trending  repositories on GitHub today · GitHub',
 'fb:app_id': '1401488693436528',
 'twitter:card': 'summary_large_image',
 'twitter:title': 'GitHub',
 'twitter:creator': 'github',
 'turbo-cache-control': 'no-preview',
 'twitter:description': 'GitHub is where people build software. More than 150 million people use GitHub to discover, fork, and contribute to over 420 million projects.',
 'visitor-payload': 'eyJyZWZlcnJlciI6IiIsInJlcXVlc3RfaWQiOiI3MjE3OjEzNTVFQzoyNzAyMEQ6MzU3Njg3OjY4MTMzQjU0IiwidmlzaXRvcl9pZCI6IjE2NDY0NTcwODMwOTk1NjA3ODkiLCJyZWdpb25fZWRnZSI6ImlhZCIsInJlZ2lvbl9yZW5kZXIiOiJpYWQifQ==',
 'og:image': ['https://github.githubassets.com/assets/github-logo-55c5b9a1fe52.png',
  'https://github.githubassets.com/assets/github-mark-57519b92ca4e.png',
  'https://github.githubassets.com/assets/github-octocat-13c86b8b336d.png'],
 'og:image:width': ['1200', '1200', '1200'],
 'ogSiteName': 'GitHub',
 'route-action': 'index',
 'twitter:site:id': '13334762',
 'twitter:image': 'https://github.githubassets.com/assets/github-logo-55c5b9a1fe52.png',
 'og:url': 'https://github.com',
 'viewport': 'width=device-width',
 'visitor-hmac': '4203e43775ddf6423385b866d367d721235d751898ce686b210ec4cf206ca696',
 'expected-hostname': 'github.com',
 'turbo-body-classes': 'logged-out env-production page-responsive',
 'route-controller': 'trending',
 'github-keyboard-shortcuts': 'copilot',
 'language': 'en',
 'og:image:type': ['image/png', 'image/png', 'image/png'],
 'fetch-nonce': '67a22d1e-dde5-88ed-79d1-5c5802432b71',
 'google-site-verification': 'Apib7-x98H0j5cPqHWwSMm6dNU4GmODRoqxLiDzdx9I',
 'og:image:height': ['1200', '620', '620'],
 'twitter:site': 'github',
 'user-login': '',
 'og:site_name': 'GitHub',
 'twitter:image:height': '1200',
 'ogTitle': 'Build software better, together',
 'favicon': 'https://github.githubassets.com/favicons/favicon.svg',
 'browser-stats-url': 'https://api.github.com/_private/browser/stats',
 'octolytics-url': 'https://collector.github.com/github/collect',
 'browser-errors-url': 'https://api.github.com/_private/browser/errors',
 'ogDescription': 'GitHub is where people build software. More than 150 million people use GitHub to discover, fork, and contribute to over 420 million projects.',
 'apple-itunes-app': 'app-id=1477376905, app-argument=https://github.com/trending',
 'description': 'GitHub is where people build software. More than 150 million people use GitHub to discover, fork, and contribute to over 420 million projects.',
 'twitter:creator:id': '13334762',
 'twitter:image:width': '1200',
 'html-safe-nonce': 'a2c7d7386cdf05482f18b02218df8cdf1a88525dc1e7fa9228c157219c6e50e3',
 'hostname': 'github.com',
 'route-pattern': '/trending(/:language)(.:format)',
 'scrapeId': '3746f88c-5998-4c20-98ca-e91b85a67f74',
 'sourceURL': 'https://github.com/trending',
 'url': 'https://github.com/trending',
 'statusCode': 200}
```

## Performing web search

### Pure search

```python
result = app.search("Best open-source frameworks to build agents", limit=10)

result
```

```
SearchResponse(success=True, data=[{'url': 'https://medium.com/data-science-collective/agentic-ai-comparing-new-open-source-frameworks-21ec676732df', 'title': 'Agentic AI: Comparing New Open-Source Frameworks - Medium', 'description': "The ones we've all heard about are CrewAI and AutoGen. CrewAI is a very high-abstraction framework that lets you build agent systems quickly by ..."}, {'url': 'https://botpress.com/blog/ai-agent-frameworks', 'title': 'Top 5 Free AI Agent Frameworks - Botpress', 'description': 'Top 5 Free AI Agent Frameworks · 1. Botpress · 2. RASA · 3. LangGraph · 4. CrewAI · 5. LlamaIndex.'}, {'url': 'https://www.reddit.com/r/LLMDevs/comments/1io0gnz/top_5_open_source_frameworks_for_building_ai/', 'title': 'Top 5 Open Source Frameworks for building AI Agents - Reddit', 'description': 'We created a list of Open Source AI Agent Frameworks mostly used by people and built an AI Agent using each one of them.'}, {'url': 'https://getstream.io/blog/multiagent-ai-frameworks/', 'title': 'Best 5 Frameworks To Build Multi-Agent AI Applications - GetStream.io', 'description': 'Autogen is an open-source framework for building agentic systems. You can use this framework to construct multi-agent collaborations and LLM ...'}, {'url': 'https://langfuse.com/blog/2025-03-19-ai-agent-comparison', 'title': 'Comparing Open-Source AI Agent Frameworks - Langfuse Blog', 'description': 'Get an overview of the leading open-source AI agent frameworks—LangGraph, OpenAI Agents SDK, Smolagents, CrewAI, AutoGen, Semantic Kernel, ...'}, {'url': 'https://www.analyticsvidhya.com/blog/2024/07/ai-agent-frameworks/', 'title': 'Top 7 Frameworks for Building AI Agents in 2025 - Analytics Vidhya', 'description': 'Explore AI Agent Frameworks like Langchain, CrewAI, and Microsoft Semantic Kernel. Understand their key importance in AI development.'}, {'url': 'https://medium.com/data-science-collective/the-open-source-stack-for-ai-agents-8ab900e33676', 'title': 'The Open-Source Stack for AI Agents - Medium', 'description': '1. Frameworks for Building and Orchestrating Agents · CrewAI — Orchestrates multiple agents working together. · Agno — Focuses on memory, tool use ...'}, {'url': 'https://blog.dataiku.com/open-source-frameworks-for-llm-powered-agents', 'title': 'A Tour of Popular Open Source Frameworks for LLM-Powered Agents', 'description': 'The purpose of this blog post is to present some of the most popular open source Python frameworks used to implement LLM-powered agents.'}, {'url': 'https://budibase.com/blog/ai-agents/open-source-ai-agent-platforms/', 'title': '6 Open-Source AI Agent Platforms - Budibase', 'description': '1. LangChain. First up, we have LangChain, perhaps the best-known and most widely adopted framework for building agentic workflows with LLMs.'}, {'url': 'https://www.ibm.com/think/insights/top-ai-agent-frameworks', 'title': 'AI Agent Frameworks: Choosing the Right Foundation for Your ... - IBM', 'description': 'LlamaIndex is an open-source data orchestration framework for building generative AI (gen AI) and agentic AI solutions. It offers prepackaged ...'}], warning=None, error=None)
```

```python
result.data
```

```
[{'url': 'https://medium.com/data-science-collective/agentic-ai-comparing-new-open-source-frameworks-21ec676732df',
  'title': 'Agentic AI: Comparing New Open-Source Frameworks - Medium',
  'description': "The ones we've all heard about are CrewAI and AutoGen. CrewAI is a very high-abstraction framework that lets you build agent systems quickly by ..."},
 {'url': 'https://botpress.com/blog/ai-agent-frameworks',
  'title': 'Top 5 Free AI Agent Frameworks - Botpress',
  'description': 'Top 5 Free AI Agent Frameworks · 1. Botpress · 2. RASA · 3. LangGraph · 4. CrewAI · 5. LlamaIndex.'},
 {'url': 'https://www.reddit.com/r/LLMDevs/comments/1io0gnz/top_5_open_source_frameworks_for_building_ai/',
  'title': 'Top 5 Open Source Frameworks for building AI Agents - Reddit',
  'description': 'We created a list of Open Source AI Agent Frameworks mostly used by people and built an AI Agent using each one of them.'},
 {'url': 'https://getstream.io/blog/multiagent-ai-frameworks/',
  'title': 'Best 5 Frameworks To Build Multi-Agent AI Applications - GetStream.io',
  'description': 'Autogen is an open-source framework for building agentic systems. You can use this framework to construct multi-agent collaborations and LLM ...'},
 {'url': 'https://langfuse.com/blog/2025-03-19-ai-agent-comparison',
  'title': 'Comparing Open-Source AI Agent Frameworks - Langfuse Blog',
  'description': 'Get an overview of the leading open-source AI agent frameworks—LangGraph, OpenAI Agents SDK, Smolagents, CrewAI, AutoGen, Semantic Kernel, ...'},
 {'url': 'https://www.analyticsvidhya.com/blog/2024/07/ai-agent-frameworks/',
  'title': 'Top 7 Frameworks for Building AI Agents in 2025 - Analytics Vidhya',
  'description': 'Explore AI Agent Frameworks like Langchain, CrewAI, and Microsoft Semantic Kernel. Understand their key importance in AI development.'},
 {'url': 'https://medium.com/data-science-collective/the-open-source-stack-for-ai-agents-8ab900e33676',
  'title': 'The Open-Source Stack for AI Agents - Medium',
  'description': '1. Frameworks for Building and Orchestrating Agents · CrewAI — Orchestrates multiple agents working together. · Agno — Focuses on memory, tool use ...'},
 {'url': 'https://blog.dataiku.com/open-source-frameworks-for-llm-powered-agents',
  'title': 'A Tour of Popular Open Source Frameworks for LLM-Powered Agents',
  'description': 'The purpose of this blog post is to present some of the most popular open source Python frameworks used to implement LLM-powered agents.'},
 {'url': 'https://budibase.com/blog/ai-agents/open-source-ai-agent-platforms/',
  'title': '6 Open-Source AI Agent Platforms - Budibase',
  'description': '1. LangChain. First up, we have LangChain, perhaps the best-known and most widely adopted framework for building agentic workflows with LLMs.'},
 {'url': 'https://www.ibm.com/think/insights/top-ai-agent-frameworks',
  'title': 'AI Agent Frameworks: Choosing the Right Foundation for Your ... - IBM',
  'description': 'LlamaIndex is an open-source data orchestration framework for building generative AI (gen AI) and agentic AI solutions. It offers prepackaged ...'}]
```

## Doing deep research

```python
result = app.deep_research(
    "Best open-source frameworks to build agents",
    max_depth=5,
    time_limit=180,
    max_urls=20
)
```

```python
print(result['data']['finalAnalysis'][:1000])
```

```
# Comprehensive Analysis of Open-Source Frameworks for Building AI Agents in 2025

This report provides an in-depth comparative analysis of the leading open-source frameworks used to build AI agents in 2025. It covers the technical features, design philosophies, and real-world deployment outcomes, drawing on multiple sources and research data from platforms including Medium, Botpress, GetStream, Firecrawl, and Shakudo.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Research Methodology](#research-methodology)
3. [Overview of Agentic AI](#overview-of-agentic-ai)
4. [Framework-by-Framework Analysis](#framework-analysis)
    - [LangGraph](#langgraph)
    - [Agno (Phidata)](#agno)
    - [SmolAgents & Mastra](#smolagents--mastra)
    - [Pydantic AI](#pydantic-ai)
    - [Atomic Agents](#atomic-agents)
    - [CrewAI](#crewai)
    - [AutoGen](#autogen)
5. [Comparative Summary Table](#comparative-table)
6. [Best Practices for Enterprise Agent Implementation](#best-practices)
7
```

```python
result['data']['sources']
```

```[{'url': 'https://medium.com/data-science-collective/agentic-ai-comparing-new-open-source-frameworks-21ec676732df',
  'title': 'Agentic AI: Comparing New Open-Source Frameworks - Medium',
  'description': "The ones we've all heard about are CrewAI and AutoGen. CrewAI is a very high-abstraction framework that lets you build agent systems quickly by ...",
  'icon': 'https://miro.medium.com/v2/5d8de952517e8160e40ef9841c781cdc14a5db313057fa3c3de41c6f5b494b19'},
 {'url': 'https://botpress.com/blog/ai-agent-frameworks',
  'title': 'Top 5 Free AI Agent Frameworks - Botpress',
  'description': 'Top 5 Free AI Agent Frameworks · 1. Botpress · 2. RASA · 3. LangGraph · 4. CrewAI · 5. LlamaIndex.',
  'icon': 'https://cdn.prod.website-files.com/635c4eeb78332f7971255095/680fcae3aa877b0851eac0ce_Frame%203%20(1).png'},
 {'url': 'https://www.reddit.com/r/LLMDevs/comments/1io0gnz/top_5_open_source_frameworks_for_building_ai/',
  'title': 'Top 5 Open Source Frameworks for building AI Agents - Reddit',
  'description': 'We created a list of Open Source AI Agent Frameworks mostly used by people and built an AI Agent using each one of them.',
  'icon': ''},
 {'url': 'https://getstream.io/blog/multiagent-ai-frameworks/',
  'title': 'Best 5 Frameworks To Build Multi-Agent AI Applications - GetStream.io',
  'description': 'Autogen is an open-source framework for building agentic systems. You can use this framework to construct multi-agent collaborations and LLM ...',
  'icon': 'https://getstream.io/icon.png'},
 {'url': 'https://www.shakudo.io/blog/top-9-ai-agent-frameworks',
  'title': 'Top 9 AI Agent Frameworks as of April 2025 - Shakudo',
  'description': 'Top 9 AI Agent Frameworks as of April 2025 · 1. LangChain · 2. AutoGen · 3. Semantic Kernel · 4. Atomic Agents · 5. CrewAI · 6. RASA · 7. Hugging Face ...',
  'icon': 'https://cdn.prod.website-files.com/625447c67b621a2b13b7e3c7/6508b3b767dd5f4c4f5ceb5e_shakudo-icon-32.png'},
 {'url': 'https://medium.com/data-science-collective/agentic-ai-comparing-new-open-source-frameworks-21ec676732df',
  'title': 'Agentic AI: Comparing New Open-Source Frameworks - Medium',
  'description': "Frameworks differ in how much they abstract away, how much control they give agents, and how much coding you'll need to do to get something ...",
  'icon': 'https://miro.medium.com/v2/5d8de952517e8160e40ef9841c781cdc14a5db313057fa3c3de41c6f5b494b19'},
 {'url': 'https://langfuse.com/blog/2025-03-19-ai-agent-comparison',
  'title': 'Comparing Open-Source AI Agent Frameworks - Langfuse Blog',
  'description': 'This post offers an in-depth look at some of the leading open-source AI agent frameworks out there: LangGraph, the OpenAI Agents SDK, Smolagents ...',
  'icon': ''},
 {'url': 'https://www.reddit.com/r/LLMDevs/comments/1io0gnz/top_5_open_source_frameworks_for_building_ai/',
  'title': 'Top 5 Open Source Frameworks for building AI Agents - Reddit',
  'description': 'We created a list of Open Source AI Agent Frameworks mostly used by people and built an AI Agent using each one of them.',
  'icon': ''},
 {'url': 'https://www.analyticsvidhya.com/blog/2024/07/ai-agent-frameworks/',
  'title': 'Top 7 Frameworks for Building AI Agents in 2025 - Analytics Vidhya',
  'description': 'Explore AI Agent Frameworks like Langchain, CrewAI, and Microsoft Semantic Kernel. Understand their key importance in AI development.',
  'icon': ''},
 {'url': 'https://www.shakudo.io/blog/top-9-ai-agent-frameworks',
  'title': 'Top 9 AI Agent Frameworks as of April 2025 - Shakudo',
  'description': 'Langflow is an open-source, low-code framework designed to simplify the development of AI agents and workflows, particularly those involving RAG ...',
  'icon': 'https://cdn.prod.website-files.com/625447c67b621a2b13b7e3c7/6508b3b767dd5f4c4f5ceb5e_shakudo-icon-32.png'},
 {'url': 'https://medium.com/data-science-collective/agentic-ai-comparing-new-open-source-frameworks-21ec676732df',
  'title': 'Agentic AI: Comparing New Open-Source Frameworks - Medium',
  'description': 'Multi-agent systems allow you to build collaborative or hierarchical setups with teams of agents connected via supervisors. Most frameworks ...',
  'icon': 'https://miro.medium.com/v2/5d8de952517e8160e40ef9841c781cdc14a5db313057fa3c3de41c6f5b494b19'},
 {'url': 'https://www.reddit.com/r/LLMDevs/comments/1io0gnz/top_5_open_source_frameworks_for_building_ai/',
  'title': 'Top 5 Open Source Frameworks for building AI Agents - Reddit',
  'description': 'We created a list of Open Source AI Agent Frameworks mostly used by people and built an AI Agent using each one of them.',
  'icon': ''},
 {'url': 'https://getstream.io/blog/multiagent-ai-frameworks/',
  'title': 'Best 5 Frameworks To Build Multi-Agent AI Applications - GetStream.io',
  'description': 'This article aims to help you build AI agents powered by memory, knowledgebase, tools, and reasoning and chat with them using the command line and beautiful ...',
  'icon': 'https://getstream.io/icon.png'},
 {'url': 'https://www.firecrawl.dev/blog/best-open-source-agent-frameworks-2025',
  'title': 'The Best Open Source Frameworks For Building AI Agents in 2025',
  'description': 'In this article, we will examine the most powerful and widely adopted open source frameworks to build agents in 2025, analyzing their technical ...',
  'icon': 'https://www.firecrawl.dev/favicon.ico'},
 {'url': 'https://medium.com/data-science-collective/the-open-source-stack-for-ai-agents-8ab900e33676',
  'title': 'The Open-Source Stack for AI Agents - Medium',
  'description': "Building AI agents can be a mess of broken repos and outdated tools. Here's the real, tested open-source stack for building reliable, ...",
  'icon': 'https://miro.medium.com/v2/5d8de952517e8160e40ef9841c781cdc14a5db313057fa3c3de41c6f5b494b19'}]
```

## Generate an image with OpenAI

```python
from openai import OpenAI
import base64
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

prompt = """
A children's robot playing with a ball.
"""

result = client.images.generate(model="gpt-image-1", prompt=prompt)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
# with open("otter.png", "wb") as f:
#     f.write(image_bytes)
```

---


## File: docs/agents/google-adk/examples/firecrawl/README.md

# ChatGPT Agentic Clone with Google ADK

This repository demonstrates how to build a ChatGPT-like agentic assistant using Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

## About the Project

This project creates a powerful AI assistant that combines the capabilities of several specialized agents:

- **General Knowledge**: Answer questions using the LLM's native knowledge
- **Web Search**: Retrieve current information from the internet using Firecrawl
- **Web Extraction**: Extract and analyze content from specific URLs
- **Deep Research**: Conduct comprehensive research across multiple sources with citations
- **Image Generation**: Create images from text descriptions using OpenAI's API

The implementation follows the standard ADK package structure for local development, making it easy to extend and customize.

## Getting Started

Navigate to the app directory for complete setup instructions:

```bash
cd app
```

See the [app/README.md](app/README.md) file for detailed instructions on:

- Setting up your environment
- Configuring API keys
- Running the agent
- Testing different capabilities

## Features Demonstrated

- ✅ **Tool Integration**: Integration with external APIs (Firecrawl, OpenAI) to extend the agent's capabilities
- ✅ **Multi-Agent Architecture**: Specialized agents for different tasks coordinated by a root agent
- ✅ **Automatic Delegation**: Intelligent routing of requests to the appropriate specialized agent
- ✅ **Content Processing**: Handling of different content types (text, images) in responses
- ✅ **Safety Mechanisms**: Content filtering to prevent harmful requests

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK GitHub Repository](https://github.com/google/adk)
- [Firecrawl Documentation](https://www.firecrawl.dev)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Gemini API Documentation](https://ai.google.dev/gemini-api)

---


## File: docs/agents/google-adk/examples/launchmybakery/google.md

# `google/mcp`

This repository contains a list of Google's official Model Context Protocol (MCP) servers, guidance on how to deploy MCP servers to Google Cloud, and examples to get started.

## ⚡ Google MCP Servers

### **Remote MCP servers** 

These [remote MCP servers are managed by Google](https://docs.cloud.google.com/mcp/overview), and are available [via endpoint](https://docs.cloud.google.com/mcp/enable-disable-mcp-servers). This list will be kept up-to-date as more remote servers become available. 

* [**Google Maps (Grounding Lite)**](https://developers.google.com/maps/ai/grounding-lite)  
* [**BigQuery**](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp)  
* [**Kubernetes Engine (GKE)**](https://docs.cloud.google.com/kubernetes-engine/docs/reference/mcp)   
* [**Compute Engine (GCE)**](https://docs.cloud.google.com/compute/docs/reference/mcp)  

### **Open-source MCP servers**  

You can run these open-source MCP servers locally, or deploy them to Google Cloud (see below).  

* [**Google Workspace**](https://github.com/gemini-cli-extensions/workspace), including Google Docs, Sheets, Slides, Calendar, and Gmail. (Gemini CLI extension)  
* [**Firebase**](https://github.com/gemini-cli-extensions/firebase/) (Gemini CLI extension)  
* [**Cloud Run**](https://github.com/GoogleCloudPlatform/cloud-run-mcp) (Gemini CLI Extension)
* [**Go**](https://go.dev/gopls/features/mcp) 
* [**Google Analytics**](https://github.com/googleanalytics/google-analytics-mcp)  
* [**MCP Toolbox for Databases**](https://github.com/googleapis/genai-toolbox), including BigQuery, Cloud SQL, AlloyDB, Spanner, Firestore, and more.  
* [**Google Cloud Storage**](https://github.com/googleapis/gcloud-mcp/tree/main/packages/storage-mcp)  
* [**Genmedia**](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia), including Imagen and Veo models.  
* [**Kubernetes Engine (GKE)**](https://github.com/GoogleCloudPlatform/gke-mcp)  
* [**Google Cloud Security**](https://github.com/google/mcp-security), including Security Command Center, Chronicle, and more.  
* [**gcloud CLI**](https://github.com/googleapis/gcloud-mcp/tree/main/packages/gcloud-mcp)  
* [**Google Cloud Observability**](https://github.com/googleapis/gcloud-mcp/tree/main/packages/observability-mcp)
* [**Flutter/Dart**](https://github.com/dart-lang/ai/tree/main/pkgs/dart_mcp_server)
* [**Google Maps Platform Code Assist toolkit**](https://developers.google.com/maps/ai/mcp)
* [**Chrome DevTools**](https://github.com/ChromeDevTools/chrome-devtools-mcp)

## 💻 Examples

* [**Launch My Bakery**](http://github.com/google/mcp/tree/main/examples/launchmybakery) (`/examples/launchmybakery`)**:** A sample agent built with Agent Development Kit (ADK) that uses remote MCP servers for Google Maps and BigQuery. 


## 📙 Resources

### **Run an MCP server in Google Cloud** 

* [Documentation \- Host MCP Servers on Cloud Run](https://docs.cloud.google.com/run/docs/host-mcp-servers)  
* Blog Post \- [Build and Deploy a Remote MCP Server to Google Cloud Run in Under 10 Minutes](https://cloud.google.com/blog/topics/developers-practitioners/build-and-deploy-a-remote-mcp-server-to-google-cloud-run-in-under-10-minutes)  
* [MCP Toolbox for Databases \- Deploy to Cloud Run](https://googleapis.github.io/genai-toolbox/how-to/deploy_toolbox/), [Deploy to Google Kubernetes Engine (GKE)](https://googleapis.github.io/genai-toolbox/how-to/deploy_gke/)  
* [Blog post - Announcing MCP support for Apigee](https://cloud.google.com/blog/products/ai-machine-learning/mcp-support-for-apigee) (Turnkey MCP hosting for Apigee-hosted APIs)  
* “Tools Make an Agent” \- [Blog](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk) and [Codelab](https://codelabs.developers.google.com/codelabs/cloud-run/tools-make-an-agent)  
* Codelab \- [How to deploy a secure MCP server on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/how-to-deploy-a-secure-mcp-server-on-cloud-run#0)  
* [Codelab \- "Agent Verse" \- Architecting Multi-agent Systems](http://goo.gle/summoner) 

## 🤝 Contributing

We welcome contributions to this repository, including bug reports, feature requests, documentation improvements, and code contributions. Please see our [Contributing Guidelines](https://github.com/google/mcp/blob/main/CONTRIBUTING.md) to get started.

## 📃 License

This project is licensed under the Apache 2.0 License \- see the [LICENSE](https://github.com/google/mcp/blob/main/LICENSE) file for details.

## Disclaimers

This is not an officially supported Google product. This project is intended for demonstration purposes only.

This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security).  

---


## File: docs/agents/google-adk/examples/launchmybakery/README.md

# Launch My Bakery: Google remote MCP demo 

[![Google Cloud](https://img.shields.io/badge/Blog-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
[![Codelab](https://img.shields.io/badge/Codelab-58A55d.svg?style=for-the-badge&logo=devbox&logoColor=white)](https://codelabs.developers.google.com/adk-mcp-bigquery-maps#0)
[![Screencast](https://img.shields.io/badge/Screencast-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://www.youtube.com/watch?v=wzccErUYhTI&t=1s)

This directory contains the data artifacts and infrastructure setup scripts for the **MCP support for BigQuery & Google Maps** demo.  

## Demo Overview

This scenario demonstrates an AI Agent's ability to orchestrate enterprise data (BigQuery) and real-world geospatial context (Google Maps) to solve a complex business problem: 

> **"How would you help a friend launch a new high-end sourdough bakery in Los Angeles?"**

The agent autonomously queries BigQuery to find macro trends and uses Google Maps to validate micro-location details. The demo relies on three key datasets:

1.  **Demographics:** To identify neighborhoods with high foot traffic using census data (Macro Discovery).
2.  **Market Data:** To analyze competitor pricing and suggest a premium price point (Pricing Strategy).
3.  **Sales History:** To forecast potential revenue based on comparable store trends (Forecasting).

### Architecture Diagram

![Architecture Diagram](architecture_diagram.png)

The diagram above illustrates the flow of information in this demo. The Agent, powered by Gemini 3 Pro Preview, orchestrates requests between the user and Google Cloud services. It uses a remote (Google hosted) MCP server to securely access BigQuery for demographic and sales data, and Google Maps APIs for real-world location analysis and validation.

## Repository Structure

```text
launchmybakery/
├── data/                        # Pre-generated CSV files for BigQuery
│   ├── demographics.csv
│   ├── bakery_prices.csv
│   ├── sales_history_weekly.csv
│   └── foot_traffic.csv
├── adk_agent/                   # AI Agent Application (ADK)
│   └── mcp_bakery_app/          # App directory
│       ├── agent.py             # Agent definition
│       └── tools.py             # Custom tools for the agent
├── setup/                       # Infrastructure setup scripts
│   ├── setup_bigquery.sh        # Script to provision BigQuery dataset and tables
│   └── setup_env.sh             # Script to set up environment variables
├── cleanup/                     # Infrastructure clean up environment
│   ├── cleanup_env.sh           # Script to remove resources in environment
└── README.md                    # This documentation
```

## Prerequisites

*   **Google Cloud Project** with billing enabled.
*   **Google Cloud Shell** (Recommended) or a local terminal with the `gcloud` CLI installed.

## Deployment Guide

Follow these steps in **Google Cloud Shell** to provision the demo environment.

### 1. Clone the Repository
```bash
git clone https://github.com/google/mcp.git
cd mcp/examples/launchmybakery
```

### 2. Authenticate with Google Cloud

Run the following command to authenticate with your Google Cloud account. This is required for the ADK to access BigQuery.

```bash
gcloud config set project [YOUR-PROJECT-ID]
gcloud auth application-default login
```

Follow the prompts to complete the authentication process.

⚠️ Note: ADK does not automatically refresh your OAuth 2.0 token. If your chat session lasts more than 60 minutes, you may need to re-authenticate using the command above.

### 3. Configure Environment

Run the environment setup script. This script will:
*   Enable necessary Google Cloud APIs (Maps, BigQuery, remote MCP).
*   Create a restricted Google Maps Platform API Key.
*   Create a `.env` file with required environment variables.

```bash
chmod +x setup/setup_env.sh
./setup/setup_env.sh
```

### 4. Provision BigQuery

Run the setup script. This script automates the following:
*   Creates a Cloud Storage bucket.
*   Uploads the CSV data files.
*   Creates the `mcp_bakery` BigQuery dataset.
*   Loads the data into BigQuery tables.

```bash
chmod +x ./setup/setup_bigquery.sh
./setup/setup_bigquery.sh
```

### 5. Install ADK and Run Agent

Create a virtual environment, install the ADK, and run the agent.

```bash
# Create virtual environment
python3 -m venv .venv

# If the above fails, you may need to install python3-venv:
# apt update && apt install python3-venv

# Activate virtual environment
source .venv/bin/activate

# Install ADK
pip install google-adk

# Navigate to the app directory
cd adk_agent/

# Run the ADK web interface
adk web
```

### 6. Chat with the Agent

Open the link provided by `adk web` in your browser. You can now chat with the agent and ask it questions about the bakery data.

**Sample Questions:**

*   "I’m looking to open my fourth bakery location in Los Angeles. I need a neighborhood with early activity. Find the zip code with the highest 'morning' foot traffic score."
*   "Can you search for 'Bakeries' in that zip code to see if it's saturated? If there are too many, check for 'Specialty Coffee' shops, so I can position myself near them to capture foot traffic."
*    "Okay and I want to position this as a premium brand. What is the maximum price being charged for a 'Sourdough Loaf' in the LA Metro area?"
*    "Now I want a revenue projection for December 2025. Look at my sales history and take data from my best performing store for the 'Sourdough Loaf'. Run a forecast for December 2025 to estimate the quantity I'll sell. Then, calculate the projected total revenue using just under the premium price we found (let's use $18)"
*    "That'll cover my rent. Lastly, let's verify logistics. Find the closest "Restaurant Depot" to the proposed area and make sure that drive time is under 30 minutes for daily restocking."

### 7. Cleanup

To avoid incurring ongoing costs for BigQuery storage or other Google Cloud resources, you can run the cleanup script. This script will delete the BigQuery dataset, the Cloud Storage bucket, and the API keys created during setup. Navigate back to the root directory of the repository and run the following command:

```bash
chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh
```

## Data Logic & Narratives

The data in this repository is synthetic but structured to support specific demo narratives and successful agent reasoning chains.

| Table | Demo Purpose | Narrative Logic |
| :--- | :--- | :--- |
| **`foot_traffic`** | **Target Discovery**<br>Finding the target neighborhood. | **Morning** activity is uniquely spiked in **90403**, allowing the Agent to pinpoint it as the optimal location for a morning-focused business like a bakery. |
| **`demographics`** | **Community Profiling**<br>Analyzing market depth. | **Santa Monica (90403)** is modeled with a dense, established residential population, providing a stable baseline for customer volume. |
| **`bakery_prices`** | **Pricing Strategy**<br>Setting a price point. | **Erewhon Market** has the highest price ceiling for a Sourdough Loaf (~$18.50), while the market average is ~$8.20. This allows the Agent to confidently suggest a premium price point of ~$15-18. |
| **`sales_history`** | **Forecasting**<br>Predicting growth. | **Silver Lake** shows aggressive week-over-week growth trends, while **Playa Vista** represents a stable, high-volume flagship store, providing distinct patterns for forecasting models. |

---


## File: docs/agents/google-adk/examples/with-adk/a2a/docs/ag_ui.md

# AG‑UI: The Agent–User Interaction Protocol

*A horizontal standard to bring AI agents into user‑facing frontend applications.*

AG‑UI is the boundary layer where agents and users meet. It standardizes how agent state, UI intents, and user interactions flow between your model/agent runtime and your app’s frontend—so you can ship reliable, debuggable, user‑friendly agentic features fast.

---

## Built with the ecosystem

**First‑party partnerships & integrations**

> **Logo strip goes here** (e.g., LangGraph • CrewAI • Autogen 2 • LlamaIndex • Mastra • Pydantic AI • Vercel AI SDK • Next.js)

Short blurb: *AG‑UI works across leading agent frameworks and frontend stacks, with shared vocabulary and primitives that keep your UX consistent as your agents evolve.*

---

## Building blocks (today & upcoming)

- **Streaming chat** — Token‑level and tool‑event streaming for responsive UIs.
- **Static generative UI** — Render model output into stable, typed components.
- **Declarative generative UI** — Let agents propose UI trees; app decides what to mount.
- **Frontend tools** — Safe, typed tool calls that bridge agent logic to app actions.
- **Interrupts & human‑in‑the‑loop** — Pause, approve, edit, or steer mid‑flow.
- **In‑chat + in‑app interactions** — Chat commands alongside regular app controls.
- **Attachments & multimodality** — Files, images, audio, and structured payloads.
- **Thinking steps** — Expose summaries/redactions of chain‑of‑thought artifacts to users, safely.
- **Sub‑agent calls** — Orchestrate nested agents and delegate specialized tasks.
- **Agent steering** — Guardrails, policies, and UX affordances to keep agents on track.

> **CTA to deeper docs** → *See the full capability map in the docs.*

---

## Design patterns

Explore reusable interaction patterns for agentic UX:

- **Link‑out:** [AI‑UI Design Patterns →](/patterns) *(placeholder URL)*

---

## Why AG‑UI

**Agentic apps break the classic request/response contract.** Agents run for longer, stream work as they go, and make nondeterministic choices that can affect your UI and state. AG‑UI defines a clean, observable boundary so frontends remain predictable while agents stay flexible.

### What’s hard about user‑facing agents

- Agents are **long‑running** and **stream** intermediate work—often across multi‑turn sessions.
- Agents are **nondeterministic** and can **control UI** in ways that must be supervised.
- Apps must mix **structured + unstructured IO** (text, voice, tool calls, state updates).
- Agents need **composition**: agents **call sub‑agents**, often non-deterministically.

With AG‑UI, these become deliberate, well‑typed interactions rather than ad‑hoc wiring.

---

## Deeper proof (docs, demos, code)

| Framework / Platform    | What works today                       | Docs      | Demo      |
| ----------------------- | -------------------------------------- | --------- | --------- |
| LangGraph               | Streams, tools, interrupts, sub‑agents | [Docs](#) | [Demo](#) |
| CrewAI                  | Tools, action routing, steering        | [Docs](#) | [Demo](#) |
| Autogen 2               | Multi‑agent orchestration, messaging   | [Docs](#) | [Demo](#) |
| LlamaIndex              | Query/agent routing, UI intents        | [Docs](#) | [Demo](#) |
| OpenAI Realtime         | Live stream, events, attachments       | [Docs](#) | [Demo](#) |
| Vercel AI SDK / Next.js | Edge streaming, SSR hydration          | [Docs](#) | [Demo](#) |

> **Note:** Replace placeholders with actual URLs to docs and demos.

---

## Quick links

- **Get started** → */docs/getting-started* (placeholder)
- **Concepts** → */docs/concepts/agent-ui-boundary* (placeholder)
- **Reference** → */docs/reference* (placeholder)
- **Patterns** → */patterns* (placeholder)

---

## Optional section: How AG‑UI fits

- **Protocol**: Events, intents, and payload schemas shared by agents & apps.
- **Runtime adapters**: Bindings for popular agent frameworks.
- **Frontend kit**: Lightweight client + components to handle streaming & interrupts.
- **Observability hooks**: Surface interaction timelines for debugging & learning.

*(Include a simple diagram later: Agent(s) ⇄ AG‑UI Boundary ⇄ App UI/State)*


---


## File: docs/agents/google-adk/examples/with-adk/a2a/docs/README.md

# Agent User Interaction Protocol Documentation

The official documentation for the [Agent User Interaction Protocol](https://ag-ui.com).

### Publishing Changes

Changes will be deployed to production automatically after pushing to the default branch.

---


## File: docs/agents/google-adk/examples/with-adk/a2a/typescript/README.md

# @ag-ui/a2a

A TypeScript integration that connects AG-UI agents with remote services that expose the [A2A protocol](https://a2a.dev/). It converts AG-UI conversations into A2A payloads, forwards them through the official A2A SDK, and replays the responses back into AG-UI event streams.

> **Status:** Experimental. APIs may change while the integration stabilises.

## Features

- Message conversion helpers between AG-UI and A2A formats (user, assistant, tool, binary payloads).
- `A2AAgent` implementation that streams or performs blocking requests against A2A endpoints.
- Optional fallback from streaming to blocking requests when an agent does not support SSE.
- Event conversion utilities that surface A2A messages, task status updates, and artifact chunks as AG-UI events.
- Helper tool schema (`send_message_to_a2a_agent`) for orchestration scenarios.
- Example client and Jest tests to validate conversions and streaming flows.

## Installation

Once dependencies are installed in the monorepo:

```bash
pnpm install
pnpm --filter @ag-ui/a2a build
```

## Quick start

```ts
import { A2AAgent } from "@ag-ui/a2a";

import { A2AClient } from "@a2a-js/sdk/client";

const client = new A2AClient("https://my-a2a-agent");

const agent = new A2AAgent({
  a2aClient: client,
  initialMessages: [
    { id: "user-1", role: "user", content: "Plan a team offsite" } as any,
  ],
});

const { result, newMessages } = await agent.runAgent();
console.log(result);
console.log(newMessages);
```

You can inject your own `A2AClient` instance via the `client` option, override default instructions, or force blocking mode by setting `strategy: "blocking"`.

## Configuration reference

| Option | Description |
| ------ | ----------- |
| `a2aClient` | Required. Provide an `A2AClient` instance (with any auth headers or custom fetch logic you need). |

## Environment variables & authentication

The integration relies on the underlying A2A agent for authentication. Common patterns include:

- `A2A_AGENT_URL` – set in deployment environments to point to the remote agent base URL.
- `A2A_API_KEY` or `A2A_BEARER_TOKEN` – consumed by a wrapped `fetch` inside a custom `A2AClient` instance if the remote agent enforces API key or bearer authentication.

Pass any credentials to the `A2AClient` you provide to `A2AAgent`, or configure an HTTP proxy that injects the correct headers.

## Utilities

- `convertAGUIMessagesToA2A(messages, options)` — reshapes AG-UI history into A2A message objects, forwarding only user/assistant/tool turns and preserving the tool payloads.
- `convertA2AEventToAGUIEvents(event, options)` — maps an A2A stream event to AG-UI text and tool events (`TEXT_MESSAGE_CHUNK`, `TOOL_CALL_*`, `TOOL_CALL_RESULT`).
- `sendMessageToA2AAgentTool` — JSON schema describing a `send_message_to_a2a_agent` tool for orchestration agents.

## Testing

```bash
pnpm --filter @ag-ui/a2a test
```

The suite covers conversion edge cases and streaming / fallback behaviour using mocked A2A clients.

## Examples

- `examples/basic.ts` – minimal script. If you set `A2A_AGENT_URL`, it will connect to that agent through the real `A2AClient`. Otherwise it falls back to a tiny in-memory mock client so you can observe the integration without hitting a remote endpoint.

## Release checklist

1. `pnpm --filter @ag-ui/a2a build`
2. `pnpm --filter @ag-ui/a2a test`
3. Update CHANGELOG / release notes.
4. Publish with `pnpm publish --filter @ag-ui/a2a`.

---


## File: docs/agents/google-adk/examples/with-adk/README.md

# CopilotKit <> ADK Starter

This is a starter template for building AI agents using Google's [ADK](https://google.github.io/adk-docs/) and [CopilotKit](https://copilotkit.ai). It provides a modern Next.js application with an integrated investment analyst agent that can research stocks, analyze market data, and provide investment insights.

## Prerequisites

- Node.js 18+
- Python 3.12+
- Google Makersuite API Key (for the ADK agent) (see https://makersuite.google.com/app/apikey)
- Any of the following package managers:
  - pnpm (recommended)
  - npm
  - yarn
  - bun

> **Note:** This repository ignores lock files (package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb) to avoid conflicts between different package managers. Each developer should generate their own lock file using their preferred package manager. After that, make sure to delete it from the .gitignore.

## Getting Started

1. Install dependencies using your preferred package manager:
```bash
# Using pnpm (recommended)
pnpm install

# Using npm
npm install

# Using yarn
yarn install

# Using bun
bun install
```

2. Install Python dependencies for the ADK agent:
```bash
# Using pnpm
pnpm install:agent

# Using npm
npm run install:agent

# Using yarn
yarn install:agent

# Using bun
bun run install:agent
```

> **Note:** This will automatically setup a `.venv` (virtual environment) inside the `agent` directory.
>
> To activate the virtual environment manually, you can run:
> ```bash
> source agent/.venv/bin/activate
> ```


3. Set up your Google API key:
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

4. Start the development server:
```bash
# Using pnpm
pnpm dev

# Using npm
npm run dev

# Using yarn
yarn dev

# Using bun
bun run dev
```

This will start both the UI and agent servers concurrently.

## Available Scripts
The following scripts can also be run using your preferred package manager:
- `dev` - Starts both UI and agent servers in development mode
- `dev:debug` - Starts development servers with debug logging enabled
- `dev:ui` - Starts only the Next.js UI server
- `dev:agent` - Starts only the ADK agent server
- `build` - Builds the Next.js application for production
- `start` - Starts the production server
- `lint` - Runs ESLint for code linting
- `install:agent` - Installs Python dependencies for the agent

## Documentation

The main UI component is in `src/app/page.tsx`. You can:
- Modify the theme colors and styling
- Add new frontend actions
- Customize the CopilotKit sidebar appearance

## 📚 Documentation

- [ADK Documentation](https://google.github.io/adk-docs/) - Learn more about the ADK and its features
- [CopilotKit Documentation](https://docs.copilotkit.ai) - Explore CopilotKit's capabilities
- [Next.js Documentation](https://nextjs.org/docs) - Learn about Next.js features and API


## Contributing

Feel free to submit issues and enhancement requests! This starter is designed to be easily extensible.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Agent Connection Issues
If you see "I'm having trouble connecting to my tools", make sure:
1. The ADK agent is running on port 8000
2. Your Google API key is set correctly
3. Both servers started successfully

### Python Dependencies
If you encounter Python import errors:
```bash
cd agent
pip install -r requirements.txt
```
---


## File: docs/agents/google-adk/GEMINI.md

Coding Agent guidance:
# Google Agent Development Kit (ADK) Python Cheatsheet

This document serves as a long-form, comprehensive reference for building, orchestrating, and deploying AI agents using the Python Agent Development Kit (ADK). It aims to cover every significant aspect with greater detail, more code examples, and in-depth best practices.

## Table of Contents

1.  [Core Concepts & Project Structure](#1-core-concepts--project-structure)
    *   1.1 ADK's Foundational Principles
    *   1.2 Essential Primitives
    *   1.3 Standard Project Layout
    *   1.A Build Agents without Code (Agent Config)
2.  [Agent Definitions (`LlmAgent`)](#2-agent-definitions-llmagent)
    *   2.1 Basic `LlmAgent` Setup
    *   2.2 Advanced `LlmAgent` Configuration
    *   2.3 LLM Instruction Crafting
    *   2.4 Production Wrapper (`App`)
3.  [Orchestration with Workflow Agents](#3-orchestration-with-workflow-agents)
    *   3.1 `SequentialAgent`: Linear Execution
    *   3.2 `ParallelAgent`: Concurrent Execution
    *   3.3 `LoopAgent`: Iterative Processes
4.  [Multi-Agent Systems & Communication](#4-multi-agent-systems--communication)
    *   4.1 Agent Hierarchy
    *   4.2 Inter-Agent Communication Mechanisms
    *   4.3 Common Multi-Agent Patterns
    *   4.A Distributed Communication (A2A Protocol)
5.  [Building Custom Agents (`BaseAgent`)](#5-building-custom-agents-baseagent)
    *   5.1 When to Use Custom Agents
    *   5.2 Implementing `_run_async_impl`
6.  [Models: Gemini, LiteLLM, and Vertex AI](#6-models-gemini-litellm-and-vertex-ai)
    *   6.1 Google Gemini Models (AI Studio & Vertex AI)
    *   6.2 Other Cloud & Proprietary Models via LiteLLM
    *   6.3 Open & Local Models via LiteLLM (Ollama, vLLM)
    *   6.4 Customizing LLM API Clients
7.  [Tools: The Agent's Capabilities](#7-tools-the-agents-capabilities)
    *   7.1 Defining Function Tools: Principles & Best Practices
    *   7.2 The `ToolContext` Object: Accessing Runtime Information
    *   7.3 All Tool Types & Their Usage
    *   7.4 Tool Confirmation (Human-in-the-Loop)
8.  [Context, State, and Memory Management](#8-context-state-and-memory-management)
    *   8.1 The `Session` Object & `SessionService`
    *   8.2 `State`: The Conversational Scratchpad
    *   8.3 `Memory`: Long-Term Knowledge & Retrieval
    *   8.4 `Artifacts`: Binary Data Management
9.  [Runtime, Events, and Execution Flow](#9-runtime-events-and-execution-flow)
    *   9.1 Runtime Configuration (`RunConfig`)
    *   9.2 The `Runner`: The Orchestrator
    *   9.3 The Event Loop: Core Execution Flow
    *   9.4 `Event` Object: The Communication Backbone
    *   9.5 Asynchronous Programming (Python Specific)
10. [Control Flow with Callbacks](#10-control-flow-with-callbacks)
    *   10.1 Callback Mechanism: Interception & Control
    *   10.2 Types of Callbacks
    *   10.3 Callback Best Practices
    *   10.A Global Control with Plugins
11. [Authentication for Tools](#11-authentication-for-tools)
    *   11.1 Core Concepts: `AuthScheme` & `AuthCredential`
    *   11.2 Interactive OAuth/OIDC Flows
    *   11.3 Custom Tool Authentication
12. [Deployment Strategies](#12-deployment-strategies)
    *   12.1 Local Development & Testing (`adk web`, `adk run`, `adk api_server`)
    *   12.2 Vertex AI Agent Engine
    *   12.3 Cloud Run
    *   12.4 Google Kubernetes Engine (GKE)
    *   12.5 CI/CD Integration
13. [Evaluation and Safety](#13-evaluation-and-safety)
    *   13.1 Agent Evaluation (`adk eval`)
    *   13.2 Safety & Guardrails
14. [Debugging, Logging & Observability](#14-debugging-logging--observability)
15. [Streaming & Advanced I/O](#15-streaming--advanced-io)
16. [Performance Optimization](#16-performance-optimization)
17. [General Best Practices & Common Pitfalls](#17-general-best-practices--common-pitfalls)
18. [Official API & CLI References](#18-official-api--cli-references)

---

## 1. Core Concepts & Project Structure

### 1.1 ADK's Foundational Principles

*   **Modularity**: Break down complex problems into smaller, manageable agents and tools.
*   **Composability**: Combine simple agents and tools to build sophisticated systems.
*   **Observability**: Detailed event logging and tracing capabilities to understand agent behavior.
*   **Extensibility**: Easily integrate with external services, models, and frameworks.
*   **Deployment-Agnostic**: Design agents once, deploy anywhere.

### 1.2 Essential Primitives

*   **`Agent`**: The core intelligent unit. Can be `LlmAgent` (LLM-driven) or `BaseAgent` (custom/workflow).
*   **`Tool`**: Callable function/class providing external capabilities (`FunctionTool`, `OpenAPIToolset`, etc.).
*   **`Session`**: A unique, stateful conversation thread with history (`events`) and short-term memory (`state`).
*   **`State`**: Key-value dictionary within a `Session` for transient conversation data.
*   **`Memory`**: Long-term, searchable knowledge base beyond a single session (`MemoryService`).
*   **`Artifact`**: Named, versioned binary data (files, images) associated with a session or user.
*   **`Runner`**: The execution engine; orchestrates agent activity and event flow.
*   **`Event`**: Atomic unit of communication and history; carries content and side-effect `actions`.
*   **`InvocationContext`**: The comprehensive root context object holding all runtime information for a single `run_async` call.

### 1.3 Standard Project Layout

A well-structured ADK project is crucial for maintainability and leveraging `adk` CLI tools.

```
your_project_root/
├── my_first_agent/             # Each folder is a distinct agent app
│   ├── __init__.py             # Makes `my_first_agent` a Python package (`from . import agent`)
│   ├── agent.py                # Contains `root_agent` definition and `LlmAgent`/WorkflowAgent instances
│   ├── tools.py                # Custom tool function definitions
│   ├── data/                   # Optional: static data, templates
│   └── .env                    # Environment variables (API keys, project IDs)
├── my_second_agent/
│   ├── __init__.py
│   └── agent.py
├── requirements.txt            # Project's Python dependencies (e.g., google-adk, litellm)
├── tests/                      # Unit and integration tests
│   ├── unit/
│   │   └── test_tools.py
│   └── integration/
│       └── test_my_first_agent.py
│       └── my_first_agent.evalset.json # Evaluation dataset for `adk eval`
└── main.py                     # Optional: Entry point for custom FastAPI server deployment
```
*   `adk web` and `adk run` automatically discover agents in subdirectories with `__init__.py` and `agent.py`.
*   `.env` files are automatically loaded by `adk` tools when run from the root or agent directory.

### 1.A Build Agents without Code (Agent Config)

ADK allows you to define agents, tools, and even multi-agent workflows using a simple YAML format, eliminating the need to write Python code for orchestration. This is ideal for rapid prototyping and for non-programmers to configure agents.

#### **Getting Started with Agent Config**

*   **Create a Config-based Agent**:
    ```bash
    adk create --type=config my_yaml_agent
    ```
    This generates a `my_yaml_agent/` folder with `root_agent.yaml` and `.env` files.

*   **Environment Setup** (in `.env` file):
    ```bash
    # For Google AI Studio (simpler setup)
    GOOGLE_GENAI_USE_VERTEXAI=0
    GOOGLE_API_KEY=<your-Google-Gemini-API-key>
    
    # For Google Cloud Vertex AI (production)
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=eu-west1
    ```

#### **Core Agent Config Structure**

*   **Basic Agent (`root_agent.yaml`)**:
    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: assistant_agent
    model: gemini-2.5-flash
    description: A helper agent that can answer users' various questions.
    instruction: You are an agent to help answer users' various questions.
    ```

*   **Agent with Built-in Tools**:
    ```yaml
    name: search_agent
    model: gemini-2.0-flash
    description: 'an agent whose job it is to perform Google search queries and answer questions about the results.'
    instruction: You are an agent whose job is to perform Google search queries and answer questions about the results.
    tools:
      - name: google_search # Built-in ADK tool
    ```

*   **Agent with Custom Tools**:
    ```yaml
    agent_class: LlmAgent
    model: gemini-2.5-flash
    name: prime_agent
    description: Handles checking if numbers are prime.
    instruction: |
      You are responsible for checking whether numbers are prime.
      When asked to check primes, you must call the check_prime tool with a list of integers.
      Never attempt to determine prime numbers manually.
    tools:
      - name: ma_llm.check_prime # Reference to Python function
    ```

*   **Multi-Agent System with Sub-Agents**:
    ```yaml
    agent_class: LlmAgent
    model: gemini-2.5-flash
    name: root_agent
    description: Learning assistant that provides tutoring in code and math.
    instruction: |
      You are a learning assistant that helps students with coding and math questions.
      
      You delegate coding questions to the code_tutor_agent and math questions to the math_tutor_agent.
      
      Follow these steps:
      1. If the user asks about programming or coding, delegate to the code_tutor_agent.
      2. If the user asks about math concepts or problems, delegate to the math_tutor_agent.
      3. Always provide clear explanations and encourage learning.
    sub_agents:
      - config_path: code_tutor_agent.yaml
      - config_path: math_tutor_agent.yaml
    ```

#### **Loading Agent Config in Python**

```python
from google.adk.agents import config_agent_utils
root_agent = config_agent_utils.from_config("{agent_folder}/root_agent.yaml")
```

#### **Running Agent Config Agents**

From the agent directory, use any of these commands:
*   `adk web` - Launch web UI interface
*   `adk run` - Run in terminal without UI
*   `adk api_server` - Run as a service for other applications

#### **Deployment Support**

Agent Config agents can be deployed using:
*   `adk deploy cloud_run` - Deploy to Google Cloud Run
*   `adk deploy agent_engine` - Deploy to Vertex AI Agent Engine

#### **Key Features & Capabilities**

*   **Supported Built-in Tools**: `google_search`, `load_artifacts`, `url_context`, `exit_loop`, `preload_memory`, `get_user_choice`, `enterprise_web_search`, `load_web_page`
*   **Custom Tool Integration**: Reference Python functions using fully qualified module paths
*   **Multi-Agent Orchestration**: Link agents via `config_path` references
*   **Schema Validation**: Built-in YAML schema for IDE support and validation

#### **Current Limitations** (Experimental Feature)

*   **Model Support**: Only Gemini models currently supported
*   **Language Support**: Custom tools must be written in Python
*   **Unsupported Agent Types**: `LangGraphAgent`, `A2aAgent`
*   **Unsupported Tools**: `AgentTool`, `LongRunningFunctionTool`, `VertexAiSearchTool`, `MCPToolset`, `LangchainTool`, `ExampleTool`

For complete examples and reference, see the [ADK samples repository](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code).

---

## 2. Agent Definitions (`LlmAgent`)

The `LlmAgent` is the cornerstone of intelligent behavior, leveraging an LLM for reasoning and decision-making.

### 2.1 Basic `LlmAgent` Setup

```python
from google.adk.agents import Agent

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    # Mock implementation
    if city.lower() == "new york":
        return {"status": "success", "time": "10:30 AM EST"}
    return {"status": "error", "message": f"Time for {city} not available."}

my_first_llm_agent = Agent(
    name="time_teller_agent",
    model="gemini-3-flash-preview", # Essential: The LLM powering the agent
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    description="Tells the current time in a specified city.", # Crucial for multi-agent delegation
    tools=[get_current_time] # List of callable functions/tool instances
)
```

### 2.2 Advanced `LlmAgent` Configuration

*   **`generate_content_config`**: Controls LLM generation parameters (temperature, token limits, safety).
    ```python
    from google.genai import types as genai_types
    from google.adk.agents import Agent

    gen_config = genai_types.GenerateContentConfig(
        temperature=0.2,            # Controls randomness (0.0-1.0), lower for more deterministic.
        top_p=0.9,                  # Nucleus sampling: sample from top_p probability mass.
        top_k=40,                   # Top-k sampling: sample from top_k most likely tokens.
        max_output_tokens=1024,     # Max tokens in LLM's response.
        stop_sequences=["## END"]   # LLM will stop generating if these sequences appear.
    )
    agent = Agent(
        # ... basic config ...
        generate_content_config=gen_config
    )
    ```

*   **`output_key`**: Automatically saves the agent's final text or structured (if `output_schema` is used) response to the `session.state` under this key. Facilitates data flow between agents.
    ```python
    agent = Agent(
        # ... basic config ...
        output_key="llm_final_response_text"
    )
    # After agent runs, session.state['llm_final_response_text'] will contain its output.
    ```

*   **`input_schema` & `output_schema`**: Define strict JSON input/output formats using Pydantic models.
    > **Warning**: Using `output_schema` forces the LLM to generate JSON and **disables** its ability to use tools or delegate to other agents.

#### **Example: Defining and Using Structured Output**

This is the most reliable way to make an LLM produce predictable, parseable JSON, which is essential for multi-agent workflows.

1.  **Define the Schema with Pydantic:**
    ```python
    from pydantic import BaseModel, Field
    from typing import Literal

    class SearchQuery(BaseModel):
        """Model representing a specific search query for web search."""
        search_query: str = Field(
            description="A highly specific and targeted query for web search."
        )

    class Feedback(BaseModel):
        """Model for providing evaluation feedback on research quality."""
        grade: Literal["pass", "fail"] = Field(
            description="Evaluation result. 'pass' if the research is sufficient, 'fail' if it needs revision."
        )
        comment: str = Field(
            description="Detailed explanation of the evaluation, highlighting strengths and/or weaknesses of the research."
        )
        follow_up_queries: list[SearchQuery] | None = Field(
            default=None,
            description="A list of specific, targeted follow-up search queries needed to fix research gaps. This should be null or empty if the grade is 'pass'."
        )
    ```
    *   **`BaseModel` & `Field`**: Define data types, defaults, and crucial `description` fields. These descriptions are sent to the LLM to guide its output.
    *   **`Literal`**: Enforces strict enum-like values (`"pass"` or `"fail"`), preventing the LLM from hallucinating unexpected values.

2.  **Assign the Schema to an `LlmAgent`:**
    ```python
    research_evaluator = LlmAgent(
        name="research_evaluator",
        model="gemini-3-pro-preview",
        instruction="""You are a meticulous quality assurance analyst. Evaluate the research findings in 'section_research_findings' and be very critical.
        If you find significant gaps, assign a grade of 'fail', write a detailed comment, and generate 5-7 specific follow-up queries.
        If the research is thorough, grade it 'pass'.
        Your response must be a single, raw JSON object validating against the 'Feedback' schema.
        """,
        output_schema=Feedback, # This forces the LLM to output JSON matching the Feedback model.
        output_key="research_evaluation", # The resulting JSON object will be saved to state.
        disallow_transfer_to_peers=True, # Prevents this agent from delegating. Its job is only to evaluate.
    )
    ```

*   **`include_contents`**: Controls whether the conversation history is sent to the LLM.
    *   `'default'` (default): Sends relevant history.
    *   `'none'`: Sends no history; agent operates purely on current turn's input and `instruction`. Useful for stateless API wrapper agents.
    ```python
    agent = Agent(..., include_contents='none')
    ```

*   **`planner`**: Assign a `BasePlanner` instance to enable multi-step reasoning.
    *   **`BuiltInPlanner`**: Leverages a model's native "thinking" or planning capabilities (e.g., Gemini).
        ```python
        from google.adk.planners import BuiltInPlanner
        from google.genai.types import ThinkingConfig

        agent = Agent(
            model="gemini-3-flash-preview",
            planner=BuiltInPlanner(
                thinking_config=ThinkingConfig(include_thoughts=True)
            ),
            # ... tools ...
        )
        ```
    *   **`PlanReActPlanner`**: Instructs the model to follow a structured Plan-Reason-Act output format, useful for models without built-in planning.

*   **`code_executor`**: Assign a `BaseCodeExecutor` to allow the agent to execute code blocks.
    *   **`BuiltInCodeExecutor`**: The standard, sandboxed code executor provided by ADK for safe execution.
        ```python
        from google.adk.code_executors import BuiltInCodeExecutor
        agent = Agent(
            name="code_agent",
            model="gemini-3-flash-preview",
            instruction="Write and execute Python code to solve math problems.",
            code_executor=BuiltInCodeExecutor() # Corrected from a list to an instance
        )
        ```

*   **Callbacks**: Hooks for observing and modifying agent behavior at key lifecycle points (`before_model_callback`, `after_tool_callback`, etc.). (Covered in Callbacks).

### 2.3 LLM Instruction Crafting (`instruction`)

The `instruction` is critical. It guides the LLM's behavior, persona, and tool usage. The following examples demonstrate powerful techniques for creating specialized, reliable agents.

**Best Practices & Examples:**

*   **Be Specific & Concise**: Avoid ambiguity.
*   **Define Persona & Role**: Give the LLM a clear role.
*   **Constrain Behavior & Tool Use**: Explicitly state what the LLM *and should not* do.
*   **Define Output Format**: Tell the LLM *exactly* what its output should look like, especially when not using `output_schema`.
*   **Dynamic Injection**: Use `{state_key}` to inject runtime data from `session.state` into the prompt.
*   **Iteration**: Test, observe, and refine instructions.

**Example 1: Constraining Tool Use and Output Format**
```python
import datetime
from google.adk.tools import google_search   


plan_generator = LlmAgent(
    model="gemini-3-flash-preview",
    name="plan_generator",
    description="Generates a 4-5 line action-oriented research plan.",
    instruction=f"""
    You are a research strategist. Your job is to create a high-level RESEARCH PLAN, not a summary.
    **RULE: Your output MUST be a bulleted list of 4-5 action-oriented research goals or key questions.**
    - A good goal starts with a verb like "Analyze," "Identify," "Investigate."
    - A bad output is a statement of fact like "The event was in April 2024."
    **TOOL USE IS STRICTLY LIMITED:**
    Your goal is to create a generic, high-quality plan *without searching*.
    Only use `google_search` if a topic is ambiguous and you absolutely cannot create a plan without it.
    You are explicitly forbidden from researching the *content* or *themes* of the topic.
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[google_search],
)
```

**Example 2: Injecting Data from State and Specifying Custom Tags**
This agent's `instruction` relies on data placed in `session.state` by previous agents.
```python
report_composer = LlmAgent(
    model="gemini-3-pro-preview",
    name="report_composer_with_citations",
    include_contents="none", # History not needed; all data is injected.
    description="Transforms research data and a markdown outline into a final, cited report.",
    instruction="""
    Transform the provided data into a polished, professional, and meticulously cited research report.

    ---
    ### INPUT DATA
    *   Research Plan: `{research_plan}`
    *   Research Findings: `{section_research_findings}`
    *   Citation Sources: `{sources}`
    *   Report Structure: `{report_sections}`

    ---
    ### CRITICAL: Citation System
    To cite a source, you MUST insert a special citation tag directly after the claim it supports.

    **The only correct format is:** `<cite source="src-ID_NUMBER" />`

    ---
    ### Final Instructions
    Generate a comprehensive report using ONLY the `<cite source="src-ID_NUMBER" />` tag system for all citations.
    The final report must strictly follow the structure provided in the **Report Structure** markdown outline.
    Do not include a "References" or "Sources" section; all citations must be in-line.
    """,
    output_key="final_cited_report",
)
```

### 2.4 Production Wrapper (`App`)
Wraps the `root_agent` to enable production-grade runtime features that an `Agent` cannot handle alone.

```python
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.events_compaction_config import EventsCompactionConfig
from google.adk.apps.resumability_config import ResumabilityConfig

production_app = App(
    name="my_app",
    root_agent=my_agent,
    # 1. Reduce costs/latency for long contexts
    context_cache_config=ContextCacheConfig(min_tokens=2048, ttl_seconds=600),
    # 2. Allow resuming crashed workflows from last state
    resumability_config=ResumabilityConfig(is_resumable=True),
    # 3. Manage long conversation history automatically
    events_compaction_config=EventsCompactionConfig(compaction_interval=5, overlap_size=1)
)

# Usage: Pass 'app' instead of 'agent' to the Runner
# runner = Runner(app=production_app, ...)
```

---

## 3. Orchestration with Workflow Agents

Workflow agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) provide deterministic control flow, combining LLM capabilities with structured execution. They do **not** use an LLM for their own orchestration logic.

### 3.1 `SequentialAgent`: Linear Execution

Executes `sub_agents` one after another in the order defined. The `InvocationContext` is passed along, allowing state changes to be visible to subsequent agents.

```python
from google.adk.agents import SequentialAgent, Agent

# Agent 1: Summarizes a document and saves to state
summarizer = Agent(
    name="DocumentSummarizer",
    model="gemini-3-flash-preview",
    instruction="Summarize the provided document in 3 sentences.",
    output_key="document_summary" # Output saved to session.state['document_summary']
)

# Agent 2: Generates questions based on the summary from state
question_generator = Agent(
    name="QuestionGenerator",
    model="gemini-3-flash-preview",
    instruction="Generate 3 comprehension questions based on this summary: {document_summary}",
    # 'document_summary' is dynamically injected from session.state
)

document_pipeline = SequentialAgent(
    name="SummaryQuestionPipeline",
    sub_agents=[summarizer, question_generator], # Order matters!
    description="Summarizes a document then generates questions."
)
```

### 3.2 `ParallelAgent`: Concurrent Execution

Executes `sub_agents` simultaneously. Useful for independent tasks to reduce overall latency. All sub-agents share the same `session.state`.

```python
from google.adk.agents import ParallelAgent, Agent, SequentialAgent

# Agents to fetch data concurrently
fetch_stock_price = Agent(name="StockPriceFetcher", ..., output_key="stock_data")
fetch_news_headlines = Agent(name="NewsFetcher", ..., output_key="news_data")
fetch_social_sentiment = Agent(name="SentimentAnalyzer", ..., output_key="sentiment_data")

# Agent to merge results (runs after ParallelAgent, usually in a SequentialAgent)
merger_agent = Agent(
    name="ReportGenerator",
    model="gemini-3-flash-preview",
    instruction="Combine stock data: {stock_data}, news: {news_data}, and sentiment: {sentiment_data} into a market report."
)

# Pipeline to run parallel fetching then sequential merging
market_analysis_pipeline = SequentialAgent(
    name="MarketAnalyzer",
    sub_agents=[
        ParallelAgent(
            name="ConcurrentFetch",
            sub_agents=[fetch_stock_price, fetch_news_headlines, fetch_social_sentiment]
        ),
        merger_agent # Runs after all parallel agents complete
    ]
)
```
*   **Concurrency Caution**: When parallel agents write to the same `state` key, race conditions can occur. Always use distinct `output_key`s or manage concurrent writes explicitly.

### 3.3 `LoopAgent`: Iterative Processes

Repeatedly executes its `sub_agents` (sequentially within each loop iteration) until a condition is met or `max_iterations` is reached.

#### **Termination of `LoopAgent`**
A `LoopAgent` terminates when:
1.  `max_iterations` is reached.
2.  Any `Event` yielded by a sub-agent (or a tool within it) sets `actions.escalate = True`. This provides dynamic, content-driven loop termination.

#### **Example: Iterative Refinement Loop with a Custom `BaseAgent` for Control**
This example shows a loop that continues until a condition, determined by an evaluation agent, is met.

```python
from google.adk.agents import LoopAgent, Agent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

# An LLM Agent that evaluates research and produces structured JSON output
research_evaluator = Agent(
    name="research_evaluator",
    # ... configuration from Section 2.2 ...
    output_schema=Feedback,
    output_key="research_evaluation",
)

# An LLM Agent that performs additional searches based on feedback
enhanced_search_executor = Agent(
    name="enhanced_search_executor",
    instruction="Execute the follow-up queries from 'research_evaluation' and combine with existing findings.",
    # ... other configurations ...
)

# A custom BaseAgent to check the evaluation and stop the loop
class EscalationChecker(BaseAgent):
    """Checks research evaluation and escalates to stop the loop if grade is 'pass'."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        evaluation = ctx.session.state.get("research_evaluation")
        if evaluation and evaluation.get("grade") == "pass":
            # The key to stopping the loop: yield an Event with escalate=True
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # Let the loop continue
            yield Event(author=self.name)

# Define the loop
iterative_refinement_loop = LoopAgent(
    name="IterativeRefinementLoop",
    sub_agents=[
        research_evaluator, # Step 1: Evaluate
        EscalationChecker(name="EscalationChecker"), # Step 2: Check and maybe stop
        enhanced_search_executor, # Step 3: Refine (only runs if loop didn't stop)
    ],
    max_iterations=5, # Fallback to prevent infinite loops
    description="Iteratively evaluates and refines research until it passes quality checks."
)
```

---

## 4. Multi-Agent Systems & Communication

Building complex applications by composing multiple, specialized agents.

### 4.1 Agent Hierarchy

A hierarchical (tree-like) structure of parent-child relationships defined by the `sub_agents` parameter during `BaseAgent` initialization. An agent can only have one parent.

```python
# Conceptual Hierarchy
# Root
# └── Coordinator (LlmAgent)
#     ├── SalesAgent (LlmAgent)
#     └── SupportAgent (LlmAgent)
#     └── DataPipeline (SequentialAgent)
#         ├── DataFetcher (LlmAgent)
#         └── DataProcessor (LlmAgent)
```

### 4.2 Inter-Agent Communication Mechanisms

1.  **Shared Session State (`session.state`)**: The most common and robust method. Agents read from and write to the same mutable dictionary.
    *   **Mechanism**: Agent A sets `ctx.session.state['key'] = value`. Agent B later reads `ctx.session.state.get('key')`. `output_key` on `LlmAgent` is a convenient auto-setter.
    *   **Best for**: Passing intermediate results, shared configurations, and flags in pipelines (Sequential, Loop agents).

2.  **LLM-Driven Delegation (`transfer_to_agent`)**: A `LlmAgent` can dynamically hand over control to another agent based on its reasoning.
    *   **Mechanism**: The LLM generates a special `transfer_to_agent` function call. The ADK framework intercepts this, routes the next turn to the target agent.
    *   **Prerequisites**:
        *   The initiating `LlmAgent` needs `instruction` to guide delegation and `description` of the target agent(s).
        *   Target agents need clear `description`s to help the LLM decide.
        *   Target agent must be discoverable within the current agent's hierarchy (direct `sub_agent` or a descendant).
    *   **Configuration**: Can be enabled/disabled via `disallow_transfer_to_parent` and `disallow_transfer_to_peers` on `LlmAgent`.

3.  **Explicit Invocation (`AgentTool`)**: An `LlmAgent` can treat another `BaseAgent` instance as a callable tool.
    *   **Mechanism**: Wrap the target agent (`target_agent`) in `AgentTool(agent=target_agent)` and add it to the calling `LlmAgent`'s `tools` list. The `AgentTool` generates a `FunctionDeclaration` for the LLM. When called, `AgentTool` runs the target agent and returns its final response as the tool result.
    *   **Best for**: Hierarchical task decomposition, where a higher-level agent needs a specific output from a lower-level agent.

**Delegation vs. Agent-as-a-Tool**
*   **Delegation (`sub_agents`)**: The parent agent *transfers control*. The sub-agent interacts directly with the user for subsequent turns until it finishes.
*   **Agent-as-a-Tool (`AgentTool`)**: The parent agent *calls* another agent like a function. The parent remains in control, receives the sub-agent's entire interaction as a single tool result, and summarizes it for the user.

```python
# Delegation: "I'll let the specialist handle this conversation."
root = Agent(name="root", sub_agents=[specialist])

# Agent-as-a-Tool: "I need the specialist to do a task and give me the results."
from google.adk.tools import AgentTool
root = Agent(name="root", tools=[AgentTool(specialist)])
```

### 4.3 Common Multi-Agent Patterns

*   **Coordinator/Dispatcher**: A central agent routes requests to specialized sub-agents (often via LLM-driven delegation).
*   **Sequential Pipeline**: `SequentialAgent` orchestrates a fixed sequence of tasks, passing data via shared state.
*   **Parallel Fan-Out/Gather**: `ParallelAgent` runs concurrent tasks, followed by a final agent that synthesizes results from state.
*   **Review/Critique (Generator-Critic)**: `SequentialAgent` with a generator followed by a critic, often in a `LoopAgent` for iterative refinement.
*   **Hierarchical Task Decomposition (Planner/Executor)**: High-level agents break down complex problems, delegating sub-tasks to lower-level agents (often via `AgentTool` and delegation).

#### **Example: Hierarchical Planner/Executor Pattern**
This pattern combines several mechanisms. A top-level `interactive_planner_agent` uses another agent (`plan_generator`) as a tool to create a plan, then delegates the execution of that plan to a complex `SequentialAgent` (`research_pipeline`).

```python
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

# Assume plan_generator, section_planner, research_evaluator, etc. are defined.

# The execution pipeline itself is a complex agent.
research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="Executes a pre-approved research plan. It performs iterative research, evaluation, and composes a final, cited report.",
    sub_agents=[
        section_planner,
        section_researcher,
        LoopAgent(
            name="iterative_refinement_loop",
            max_iterations=3,
            sub_agents=[
                research_evaluator,
                EscalationChecker(name="escalation_checker"),
                enhanced_search_executor,
            ],
        ),
        report_composer,
    ],
)

# The top-level agent that interacts with the user.
interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model="gemini-3-flash-preview",
    description="The primary research assistant. It collaborates with the user to create a research plan, and then executes it upon approval.",
    instruction="""
    You are a research planning assistant. Your workflow is:
    1.  **Plan:** Use the `plan_generator` tool to create a draft research plan.
    2.  **Refine:** Incorporate user feedback until the plan is approved.
    3.  **Execute:** Once the user gives EXPLICIT approval (e.g., "looks good, run it"), you MUST delegate the task to the `research_pipeline` agent.
    Your job is to Plan, Refine, and Delegate. Do not do the research yourself.
    """,
    # The planner delegates to the pipeline.
    sub_agents=[research_pipeline],
    # The planner uses another agent as a tool.
    tools=[AgentTool(plan_generator)],
    output_key="research_plan",
)

# The root agent of the application is the top-level planner.
root_agent = interactive_planner_agent
```

### 4.A. Distributed Communication (A2A Protocol)

The Agent-to-Agent (A2A) Protocol enables agents to communicate over a network, even if they are written in different languages or run as separate services. Use A2A for integrating with third-party agents, building microservice-based agent architectures, or when a strong, formal API contract is needed. For internal code organization, prefer local sub-agents.

*   **Exposing an Agent**: Make an existing ADK agent available to others over A2A.
    *   **`to_a2a()` Utility**: The simplest method. Wraps your `root_agent` and creates a runnable FastAPI app, auto-generating the required `agent.json` card.
        ```python
        from google.adk.a2a.utils.agent_to_a2a import to_a2a
        # root_agent is your existing ADK Agent instance
        a2a_app = to_a2a(root_agent, port=8001)
        # Run with: uvicorn your_module:a2a_app --host localhost --port 8001
        ```
    *   **`adk api_server --a2a`**: A CLI command that serves agents from a directory. Requires you to manually create an `agent.json` card for each agent you want to expose.

*   **Consuming a Remote Agent**: Use a remote A2A agent as if it were a local agent.
    *   **`RemoteA2aAgent`**: This agent acts as a client proxy. You initialize it with the URL to the remote agent's card.
        ```python
        from google.adk.a2a.remote_a2a_agent import RemoteA2aAgent

        # This agent can now be used as a sub-agent or tool
        prime_checker_agent = RemoteA2aAgent(
            name="prime_agent",
            description="A remote agent that checks if numbers are prime.",
            agent_card="http://localhost:8001/a2a/check_prime_agent/.well-known/agent.json"
        )
        ```

---

## 5. Building Custom Agents (`BaseAgent`)

For unique orchestration logic that doesn't fit standard workflow agents, inherit directly from `BaseAgent`.

### 5.1 When to Use Custom Agents

*   **Complex Conditional Logic**: `if/else` branching based on multiple state variables.
*   **Dynamic Agent Selection**: Choosing which sub-agent to run based on runtime evaluation.
*   **Direct External Integrations**: Calling external APIs or libraries directly within the orchestration flow.
*   **Custom Loop/Retry Logic**: More sophisticated iteration patterns than `LoopAgent`, such as the `EscalationChecker` example.

### 5.2 Implementing `_run_async_impl`

This is the core asynchronous method you must override.

#### **Example: A Custom Agent for Loop Control**
This agent reads state, applies simple Python logic, and yields an `Event` with an `escalate` action to control a `LoopAgent`.

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator
import logging

class EscalationChecker(BaseAgent):
    """Checks research evaluation and escalates to stop the loop if grade is 'pass'."""

    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 1. Read from session state.
        evaluation_result = ctx.session.state.get("research_evaluation")

        # 2. Apply custom Python logic.
        if evaluation_result and evaluation_result.get("grade") == "pass":
            logging.info(
                f"[{self.name}] Research passed. Escalating to stop loop."
            )
            # 3. Yield an Event with a control Action.
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(
                f"[{self.name}] Research failed or not found. Loop continues."
            )
            # Yielding an event without actions lets the flow continue.
            yield Event(author=self.name)
```
*   **Asynchronous Generator**: `async def ... yield Event`. This allows pausing and resuming execution.
*   **`ctx: InvocationContext`**: Provides access to all session state (`ctx.session.state`).
*   **Calling Sub-Agents**: Use `async for event in self.sub_agent_instance.run_async(ctx): yield event`.
*   **Control Flow**: Use standard Python `if/else`, `for/while` loops for complex logic.

---

## 6. Models: Gemini, LiteLLM, and Vertex AI

ADK's model flexibility allows integrating various LLMs for different needs.

### 6.1 Google Gemini Models (AI Studio & Vertex AI)

*   **Default Integration**: Native support via `google-genai` library.
*   **AI Studio (Easy Start)**:
    *   Set `GOOGLE_API_KEY="YOUR_API_KEY"` (environment variable).
    *   Set `GOOGLE_GENAI_USE_VERTEXAI="False"`.
    *   Model strings: `"gemini-3-flash-preview"`, `"gemini-3-pro-preview"`, etc.
*   **Vertex AI (Production)**:
    *   Authenticate via `gcloud auth application-default login` (recommended).
    *   Set `GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`, `GOOGLE_CLOUD_LOCATION="your-region"` (environment variables).
    *   Set `GOOGLE_GENAI_USE_VERTEXAI="True"`.
    *   Model strings: `"gemini-3-flash-preview"`, `"gemini-3-pro-preview"`, or full Vertex AI endpoint resource names for specific deployments.

### 6.2 Other Cloud & Proprietary Models via LiteLLM

`LiteLlm` provides a unified interface to 100+ LLMs (OpenAI, Anthropic, Cohere, etc.).

*   **Installation**: `pip install litellm`
*   **API Keys**: Set environment variables as required by LiteLLM (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
*   **Usage**:
    ```python
    from google.adk.models.lite_llm import LiteLlm
    agent_openai = Agent(model=LiteLlm(model="openai/gpt-4o"), ...)
    agent_claude = Agent(model=LiteLlm(model="anthropic/claude-3-haiku-20240307"), ...)
    ```

### 6.3 Open & Local Models via LiteLLM (Ollama, vLLM)

For self-hosting, cost savings, privacy, or offline use.

*   **Ollama Integration**: Run Ollama locally (`ollama run <model>`).
    ```bash
    export OLLAMA_API_BASE="http://localhost:11434" # Ensure Ollama server is running
    ```
    ```python
    from google.adk.models.lite_llm import LiteLlm
    # Use 'ollama_chat' provider for tool-calling capabilities with Ollama models
    agent_ollama = Agent(model=LiteLlm(model="ollama_chat/llama3:instruct"), ...)
    ```

*   **Self-Hosted Endpoint (e.g., vLLM)**:
    ```python
    from google.adk.models.lite_llm import LiteLlm
    api_base_url = "https://your-vllm-endpoint.example.com/v1"
    agent_vllm = Agent(
        model=LiteLlm(
            model="your-model-name-on-vllm",
            api_base=api_base_url,
            extra_headers={"Authorization": "Bearer YOUR_TOKEN"},
        ),
        ...
    )
    ```

### 6.4 Customizing LLM API Clients

For `google-genai` (used by Gemini models), you can configure the underlying client.

```python
import os
from google.genai import configure as genai_configure

genai_configure.use_defaults(
    timeout=60, # seconds
    client_options={"api_key": os.getenv("GOOGLE_API_KEY")},
)
```

---

## 7. Tools: The Agent's Capabilities

Tools extend an agent's abilities beyond text generation.

### 7.1 Defining Function Tools: Principles & Best Practices

*   **Signature**: `def my_tool(param1: Type, param2: Type, tool_context: ToolContext) -> dict:`
*   **Function Name**: Descriptive verb-noun (e.g., `schedule_meeting`).
*   **Parameters**: Clear names, required type hints, **NO DEFAULT VALUES**.
*   **Return Type**: **Must** be a `dict` (JSON-serializable), preferably with a `'status'` key.
*   **Docstring**: **CRITICAL**. Explain purpose, when to use, arguments, and return value structure. **AVOID** mentioning `tool_context`.

    ```python
    def calculate_compound_interest(
        principal: float,
        rate: float,
        years: int,
        compounding_frequency: int,
        tool_context: ToolContext
    ) -> dict:
        """Calculates the future value of an investment with compound interest.

        Use this tool to calculate the future value of an investment given a
        principal amount, interest rate, number of years, and how often the
        interest is compounded per year.

        Args:
            principal (float): The initial amount of money invested.
            rate (float): The annual interest rate (e.g., 0.05 for 5%).
            years (int): The number of years the money is invested.
            compounding_frequency (int): The number of times interest is compounded
                                         per year (e.g., 1 for annually, 12 for monthly).
            
        Returns:
            dict: Contains the calculation result.
                  - 'status' (str): "success" or "error".
                  - 'future_value' (float, optional): The calculated future value.
                  - 'error_message' (str, optional): Description of error, if any.
        """
        # ... implementation ...
    ```

### 7.2 The `ToolContext` Object: Accessing Runtime Information

`ToolContext` is the gateway for tools to interact with the ADK runtime.

*   `tool_context.state`: Read and write to the current `Session`'s `state` dictionary.
*   `tool_context.actions`: Modify the `EventActions` object (e.g., `tool_context.actions.escalate = True`).
*   `tool_context.load_artifact(filename)` / `tool_context.save_artifact(filename, part)`: Manage binary data.
*   `tool_context.search_memory(query)`: Query the long-term `MemoryService`.

### 7.3 All Tool Types & Their Usage

1.  **Custom Function Tools**:
    *   **`FunctionTool`**: The most common type, wrapping a standard Python function.
    *   **`LongRunningFunctionTool`**: Wraps an `async` function that `yields` intermediate results, for tasks that provide progress updates.
    *   **`AgentTool`**: Wraps another `BaseAgent` instance, allowing it to be invoked as a tool by a parent agent.

2.  **Built-in Tools**: Ready-to-use tools provided by ADK.
    *   `google_search`: Provides Google Search grounding.
    *   **Code Execution**:
        *   `BuiltInCodeExecutor`: Local, convenient for development. **Not** for untrusted production use.
        *   `GkeCodeExecutor`: Production-grade. Executes code in ephemeral, sandboxed pods on Google Kubernetes Engine (GKE) using gVisor for isolation. Requires GKE cluster setup.
    *   `VertexAiSearchTool`: Provides grounding from your private Vertex AI Search data stores.
    *   `BigQueryToolset`: A collection of tools for interacting with BigQuery (e.g., `list_datasets`, `execute_sql`).
    > **Warning**: An agent can only use one type of built-in tool at a time and they cannot be used in sub-agents.

3.  **Third-Party Tool Wrappers**: For seamless integration with other frameworks.
    *   `LangchainTool`: Wraps a tool from the LangChain ecosystem.

4.  **OpenAPI & Protocol Tools**: For interacting with APIs and services.
    *   **`OpenAPIToolset`**: Automatically generates a set of `RestApiTool`s from an OpenAPI (Swagger) v3 specification.
    *   **`MCPToolset`**: Connects to an external Model Context Protocol (MCP) server to dynamically load its tools.

5.  **Google Cloud Tools**: For deep integration with Google Cloud services.
    *   **`ApiHubToolset`**: Turns any documented API from Apigee API Hub into a tool.
    *   **`ApplicationIntegrationToolset`**: Turns Application Integration workflows and Integration Connectors (e.g., Salesforce, SAP) into callable tools.
    *   **Toolbox for Databases**: An open-source MCP server that ADK can connect to for database interactions.

6.  **Dynamic Toolsets (`BaseToolset`)**: Instead of a static list of tools, use a `Toolset` to dynamically determine which tools an agent can use based on the current context (e.g., user permissions).
    ```python
    from google.adk.tools.base_toolset import BaseToolset

    class AdminAwareToolset(BaseToolset):
        async def get_tools(self, context: ReadonlyContext) -> list[BaseTool]:
            # Check state to see if user is admin
            if context.state.get('user:role') == 'admin':
                 return [admin_delete_tool, standard_query_tool]
            return [standard_query_tool]

    # Usage:
    agent = Agent(tools=[AdminAwareToolset()])
    ```

### 7.4 Tool Confirmation (Human-in-the-Loop)
ADK can pause tool execution to request human or system confirmation before proceeding, essential for sensitive actions.

*   **Boolean Confirmation**: Simple yes/no via `FunctionTool(..., require_confirmation=True)`.
*   **Dynamic Confirmation**: Pass a function to `require_confirmation` to decide at runtime based on arguments.
*   **Advanced/Payload Confirmation**: Use `tool_context.request_confirmation()` inside the tool for structured feedback.

```python
from google.adk.tools import FunctionTool, ToolContext

# 1. Simple Boolean Confirmation
# Pauses execution until a 'confirmed': True/False event is received.
sensitive_tool = FunctionTool(delete_database, require_confirmation=True)

# 2. Dynamic Threshold Confirmation
def needs_approval(amount: float, **kwargs) -> bool:
    return amount > 10000

transfer_tool = FunctionTool(wire_money, require_confirmation=needs_approval)

# 3. Advanced Payload Confirmation (inside tool definition)
def book_flight(destination: str, price: float, tool_context: ToolContext):
    # Pause and ask user to select a seat class before continuing
    tool_context.request_confirmation(
        hint="Please confirm booking and select seat class.",
        payload={"seat_class": ["economy", "business", "first"]} # Expected structure
    )
    return {"status": "pending_confirmation"}
```

---

## 8. Context, State, and Memory Management

Effective context management is crucial for coherent, multi-turn conversations.

### 8.1 The `Session` Object & `SessionService`

*   **`Session`**: The container for a single, ongoing conversation (`id`, `state`, `events`).
*   **`SessionService`**: Manages the lifecycle of `Session` objects (`create_session`, `get_session`, `append_event`).
*   **Implementations**: `InMemorySessionService` (dev), `VertexAiSessionService` (prod), `DatabaseSessionService` (self-managed).

### 8.2 `State`: The Conversational Scratchpad

A mutable dictionary within `session.state` for short-term, dynamic data.

*   **Update Mechanism**: Always update via `context.state` (in callbacks/tools) or `LlmAgent.output_key`.
*   **Prefixes for Scope**:
    *   **(No prefix)**: Session-specific (e.g., `session.state['booking_step']`).
    *   `user:`: Persistent for a `user_id` across all their sessions (e.g., `session.state['user:preferred_currency']`).
    *   `app:`: Persistent for `app_name` across all users and sessions.
    *   `temp:`: Ephemeral state that only exists for the current **invocation** (one user request -> final agent response cycle). It is discarded afterwards.

### 8.3 `Memory`: Long-Term Knowledge & Retrieval

For knowledge beyond a single conversation.

*   **`BaseMemoryService`**: Defines the interface (`add_session_to_memory`, `search_memory`).
*   **Implementations**: `InMemoryMemoryService`, `VertexAiRagMemoryService`.
*   **Usage**: Agents interact via tools (e.g., the built-in `load_memory` tool).

### 8.4 `Artifacts`: Binary Data Management

For named, versioned binary data (files, images).

*   **Representation**: `google.genai.types.Part` (containing a `Blob` with `data: bytes` and `mime_type: str`).
*   **`BaseArtifactService`**: Manages storage (`save_artifact`, `load_artifact`).
*   **Implementations**: `InMemoryArtifactService`, `GcsArtifactService`.

---

## 9. Runtime, Events, and Execution Flow

The `Runner` is the central orchestrator of an ADK application.

### 9.1 Runtime Configuration (`RunConfig`)
Passed to `run` or `run_live` to control execution limits and output formats.

```python
from google.adk.agents.run_config import RunConfig
from google.genai import types

config = RunConfig(
    # Safety limits
    max_llm_calls=100,  # Prevent infinite agent loops
    
    # Streaming & Modality
    response_modalities=["AUDIO", "TEXT"], # Request specific output formats
    
    # Voice configuration (for AUDIO modality)
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    ),
    
    # Debugging
    save_input_blobs_as_artifacts=True # Save uploaded files to ArtifactService
)
```

### 9.2 The `Runner`: The Orchestrator

*   **Role**: Manages the agent's lifecycle, the event loop, and coordinates with services.
*   **Entry Point**: `runner.run_async(user_id, session_id, new_message)`.

### 9.3 The Event Loop: Core Execution Flow

1.  User input becomes a `user` `Event`.
2.  `Runner` calls `agent.run_async(invocation_context)`.
3.  Agent `yield`s an `Event` (e.g., tool call, text response). Execution pauses.
4.  `Runner` processes the `Event` (applies state changes, etc.) and yields it to the client.
5.  Execution resumes. This cycle repeats until the agent is done.

### 9.4 `Event` Object: The Communication Backbone

`Event` objects carry all information and signals.

*   `Event.author`: Source of the event (`'user'`, agent name, `'system'`).
*   `Event.content`: The primary payload (text, function calls, function responses).
*   `Event.actions`: Signals side effects (`state_delta`, `transfer_to_agent`, `escalate`).
*   `Event.is_final_response()`: Helper to identify the complete, displayable message.

### 9.5 Asynchronous Programming (Python Specific)

ADK is built on `asyncio`. Use `async def`, `await`, and `async for` for all I/O-bound operations.

---

## 10. Control Flow with Callbacks

Callbacks are functions that intercept and control agent execution at specific points.

### 10.1 Callback Mechanism: Interception & Control

*   **Definition**: A Python function assigned to an agent's `callback` parameter (e.g., `after_agent_callback=my_func`).
*   **Context**: Receives a `CallbackContext` (or `ToolContext`) with runtime info.
*   **Return Value**: **Crucially determines flow.**
    *   `return None`: Allow the default action to proceed.
    *   `return <Specific Object>`: **Override** the default action/result.

### 10.2 Types of Callbacks

1.  **Agent Lifecycle**: `before_agent_callback`, `after_agent_callback`.
2.  **LLM Interaction**: `before_model_callback`, `after_model_callback`.
3.  **Tool Execution**: `before_tool_callback`, `after_tool_callback`.

### 10.3 Callback Best Practices

*   **Keep Focused**: Each callback for a single purpose.
*   **Performance**: Avoid blocking I/O or heavy computation.
*   **Error Handling**: Use `try...except` to prevent crashes.

#### **Example 1: Data Aggregation with `after_agent_callback`**
This callback runs after an agent, inspects the `session.events` to find structured data from tool calls (like `google_search` results), and saves it to state for later use.

```python
from google.adk.agents.callback_context import CallbackContext

def collect_research_sources_callback(callback_context: CallbackContext) -> None:
    """Collects and organizes web research sources from agent events."""
    session = callback_context._invocation_context.session
    # Get existing sources from state to append to them.
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1

    # Iterate through all events in the session to find grounding metadata.
    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue
        # ... logic to parse grounding_chunks and grounding_supports ...
        # (See full implementation in the original code snippet)

    # Save the updated source map back to state.
    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources

# Used in an agent like this:
# section_researcher = LlmAgent(..., after_agent_callback=collect_research_sources_callback)
```

#### **Example 2: Output Transformation with `after_agent_callback`**
This callback takes an LLM's raw output (containing custom tags), uses Python to format it into markdown, and returns the modified content, overriding the original.

```python
import re
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types

def citation_replacement_callback(callback_context: CallbackContext) -> genai_types.Content:
    """Replaces <cite> tags in a report with Markdown-formatted links."""
    # 1. Get raw report and sources from state.
    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    # 2. Define a replacer function for regex substitution.
    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            return "" # Remove invalid tags
        title = source_info.get("title", short_id)
        return f" [{title}]({source_info['url']})"

    # 3. Use regex to find all <cite> tags and replace them.
    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?(src-\d+)["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report) # Fix spacing

    # 4. Save the new version to state and return it to override the original agent output.
    callback_context.state["final_report_with_citations"] = processed_report
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])

# Used in an agent like this:
# report_composer = LlmAgent(..., after_agent_callback=citation_replacement_callback)
```

### 10.A. Global Control with Plugins

Plugins are stateful, reusable modules for implementing cross-cutting concerns that apply globally to all agents, tools, and model calls managed by a `Runner`. Unlike Callbacks which are configured per-agent, Plugins are registered once on the `Runner`.

*   **Use Cases**: Ideal for universal logging, application-wide policy enforcement, global caching, and collecting metrics.
*   **Execution Order**: Plugin callbacks run **before** their corresponding agent-level callbacks. If a plugin callback returns a value, the agent-level callback is skipped.
*   **Defining a Plugin**: Inherit from `BasePlugin` and implement callback methods.
    ```python
    from google.adk.plugins import BasePlugin
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest

    class AuditLoggingPlugin(BasePlugin):
        def __init__(self):
            super().__init__(name="audit_logger")

        async def before_model_callback(self, callback_context: CallbackContext, llm_request: LlmRequest):
            # Log every prompt sent to any LLM
            print(f"[AUDIT] Agent {callback_context.agent_name} calling LLM with: {llm_request.contents[-1]}")

        async def on_tool_error_callback(self, tool, error, **kwargs):
            # Global error handler for all tools
            print(f"[ALERT] Tool {tool.name} failed: {error}")
            # Optionally return a dict to suppress the exception and provide fallback
            return {"status": "error", "message": "An internal error occurred, handled by plugin."}
    ```
*   **Registering a Plugin**:
    ```python
    from google.adk.runners import Runner
    # runner = Runner(agent=root_agent, ..., plugins=[AuditLoggingPlugin()])
    ```
*   **Error Handling Callbacks**: Plugins support unique error hooks like `on_model_error_callback` and `on_tool_error_callback` for centralized error management.
*   **Limitation**: Plugins are not supported by the `adk web` interface.

---

## 11. Authentication for Tools

Enabling agents to securely access protected external resources.

### 11.1 Core Concepts: `AuthScheme` & `AuthCredential`

*   **`AuthScheme`**: Defines *how* an API expects authentication (e.g., `APIKey`, `HTTPBearer`, `OAuth2`, `OpenIdConnectWithConfig`).
*   **`AuthCredential`**: Holds *initial* information to *start* the auth process (e.g., API key value, OAuth client ID/secret).

### 11.2 Interactive OAuth/OIDC Flows

When a tool requires user interaction (OAuth consent), ADK pauses and signals your `Agent Client` application.

1.  **Detect Auth Request**: `runner.run_async()` yields an event with a special `adk_request_credential` function call.
2.  **Redirect User**: Extract `auth_uri` from `auth_config` in the event. Your client app redirects the user's browser to this `auth_uri` (appending `redirect_uri`).
3.  **Handle Callback**: Your client app has a pre-registered `redirect_uri` to receive the user after authorization. It captures the full callback URL (containing `authorization_code`).
4.  **Send Auth Result to ADK**: Your client prepares a `FunctionResponse` for `adk_request_credential`, setting `auth_config.exchanged_auth_credential.oauth2.auth_response_uri` to the captured callback URL.
5.  **Resume Execution**: `runner.run_async()` is called again with this `FunctionResponse`. ADK performs the token exchange, stores the access token, and retries the original tool call.

### 11.3 Custom Tool Authentication

If building a `FunctionTool` that needs authentication:

1.  **Check for Cached Creds**: `tool_context.state.get("my_token_cache_key")`.
2.  **Check for Auth Response**: `tool_context.get_auth_response(my_auth_config)`.
3.  **Initiate Auth**: If no creds, call `tool_context.request_credential(my_auth_config)` and return a pending status. This triggers the external flow.
4.  **Cache Credentials**: After obtaining, store in `tool_context.state`.
5.  **Make API Call**: Use the valid credentials (e.g., `google.oauth2.credentials.Credentials`).

---

## 12. Deployment Strategies

From local dev to production.

### 12.1 Local Development & Testing (`adk web`, `adk run`, `adk api_server`)

*   **`adk web`**: Launches a local web UI for interactive chat, session inspection, and visual tracing.
    ```bash
    adk web /path/to/your/project_root
    ```
*   **`adk run`**: Command-line interactive chat.
    ```bash
    adk run /path/to/your/agent_folder
    ```
*   **`adk api_server`**: Launches a local FastAPI server exposing `/run`, `/run_sse`, `/list-apps`, etc., for API testing with `curl` or client libraries.
    ```bash
    adk api_server /path/to/your/project_root
    ```

### 12.2 Vertex AI Agent Engine

Fully managed, scalable service for ADK agents on Google Cloud.

*   **Features**: Auto-scaling, session management, observability integration.
*   **ADK CLI**: `adk deploy agent_engine --project <id> --region <loc> ... /path/to/agent`
*   **Deployment**: Use `vertexai.agent_engines.create()`.
    ```python
    from vertexai.preview import reasoning_engines # or agent_engines directly in later versions
    
    # Wrap your root_agent for deployment
    app_for_engine = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    
    # Deploy
    remote_app = agent_engines.create(
        agent_engine=app_for_engine,
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        display_name="My Production Agent"
    )
    print(remote_app.resource_name) # projects/PROJECT_NUM/locations/REGION/reasoningEngines/ID
    ```
*   **Interaction**: Use `remote_app.stream_query()`, `create_session()`, etc.

### 12.3 Cloud Run

Serverless container platform for custom web applications.

*   **ADK CLI**: `adk deploy cloud_run --project <id> --region <loc> ... /path/to/agent`
*   **Deployment**:
    1.  Create a `Dockerfile` for your FastAPI app (using `google.adk.cli.fast_api.get_fast_api_app`).
    2.  Use `gcloud run deploy --source .`.
    3.  Alternatively, `adk deploy cloud_run` (simpler, opinionated).
*   **Example `main.py`**:
    ```python
    import os
    from fastapi import FastAPI
    from google.adk.cli.fast_api import get_fast_api_app

    # Ensure your agent_folder (e.g., 'my_first_agent') is in the same directory as main.py
    app: FastAPI = get_fast_api_app(
        agents_dir=os.path.dirname(os.path.abspath(__file__)),
        session_service_uri="sqlite:///./sessions.db", # In-container SQLite, for simple cases
        # For production: use a persistent DB (Cloud SQL) or VertexAiSessionService
        allow_origins=["*"],
        web=True # Serve ADK UI
    )
    # uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) # If running directly
    ```

### 12.4 Google Kubernetes Engine (GKE)

For maximum control, run your containerized agent in a Kubernetes cluster.

*   **ADK CLI**: `adk deploy gke --project <id> --cluster_name <name> ... /path/to/agent`
*   **Deployment**:
    1.  Build Docker image (`gcloud builds submit`).
    2.  Create Kubernetes Deployment and Service YAMLs.
    3.  Apply with `kubectl apply -f deployment.yaml`.
    4.  Configure Workload Identity for GCP permissions.

### 12.5 CI/CD Integration

*   Automate testing (`pytest`, `adk eval`) in CI.
*   Automate container builds and deployments (e.g., Cloud Build, GitHub Actions).
*   Use environment variables for secrets.

---

## 13. Evaluation and Safety

Critical for robust, production-ready agents.

### 13.1 Agent Evaluation (`adk eval`)

Systematically assess agent performance using predefined test cases.

*   **Evalset File (`.evalset.json`)**: Contains `eval_cases`, each with a `conversation` (user queries, expected tool calls, expected intermediate/final responses) and `session_input` (initial state).
    ```json
    {
      "eval_set_id": "weather_bot_eval",
      "eval_cases": [
        {
          "eval_id": "london_weather_query",
          "conversation": [
            {
              "user_content": {"parts": [{"text": "What's the weather in London?"}]},
              "final_response": {"parts": [{"text": "The weather in London is cloudy..."}]},
              "intermediate_data": {
                "tool_uses": [{"name": "get_weather", "args": {"city": "London"}}]
              }
            }
          ],
          "session_input": {"app_name": "weather_app", "user_id": "test_user", "state": {}}
        }
      ]
    }
    ```
*   **Running Evaluation**:
    *   `adk web`: Interactive UI for creating/running eval cases.
    *   `adk eval /path/to/agent_folder /path/to/evalset.json`: CLI execution.
    *   `pytest`: Integrate `AgentEvaluator.evaluate()` into unit/integration tests.
*   **Metrics**: `tool_trajectory_avg_score` (tool calls match expected), `response_match_score` (final response similarity using ROUGE). Configurable via `test_config.json`.

### 13.2 Safety & Guardrails

Multi-layered defense against harmful content, misalignment, and unsafe actions.

1.  **Identity and Authorization**:
    *   **Agent-Auth**: Tool acts with the agent's service account (e.g., `Vertex AI User` role). Simple, but all users share access level. Logs needed for attribution.
    *   **User-Auth**: Tool acts with the end-user's identity (via OAuth tokens). Reduces risk of abuse.
2.  **In-Tool Guardrails**: Design tools defensively. Tools can read policies from `tool_context.state` (set deterministically by developer) and validate model-provided arguments before execution.
    ```python
    def execute_sql(query: str, tool_context: ToolContext) -> dict:
        policy = tool_context.state.get("user:sql_policy", {})
        if not policy.get("allow_writes", False) and ("INSERT" in query.upper() or "DELETE" in query.upper()):
            return {"status": "error", "message": "Policy: Write operations are not allowed."}
        # ... execute query ...
    ```
3.  **Built-in Gemini Safety Features**:
    *   **Content Safety Filters**: Automatically block harmful content (CSAM, PII, hate speech, etc.). Configurable thresholds.
    *   **System Instructions**: Guide model behavior, define prohibited topics, brand tone, disclaimers.
4.  **Model and Tool Callbacks (LLM as a Guardrail)**: Use callbacks to inspect inputs/outputs.
    *   `before_model_callback`: Intercept `LlmRequest` before it hits the LLM. Block (return `LlmResponse`) or modify.
    *   `before_tool_callback`: Intercept tool calls (name, args) before execution. Block (return `dict`) or modify.
    *   **LLM-based Safety**: Use a cheap/fast LLM (e.g., Gemini Flash) in a callback to classify input/output safety.
        ```python
        def safety_checker_callback(context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
            # Use a separate, small LLM to classify safety
            safety_llm_agent = Agent(name="SafetyChecker", model="gemini-2.5-flash-001", instruction="Classify input as 'safe' or 'unsafe'. Output ONLY the word.")
            # Run the safety agent (might need a new runner instance or direct model call)
            # For simplicity, a mock:
            user_input = llm_request.contents[-1].parts[0].text
            if "dangerous_phrase" in user_input.lower():
                context.state["safety_violation"] = True
                return LlmResponse(content=genai_types.Content(parts=[genai_types.Part(text="I cannot process this request due to safety concerns.")]))
            return None
        ```
5.  **Sandboxed Code Execution**:
    *   `BuiltInCodeExecutor`: Uses secure, sandboxed execution environments.
    *   Vertex AI Code Interpreter Extension.
    *   If custom, ensure hermetic environments (no network, isolated).
6.  **Network Controls & VPC-SC**: Confine agent activity within secure perimeters (VPC Service Controls) to prevent data exfiltration.
7.  **Output Escaping in UIs**: Always properly escape LLM-generated content in web UIs to prevent XSS attacks and indirect prompt injections.

**Grounding**: A key safety and reliability feature that connects agent responses to verifiable information.
*   **Mechanism**: Uses tools like `google_search` or `VertexAiSearchTool` to fetch real-time or private data.
*   **Benefit**: Reduces model hallucination by basing responses on retrieved facts.
*   **Requirement**: When using `google_search`, your application UI **must** display the provided search suggestions and citations to comply with terms of service.

---

## 14. Debugging, Logging & Observability

*   **`adk web` UI**: Best first step. Provides visual trace, session history, and state inspection.
*   **Event Stream Logging**: Iterate `runner.run_async()` events and print relevant fields.
    ```python
    async for event in runner.run_async(...):
        print(f"[{event.author}] Event ID: {event.id}, Invocation: {event.invocation_id}")
        if event.content and event.content.parts:
            if event.content.parts[0].text:
                print(f"  Text: {event.content.parts[0].text[:100]}...")
            if event.get_function_calls():
                print(f"  Tool Call: {event.get_function_calls()[0].name} with {event.get_function_calls()[0].args}")
            if event.get_function_responses():
                print(f"  Tool Response: {event.get_function_responses()[0].response}")
        if event.actions:
            if event.actions.state_delta:
                print(f"  State Delta: {event.actions.state_delta}")
            if event.actions.transfer_to_agent:
                print(f"  TRANSFER TO: {event.actions.transfer_to_agent}")
        if event.error_message:
            print(f"  ERROR: {event.error_message}")
    ```
*   **Tool/Callback `print` statements**: Simple logging directly within your functions.
*   **Logging**: Use Python's standard `logging` module. Control verbosity with `adk web --log_level DEBUG` or `adk web -v`.
*   **One-Line Observability Integrations**: ADK has native hooks for popular tracing platforms.
    *   **AgentOps**:
        ```python
        import agentops
        agentops.init(api_key="...") # Automatically instruments ADK agents
        ```
    *   **Arize Phoenix**:
        ```python
        from phoenix.otel import register
        register(project_name="my_agent", auto_instrument=True)
        ```
    *   **Google Cloud Trace**: Enable via flag during deployment: `adk deploy [cloud_run|agent_engine] --trace_to_cloud ...`
*   **Session History (`session.events`)**: Persisted for detailed post-mortem analysis.

---

## 15. Streaming & Advanced I/O

ADK supports real-time, bidirectional communication for interactive experiences like live voice conversations.

#### Bidirectional Streaming Loop (`run_live`)
For real-time voice/video, use `run_live` with a `LiveRequestQueue`. This enables low-latency, two-way communication where the user can interrupt the agent.

```python
import asyncio
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

async def start_streaming_session(runner, session, user_id):
    # 1. Configure modalities (e.g., AUDIO output for voice agents)
    run_config = RunConfig(response_modalities=["AUDIO"])
    
    # 2. Create input queue for client data (audio chunks, text)
    live_queue = LiveRequestQueue()

    # 3. Start the bidirectional stream
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_queue,
        run_config=run_config
    )

    # 4. Process events (simplified loop)
    try:
        async for event in live_events:
            # Handle agent output (text or audio bytes)
            if event.content and event.content.parts:
                part = event.content.parts[0]
                if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                    # Send audio bytes to client
                    await client.send_audio(part.inline_data.data)
                elif part.text:
                     # Send text to client
                     await client.send_text(part.text)
            
            # Handle turn signals
            if event.turn_complete:
                 pass # Signal client that agent finished speaking
    finally:
        live_queue.close()

# To send user input to agent during the stream:
# await live_queue.send_content(Content(role="user", parts=[Part(text="Hello")]))
# await live_queue.send_realtime(Blob(mime_type="audio/pcm", data=audio_bytes))
```

*   **Streaming Tools**: A special type of `FunctionTool` that can stream intermediate results back to the agent.
    *   **Definition**: Must be an `async` function with a return type of `AsyncGenerator`.
        ```python
        from typing import AsyncGenerator

        async def monitor_stock_price(symbol: str) -> AsyncGenerator[str, None]:
            """Yields stock price updates as they occur."""
            while True:
                price = await get_live_price(symbol)
                yield f"Update for {symbol}: ${price}"
                await asyncio.sleep(5)
        ```

*   **Advanced I/O Modalities**: ADK (especially with Gemini Live API models) supports richer interactions.
    *   **Audio**: Input via `Blob(mime_type="audio/pcm", data=bytes)`, Output via `genai_types.SpeechConfig` in `RunConfig`.
    *   **Vision (Images/Video)**: Input via `Blob(mime_type="image/jpeg", data=bytes)` or `Blob(mime_type="video/mp4", data=bytes)`. Models like `gemini-2.5-flash-exp` can process these.
    *   **Multimodal Input in `Content`**:
        ```python
        multimodal_content = genai_types.Content(
            parts=[
                genai_types.Part(text="Describe this image:"),
                genai_types.Part(inline_data=genai_types.Blob(mime_type="image/jpeg", data=image_bytes))
            ]
        )
        ```

---

## 16. Performance Optimization

*   **Model Selection**: Choose the smallest model that meets requirements (e.g., `gemini-2.5-flash` for simple tasks).
*   **Instruction Prompt Engineering**: Concise, clear instructions reduce tokens and improve accuracy.
*   **Tool Use Optimization**:
    *   Design efficient tools (fast API calls, optimize database queries).
    *   Cache tool results (e.g., using `before_tool_callback` or `tool_context.state`).
*   **State Management**: Store only necessary data in state to avoid large context windows.
*   **`include_contents='none'`**: For stateless utility agents, saves LLM context window.
*   **Parallelization**: Use `ParallelAgent` for independent tasks.
*   **Streaming**: Use `StreamingMode.SSE` or `BIDI` for perceived latency reduction.
*   **`max_llm_calls`**: Limit LLM calls to prevent runaway agents and control costs.

---

## 17. General Best Practices & Common Pitfalls

*   **Start Simple**: Begin with `LlmAgent`, mock tools, and `InMemorySessionService`. Gradually add complexity.
*   **Iterative Development**: Build small features, test, debug, refine.
*   **Modular Design**: Use agents and tools to encapsulate logic.
*   **Clear Naming**: Descriptive names for agents, tools, state keys.
*   **Error Handling**: Implement robust `try...except` blocks in tools and callbacks. Guide LLMs on how to handle tool errors.
*   **Testing**: Write unit tests for tools/callbacks, integration tests for agent flows (`pytest`, `adk eval`).
*   **Dependency Management**: Use virtual environments (`venv`) and `requirements.txt`.
*   **Secrets Management**: Never hardcode API keys. Use `.env` for local dev, environment variables or secret managers (Google Cloud Secret Manager) for production.
*   **Avoid Infinite Loops**: Especially with `LoopAgent` or complex LLM tool-calling chains. Use `max_iterations`, `max_llm_calls`, and strong instructions.
*   **Handle `None` & `Optional`**: Always check for `None` or `Optional` values when accessing nested properties (e.g., `event.content and event.content.parts and event.content.parts[0].text`).
*   **Immutability of Events**: Events are immutable records. If you need to change something *before* it's processed, do so in a `before_*` callback and return a *new* modified object.
*   **Understand `output_key` vs. direct `state` writes**: `output_key` is for the agent's *final conversational* output. Direct `tool_context.state['key'] = value` is for *any other* data you want to save.
*   **Example Agents**: Find practical examples and reference implementations in the [ADK Samples repository](https://github.com/google/adk-samples).


### Testing the output of an agent

The following script demonstrates how to programmatically test an agent's output. This approach is extremely useful when an LLM or coding agent needs to interact with a work-in-progress agent, as well as for automated testing, debugging, or when you need to integrate agent execution into other workflows:
```python
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agent import root_agent
from google.genai import types as genai_types


async def main():
    """Runs the agent with a sample query."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )
    query = "I want a recipe for pancakes"
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user", 
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 18. Official API & CLI References

For detailed specifications of all classes, methods, and commands, refer to the official reference documentation.

*   [Python API Reference](https://github.com/google/adk-docs/tree/main/docs/api-reference/python)
*   [Java API Reference](https://github.com/google/adk-docs/tree/main/docs/api-reference/java)
*   [CLI Reference](https://github.com/google/adk-docs/tree/main/docs/api-reference/cli)
*   [REST API Reference](https://github.com/google/adk-docs/tree/main/docs/api-reference/rest)
*   [Agent Config YAML Reference](https://github.com/google/adk-docs/tree/main/docs/api-reference/agentconfig)

---
**llm.txt** documents the "Agent Starter Pack" repository, providing a source of truth on its purpose, features, and usage.
---

### Section 1: Project Overview

*   **Project Name:** Agent Starter Pack
*   **Purpose:** Accelerate development of production-ready GenAI Agents on Google Cloud.
*   **Tagline:** Production-Ready Agents on Google Cloud, faster.

**The "Production Gap":**
While prototyping GenAI agents is quick, production deployment often takes 3-9 months.

**Key Challenges Addressed:**
*   **Customization:** Business logic, data grounding, security/compliance.
*   **Evaluation:** Metrics, quality assessment, test datasets.
*   **Deployment:** Cloud infrastructure, CI/CD, UI integration.
*   **Observability:** Performance tracking, user feedback.

**Solution: Agent Starter Pack**
Provides MLOps and infrastructure templates so developers focus on agent logic.

*   **You Build:** Prompts, LLM interactions, business logic, agent orchestration.
*   **We Provide:**
    *   Deployment infrastructure, CI/CD, testing
    *   Logging, monitoring
    *   Evaluation tools
    *   Data connections, UI playground
    *   Security best practices

Establishes production patterns from day one, saving setup time.

---
### Section 2: Creating & Enhancing Agent Projects

Start by creating a new agent project from a predefined template, or enhance an existing project with agent capabilities. Both processes support interactive and fully automated setup.

**Prerequisites:**
Before you begin, ensure you have `uv`/`uvx`, `gcloud` CLI, `terraform`, `git`, and `gh` CLI (for automated CI/CD setup) installed and authenticated.

**Installing the `agent-starter-pack` CLI:**
Choose one method to get the `agent-starter-pack` command:

1.  **`uvx` (Recommended for Zero-Install/Automation):** Run directly without prior installation.
    ```bash
    uvx agent-starter-pack create ...
    ```
2.  **Virtual Environment (`pip` or `uv`):**
    ```bash
    pip install agent-starter-pack
    ```
3.  **Persistent CLI Install (`pipx` or `uv tool`):** Installs globally in an isolated environment.

---
### `agent-starter-pack create` Command

Generates a new agent project directory based on a chosen template and configuration.

**Usage:**
```bash
agent-starter-pack create PROJECT_NAME [OPTIONS]
```

**Arguments:**
*   `PROJECT_NAME`: Name for your new project directory and base for GCP resource naming (max 26 chars, converted to lowercase).

**Template Selection:**
*   `-a, --agent`: Agent template - built-in agents (e.g., `adk_base`, `agentic_rag`), remote templates (`adk@gemini-fullstack`, `github.com/user/repo@branch`), or local projects (`local@./path`).

**Deployment Options:**
*   `-d, --deployment-target`: Target environment (`cloud_run` or `agent_engine`).
*   `--cicd-runner`: CI/CD runner (`google_cloud_build` or `github_actions`).
*   `--region`: GCP region (default: `eu-west1`).

**Data & Storage:**
*   `-i, --include-data-ingestion`: Include data ingestion pipeline.
*   `-ds, --datastore`: Datastore type (`vertex_ai_search`, `vertex_ai_vector_search`, `cloud_sql`).
*   `--session-type`: Session storage (`in_memory`, `cloud_sql`, `agent_engine`).

**Project Creation:**
*   `-o, --output-dir`: Output directory (default: current directory).
*   `--agent-directory, -dir`: Agent code directory name (default: `app`).
*   `--in-folder`: Create files in current directory instead of new subdirectory.

**Automation:**
*   `--auto-approve`: **Skip all interactive prompts (crucial for automation).**
*   `--skip-checks`: Skip GCP/Vertex AI verification checks.
*   `--debug`: Enable debug logging.

**Automated Creation Example:**
```bash
uvx agent-starter-pack create my-automated-agent \
  -a adk_base \
  -d cloud_run \
  --region eu-west1 \
  --auto-approve
```

---

### `agent-starter-pack enhance` Command

Enhance your existing project with AI agent capabilities by adding agent-starter-pack features in-place. This command supports all the same options as `create` but templates directly into the current directory instead of creating a new project directory.

**Usage:**
```bash
agent-starter-pack enhance [TEMPLATE_PATH] [OPTIONS]
```

**Key Differences from `create`:**
*   Templates into current directory (equivalent to `create --in-folder`)
*   `TEMPLATE_PATH` defaults to current directory (`.`)
*   Project name defaults to current directory name
*   Additional `--base-template` option to override template inheritance

**Enhanced Project Example:**
```bash
# Enhance current directory with agent capabilities
uvx agent-starter-pack enhance . \
  --base-template adk_base \
  -d cloud_run \
  --region eu-west1 \
  --auto-approve
```

**Project Structure:** Expects agent code in `app/` directory (configurable via `--agent-directory`).

---

### Available Agent Templates

Templates for the `create` command (via `-a` or `--agent`):

| Agent Name             | Description                                  |
| :--------------------- | :------------------------------------------- |
| `adk_base`             | Base ReAct agent (ADK)                       |
| `adk_gemini_fullstack` | Production-ready fullstack research agent    |
| `agentic_rag`          | RAG agent for document retrieval & Q&A       |
| `langgraph_base`       | Base ReAct agent (LangGraph)                 |
| `adk_live`             | Real-time multimodal RAG agent               |

---

### Including a Data Ingestion Pipeline (for RAG agents)

For RAG agents needing custom document search, enabling this option automates loading, chunking, embedding documents with Vertex AI, and storing them in a vector database.

**How to enable:**
```bash
uvx agent-starter-pack create my-rag-agent \
  -a agentic_rag \
  -d cloud_run \
  -i \
  -ds vertex_ai_search \
  --auto-approve
```
**Post-creation:** Follow your new project's `data_ingestion/README.md` to deploy the necessary infrastructure.

---
### Section 3: Development & Automated Deployment Workflow
---

This section describes the end-to-end lifecycle of an agent, with emphasis on automation.


### 1. Local Development & Iteration

Once your project is created, navigate into its directory to begin development.

**First, install dependencies (run once):**
```bash
make install
```

**Next, test your agent. The recommended method is to use a programmatic script.**

#### Programmatic Testing (Recommended Workflow)

This method allows for quick, automated validation of your agent's logic.

1.  **Create a script:** In the project's root directory, create a Python script named `run_agent.py`.
2.  **Invoke the agent:** In the script, write code to programmatically call your agent with sample input and `print()` the output for inspection.
    *   **Guidance:** If you're unsure or no guidance exists, you can look at files in the `tests/` directory for examples of how to import and call the agent's main function.
    *   **Important:** This script is for simple validation. **Assertions are not required**, and you should not create a formal `pytest` file.
3.  **Run the test:** Execute your script from the terminal using `uv`.
    ```bash
    uv run python run_agent.py
    ```
You can keep the test file for future testing.

#### Manual Testing with the UI Playground (Optional)

If the user needs to interact with your agent manually in a chat interface for debugging:

1.  Run the following command to start the local web UI:
    ```bash
    make playground
    ```
    This is useful for human-in-the-loop testing and features hot-reloading.

### 2. Deploying to a Cloud Development Environment
Before setting up full CI/CD, you can deploy to a personal cloud dev environment.

1.  **Set Project:** `gcloud config set project YOUR_DEV_PROJECT_ID`
2.  **Provision Resources:** `make setup-dev-env` (uses Terraform).
3.  **Deploy Backend:** `make deploy` (builds and deploys the agent).

### 3. Automated Production-Ready Deployment with CI/CD
For reliable deployments, the `setup-cicd` command streamlines the entire process. It creates a GitHub repo, connects it to your chosen CI/CD runner (Google Cloud Build or GitHub Actions), provisions staging/prod infrastructure, and configures deployment triggers.

**Automated CI/CD Setup Example (Recommended):**
```bash
# Run from the project root. This command will guide you or can be automated with flags.
uvx agent-starter-pack setup-cicd
```

**CI/CD Workflow Logic:**
*   **On Pull Request:** CI pipeline runs tests.
*   **On Merge to `main`:** CD pipeline deploys to staging.
*   **Manual Approval:** A manual approval step triggers the production deployment.

---
### Section 4: Key Features & Customization
---

### Deploying with a User Interface (UI)
*   **Unified Deployment (for Dev/Test):** The backend and frontend can be packaged and served from a single Cloud Run service, secured with Identity-Aware Proxy (IAP).
*   **Deploying with UI:** `make deploy IAP=true`
*   **Access Control:** After deploying with IAP, grant users the `IAP-secured Web App User` role in IAM to give them access.

### Session Management

For stateful agents, the starter pack supports persistent sessions.
*   **Cloud Run:** Choose between `in_memory` (for testing) and durable `cloud_sql` sessions using the `--session-type` flag.
*   **Agent Engine:** Provides session management automatically.

### Monitoring & Observability
*   **Technology:** Uses OpenTelemetry to emit events to Google Cloud Trace and Logging.
*   **Custom Tracer:** A custom tracer in `app/utils/tracing.py` (or a different agent directory instead of app) handles large payloads by linking to GCS, overcoming default service limits.
*   **Infrastructure:** A Log Router to sink data to BigQuery is provisioned by Terraform.

---
### Section 5: CLI Reference for CI/CD Setup
---

### `agent-starter-pack setup-cicd`
Automates the complete CI/CD infrastructure setup for GitHub-based deployments. Intelligently detects your CI/CD runner (Google Cloud Build or GitHub Actions) and configures everything automatically.

**Usage:**
```bash
uvx agent-starter-pack setup-cicd [OPTIONS]
```

**Prerequisites:** 
- Run from the project root (directory with `pyproject.toml`)
- Required tools: `gh` CLI (authenticated), `gcloud` CLI (authenticated), `terraform`
- `Owner` role on GCP projects
- GitHub token with `repo` and `workflow` scopes

**Key Options:**
*   `--staging-project`, `--prod-project`: GCP project IDs (will prompt if omitted).
*   `--repository-name`, `--repository-owner`: GitHub repo details (will prompt if omitted).
*   `--cicd-project`: CI/CD resources project (defaults to prod project).
*   `--dev-project`: Development project ID (optional).
*   `--region`: GCP region (default: `eu-west1`).
*   `--auto-approve`: Skip all interactive prompts.
*   `--local-state`: Use local Terraform state instead of GCS backend.
*   `--debug`: Enable debug logging.

**What it does:**
1. Creates/connects GitHub repository
2. Sets up Terraform infrastructure with remote state
3. Configures CI/CD runner connection (Cloud Build or GitHub Actions with WIF)
4. Provisions staging/prod environments
5. Sets up local Git repository with origin remote

**Automated Example:**
```bash
uvx agent-starter-pack setup-cicd \
  --staging-project your-staging-project \
  --prod-project your-prod-project \
  --repository-name your-repo-name \
  --repository-owner your-username \
  --auto-approve
```

**After setup, push to trigger pipeline:**
```bash
git add . && git commit -m "Initial commit" && git push -u origin main
```

* Note: For coding agents - ask user for required project IDs and repo details before running with `--auto-approve`.
* Note: If user prefers different git provider, refer to `deployment/README.md` for manual deployment.
---
### Section 6: Operational Guidelines for Coding Agents

These guidelines are essential for interacting with the Agent Starter Pack project effectively.

---

### Principle 1: Code Preservation & Isolation

When executing code modifications using tools like `replace` or `write_file`, your paramount objective is surgical precision. You **must alter only the code segments directly targeted** by the user's request, while **strictly preserving all surrounding and unrelated code.**

**Mandatory Pre-Execution Verification:**

Before finalizing any `new_string` for a `replace` operation, meticulously verify the following:

1.  **Target Identification:** Clearly define the exact lines or expressions to be changed, based *solely* on the user's explicit instructions.
2.  **Preservation Check:** Compare your proposed `new_string` against the `old_string`. Ensure all code, configuration values (e.g., `model`, `version`, `api_key`), comments, and formatting *outside* the identified target remain identical and verbatim.

**Example: Adhering to Preservation**

*   **User Request:** "Change the agent's instruction to be a recipe suggester."
*   **Original Code Snippet:**
    ```python
    root_agent = Agent(
        name="root_agent",
        model="gemini-3-flash-preview",
        instruction="You are a helpful AI assistant."
    )
    ```
*   **Incorrect Modification (VIOLATION):**
    ```python
    root_agent = Agent(
        name="recipe_suggester",
        model="gemini-1.5-flash", # UNINTENDED MUTATION - model was not requested to change
        instruction="You are a recipe suggester."
    )
    ```
*   **Correct Modification (COMPLIANT):**
    ```python
    root_agent = Agent(
        name="recipe_suggester", # OK, related to new purpose
        model="gemini-3-flash-preview", # MUST be preserved
        instruction="You are a recipe suggester." # OK, the direct target
    )
    ```

**Critical Error:** Failure to adhere to this preservation principle is a critical error. Always prioritize the integrity of existing, unchanged code over the convenience of rewriting entire blocks.

---

### Principle 2: Workflow & Execution Best Practices

*   **Standard Workflow:**
    The validated end-to-end process is: `create` → `test` → `setup-cicd` → push to deploy. Trust this high-level workflow as the default for developing and shipping agents.

*   **Agent Testing:**
    *   **Avoid `make playground`** unless specifically instructed; it is designed for human interaction. Focus on programmatic testing.

*   **Model Selection:**
    *   **When using Gemini, prefer modern model families** for optimal performance and capabilities: "gemini-2.5-pro", "gemini-2.5-flash", and "gemini-3-flash-preview"

*   **Running Python Commands:**
    *   Always use `uv` to execute Python commands within this repository (e.g., `uv run run_agent.py`).
    *   Ensure project dependencies are installed by running `make install` before executing scripts.
    *   Consult the project's `Makefile` and `README.md` for other useful development commands.

*   **Further Reading & Troubleshooting:**
    *   For questions about specific frameworks (e.g., LangGraph) or Google Cloud products (e.g., Cloud Run), their official documentation and online resources are the best source of truth.
    *   **When encountering persistent errors or if you're unsure how to proceed after initial troubleshooting, a targeted Google Search is strongly recommended.** It is often the fastest way to find relevant documentation, community discussions, or direct solutions to your problem.

---


## File: docs/agents/google-adk/KCG_SUMMARY.md

# Google ADK — KCG Summary

## What It Is
A **saoi** (base ReAct agent) scaffolded from Google's Agent Development Kit (ADK) starter pack, supporting the Agent2Agent (A2A) protocol. Includes examples for Firecrawl web research, academic research, deep search, bakery launch workflow, and multi-agent coordination. Built on Google Cloud Platform with Terraform deployment, Cloud Build CI/CD, and Vertex AI integration.

## Why This Matters for Kings' College Galway
Google ADK provides a production-grade multi-agent framework with native A2A protocol support — critical for the oideachais platform's need to coordinate between curriculum-scraping agents, embedding agents, and QA agents. The Firecrawl integration example demonstrates the exact web research pattern needed for scraping examinations.ie and curriculum.ie content. The A2A protocol's inter-agent routing maps directly to the planned micro-agent architecture for lesson plan generation, where specialized agents (history, language, science) must coordinate. The agent-starter-pack scaffolding pattern provides a template for standardizing all Cianfhoghlaim agent deployments with consistent CI/CD, testing, and observability.

## Key Patterns Preserved
- `README.md` — Saoi base ReAct agent: project structure, requirements, quick start, A2A protocol, ADK concepts
- `GEMINI.md` — AI-assisted development guide with project conventions and ADK-specific patterns
- `deployment/README.md` — GCP + Terraform deployment guide for production agent hosting
- `tests/load_test/README.md` — Load testing configuration for agent endpoints
- `examples/firecrawl/README.md` — Firecrawl web scraping agent with tool-use examples and agent teams
- `examples/firecrawl/docs/tool-usage-examples.md` — Concrete Firecrawl MCP tool examples
- `examples/firecrawl/docs/agent-team.md` — Multi-agent team coordination pattern with Firecrawl
- `examples/firecrawl/docs/quickstart-streaming.md` — Streaming response quickstart guide
- `examples/launchmybakery/README.md` — End-to-end bakery business workflow agent
- `examples/launchmybakery/google.md` — Google Cloud-specific bakery agent deployment
- `examples/with-adk/README.md` — ADK integration patterns overview
- `examples/with-adk/a2a/typescript/README.md` — TypeScript A2A client example
- `examples/with-adk/a2a/docs/README.md` — A2A protocol documentation
- `examples/with-adk/a2a/docs/ag_ui.md` — Agent-User Interaction (AG-UI) protocol with ADK
- `examples/deep-search/README.md` — Deep search research agent pattern
- `examples/academic-research/README.md` — Academic research agent workflow

## Source Files
Full source removed (2026-06-06), available at:
- ADK: https://github.com/GoogleCloudPlatform/agent-starter-pack
- ADK SDK: https://github.com/google/adk-python

## What Was Removed
Python source (`.py`), Jupyter notebooks (`.ipynb`), Terraform HCL (`.tf`, `.tfvars`), YAML configs (`deployment.yaml`, `cloudbuild.yaml`), lock files (`uv.lock`, `yarn.lock`), `Makefile`, `Dockerfile`, `pyproject.toml`, `.env.example`, shell scripts, JSON configs, and all non-markdown assets.

---


## File: docs/agents/google-adk/README.md

# saoi

A base ReAct agent built with Google's Agent Development Kit (ADK) and Agent2Agent (A2A) Protocol. #experimental
Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.29.3`

## Project Structure

This project is organized as follows:

```
saoi/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── agent_engine_app.py # Agent Engine application logic
│   └── app_utils/       # App utilities and helpers
├── .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├── deployment/          # Infrastructure and deployment scripts
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Project dependencies and configuration
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform**: For infrastructure deployment - [Install](https://developer.hashicorp.com/terraform/downloads)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
make install && make playground
```
> **📊 Observability Note:** Agent telemetry (Cloud Trace) is always enabled. Prompt-response logging (GCS, BigQuery, Cloud Logging) is **disabled** locally, **enabled by default** in deployed environments (metadata only - no prompts/responses). See [Monitoring and Observability](#monitoring-and-observability) for details.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment for testing agent |
| `make deploy`        | Deploy agent to Agent Engine |
| `make register-gemini-enterprise` | Register deployed agent to Gemini Enterprise ([docs](https://googlecloudplatform.github.io/agent-starter-pack/cli/register_gemini_enterprise.html)) |
| `make inspector`     | Launch A2A Protocol Inspector to test your agent implementation                             |
| `make test`          | Run unit and integration tests                                                              |
| `make lint`          | Run code quality checks (codespell, ruff, mypy)                                             |
| `make setup-dev-env` | Set up development environment resources using Terraform                         |

For full command options and usage, refer to the [Makefile](Makefile).

## Using the A2A Inspector

This agent implements the [Agent2Agent (A2A) Protocol](https://a2a-protocol.org/), enabling interoperability with agents across different frameworks and languages.

The [A2A Inspector](https://github.com/a2aproject/a2a-inspector) provides the following core features:
- 🔍 View agent card and capabilities
- ✅ Validate A2A specification compliance
- 💬 Test communication with live chat interface
- 🐛 Debug with the raw message console

### Local Testing

> **Note:** For Agent Engine deployments, local testing with A2A endpoints requires deployment first, as `make playground` uses the ADK web interface. For local development, use `make playground`. To test A2A protocol compliance, follow the Remote Testing instructions below.

### Remote Testing

1. Deploy your agent:
   ```bash
   make deploy
   ```

2. Launch the inspector:
   ```bash
   make inspector
   ```

3. Get an authentication token:
   ```bash
   gcloud auth print-access-token
   ```

4. In the inspector UI at http://localhost:5001:
   - Add an HTTP header with name: `Authorization`
   - Set the value to: `Bearer <your-token-from-step-3>`
   - Connect to your Agent Engine URL using this format:
     ```
     https://eu-west1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{ENGINE_ID}/a2a/v1/card
     ```
     Find your `PROJECT_ID`, `REGION`, and `ENGINE_ID` in the `latest_deployment_metadata.json` file created after deployment.


## Usage

This template follows a "bring your own agent" approach - you focus on your business logic, and the template handles everything else (UI, infrastructure, deployment, monitoring).
1. **Prototype:** Build your Generative AI Agent using the intro notebooks in `notebooks/` for guidance. Use Vertex AI Evaluation to assess performance.
2. **Integrate:** Import your agent into the app by editing `app/agent.py`.
3. **Test:** Explore your agent functionality using the local playground with `make playground`. The playground automatically reloads your agent on code changes.
4. **Deploy:** Set up and initiate the CI/CD pipelines, customizing tests as necessary. Refer to the [deployment section](#deployment) for comprehensive instructions. For streamlined infrastructure deployment, simply run `uvx agent-starter-pack setup-cicd`. Check out the [`agent-starter-pack setup-cicd` CLI command](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html). Currently supports GitHub with both Google Cloud Build and GitHub Actions as CI/CD runners.
5. **Monitor:** Track performance and gather insights using BigQuery telemetry data, Cloud Logging, and Cloud Trace to iterate on your application.

The project includes a `GEMINI.md` file that provides context for AI tools like Gemini CLI when asking questions about your template.


## Deployment

> **Note:** For a streamlined one-command deployment of the entire CI/CD pipeline and infrastructure using Terraform, you can use the [`agent-starter-pack setup-cicd` CLI command](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html). Currently supports GitHub with both Google Cloud Build and GitHub Actions as CI/CD runners.

### Dev Environment

You can test deployment towards a Dev Environment using the following command:

```bash
gcloud config set project <your-dev-project-id>
make deploy
```


The repository includes a Terraform configuration for the setup of the Dev Google Cloud project.
See [deployment/README.md](deployment/README.md) for instructions.

### Production Deployment

The repository includes a Terraform configuration for the setup of a production Google Cloud project. Refer to [deployment/README.md](deployment/README.md) for detailed instructions on how to deploy the infrastructure and application.

## Monitoring and Observability

The application provides two levels of observability:

**1. Agent Telemetry Events (Always Enabled)**
- OpenTelemetry traces and spans exported to **Cloud Trace**
- Tracks agent execution, latency, and system metrics

**2. Prompt-Response Logging (Configurable)**
- GenAI instrumentation captures LLM interactions (tokens, model, timing)
- Exported to **Google Cloud Storage** (JSONL), **BigQuery** (external tables), and **Cloud Logging** (dedicated bucket)

| Environment | Prompt-Response Logging |
|-------------|-------------------------|
| **Local Development** (`make playground`) | ❌ Disabled by default |
| **Deployed Environments** (via Terraform) | ✅ **Enabled by default** (privacy-preserving: metadata only, no prompts/responses) |

**To enable locally:** Set `LOGS_BUCKET_NAME` and `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`.

**To disable in deployments:** Edit Terraform config to set `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`.

See the [observability guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html) for detailed instructions, example queries, and visualization options.

---


## File: docs/agents/google-adk/tests/load_test/README.md


# Robust Load Testing for Generative AI Applications

This directory provides a comprehensive load testing framework for your Generative AI application, leveraging the power of [Locust](http://locust.io), a leading open-source load testing tool.

##  Load Testing

Before running load tests, ensure you have deployed the backend remotely.

Follow these steps to execute load tests:

**1. Deploy the Backend Remotely:**
   ```bash
   gcloud config set project <your-dev-project-id>
   make deploy
   ```

**2. Create a Virtual Environment for Locust:**
   It's recommended to use a separate terminal tab and create a virtual environment for Locust to avoid conflicts with your application's Python environment.

   ```bash
   python3 -m venv .locust_env && source .locust_env/bin/activate && pip install locust==2.31.1
   ```

**3. Execute the Load Test:**
   Trigger the Locust load test with the following command:

   ```bash
   export _AUTH_TOKEN=$(gcloud auth print-access-token -q)
   locust -f tests/load_test/load_test.py \
   --headless \
   -t 30s -u 5 -r 2 \
   --csv=tests/load_test/.results/results \
   --html=tests/load_test/.results/report.html
   ```

   This command initiates a 30-second load test, simulating 2 users spawning per second, reaching a maximum of 10 concurrent users.


---


## File: docs/agents/z_ai/Vision MCP Server.md

---
title: "Vision MCP Server"
source: "https://docs.z.ai/devpack/mcp/vision-mcp-server"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
Vision MCP Server is a Z.AI capability implementation based on the Model Context Protocol (MCP), providing powerful Z.AI GLM-4.6V capabilities for MCP-compatible clients such as Claude Code and Cline, including image analysis, video understanding, and other features.

**NPM Package**: [@z\_ai/mcp-server](https://www.npmjs.com/package/@z_ai/mcp-server)  
**Prerequisites**: [Node.js >= v22.0.0](https://nodejs.org/en/download/)

Please install the latest version(>= 0.1.2) of the vision mcp server to experience the GLM-4.6V capability.  
Existing users might still be using a cached older version. Please clear the npx cache, or append the `@latest` tag to `z_ai/mcp-server` to force-install the newest version (i.e., `z_ai/mcp-server@latest`).

## Product Overview

This Local MCP Server is an exclusive server developed by Z.AI for **GLM Coding Plan users**, empowering your Code Agent with eyes and limitless vision understanding.

Except in Claude Code, pasting an image directly into the client cannot call this MCP Server, as the client will by default transcode the image and call the model interface directly.  
The best practice is to place the image in a local directory and invoke the MCP Server by specifying the image name or path in the conversation.  
For example: `What does demo.png describe?`

## Features

## Image Analysis

Supports intelligent analysis and content understanding of multiple image formats, giving your AI Agent visual capabilities

## Video Understanding

Supports visual understanding of both local and remote videos

## Easy Integration

One-click installation, quick integration with Claude Code and other MCP-compatible clients

## Supported Tools

This server implements the Model Context Protocol and can be used with any MCP-compatible client. Currently provides the following tools:
- **`ui_to_artifact`** - Turn UI screenshots into code, prompts, specs, or descriptions.
- **`extract_text_from_screenshot`** - OCR screenshots for code, terminals, docs, and general text.
- **`diagnose_error_screenshot`** - Analyze error snapshots and propose actionable fixes.
- **`understand_technical_diagram`** - Interpret architecture, flow, UML, ER, and system diagrams.
- **`analyze_data_visualization`** - Read charts and dashboards to surface insights and trends.
- **`ui_diff_check`** - Compare two UI shots to flag visual or implementation drift.
- **`image_analysis`** - General-purpose image understanding when other tools don’t fit.
- **`video_analysis`** - Inspect videos (local/remote ≤8 MB; MP4/MOV/M4V) to describe scenes, moments, and entities.

## Environment Variable Configuration

### Detailed Configuration

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Desktop
- Cline (VS Code)
- OpenCode
- Crush
- Roo Code, Kilo Code and Other MCP Clients

**Method A: One-click Installation Command** Be sure to replace `your_api_key` with the API Key you obtained.If you forgot to replace the API Key, you need to uninstall the old MCP Server before re-executing the installation command:**Method B: Manual Configuration** Edit Claude Desktop’s configuration file `.claude.json` `mcpServers` content:  
Be sure to replace `your_api_key` with the API Key you obtained.

## Usage Example

Except in Claude Code, pasting an image directly into the client cannot call this MCP Server, as the client will by default transcode the image and call the model interface directly.  
The best practice is to place the image in a local directory and invoke the MCP Server by specifying the image name or path in the conversation.  
For example: `What does demo.png describe?`

Through the previous step of installing the Vision MCP server to the client, you can directly use MCP in your Coding client.  
For example, in Claude Code, inputting `hi describe this xx.png` in the conversation, the MCP Server will process the image and return the description result. (The prerequisite is that you have the image in your current directory)![Description](https://cdn.bigmodel.cn/markdown/1760501186683image.png?attname=image.png)

Description

## Troubleshooting

Run the following command in your local terminal to verify if it can be installed locally, to troubleshoot environment, permission, and other issues:
- If installed successfully, it indicates that the environment is correct, and the issue may be with the client configuration. Please check the client’s MCP configuration.
- If installation fails, please troubleshoot based on the error message. It is recommended to paste the error message to a large model for analysis and resolution.
Other common issues:

Connection Closed

**Issue：** Mcp server connection closed **Solutions：**
1. Check whether Node.js 22 or a newer version is installed locally.
2. Run `node -v` and `npx -v` to verify that the execution environment is available.
3. Check the environment variable `Z_AI_API_KEY` is configured correctly.

**Issue:** Receiving invalid API Key error **Solutions:**
1. Confirm the API Key is correctly copied
2. Check if the API Key is activated
3. Confirm the selected platform (`Z_AI_MODE`) matches the API Key
4. Check if the API Key has sufficient balance

Connection Timeout

**Issue:** MCP server connection timeout **Solutions:**
1. Check network connection
2. Confirm firewall settings
3. Increase timeout settings

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

- [Model Context Protocol (MCP) Official Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [Vision Model Introduction](https://docs.z.ai/guides/vlm/glm-4.6v)

[FAQs](https://docs.z.ai/devpack/faq) [Web Search MCP Server](https://docs.z.ai/devpack/mcp/search-mcp-server)
---


## File: docs/agents/z_ai/Web Reader MCP Server.md

---
title: "Web Reader MCP Server"
source: "https://docs.z.ai/devpack/mcp/reader-mcp-server"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
The Web Reader MCP Server is a Z.AI implementation based on the Model Context Protocol (MCP). It provides Claude Code, Cline, and other MCP-compatible clients with powerful web content extraction capabilities, including full-page content retrieval and structured data extraction.

## Overview

This remote MCP server with web content reading capability is available to users on **GLM Coding Plan**, enabling your code agent to fetch detailed page content and structured data.

## Features

## Web Content Reading

Fetch the complete content of any webpage, including text, and links

## Structured Data

Extract structured data such as title, main body, and metadata

## Remote Service

HTTP-based remote MCP service, no local installation required

## Tools

This server implements the Model Context Protocol and works with any MCP-compatible client. Currently, it provides the following tool:
- **`webReader`** — Fetch webpage content for a specified URL. Returns the page title, main content, metadata, list of links, and more.

## Example Scenarios

Parse project websites or repository pages (such as README, release notes, and usage guides) to extract core information and link lists, assisting evaluation and integration.

Extract steps, commands, and caveats from blogs, tutorials, and guide pages, organizing unstructured content into actionable developer notes and task lists.

For issue remediation, read the publicly available steps on the specified web page and use them as references to resolve the problem.

Convert content from designated web pages into structured data and leverage in-page links for incremental synchronization to build a team technical knowledge base.

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Code
- Cline (VS Code)
- OpenCode
- Crush
- Goose
- Roo Code, Kilo Code, Others

**One-click install command** Replace `your_api_key` with the API key you obtained in the previous step **Manual configuration** Edit the Claude Code configuration file under your home directory, the MCP section of `.claude.json`:

## Troubleshooting

Connection timeout

**Issue:** Connection to the MCP server timed out **Solutions:**
1. Check your network connection
2. Verify firewall settings
3. Ensure the server URL is correct
4. Increase client timeout settings

**Issue:** Web content reading returned empty result or error **Solutions:**
1. Confirm the target URL is accessible
2. Check if the page has anti-scraping mechanisms
3. Try different URLs
4. Ensure network connectivity is normal
5. Contact technical support for assistance

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

## Resources

- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [GLM Coding Plan Overview](https://docs.z.ai/devpack/overview)

[Web Search MCP Server](https://docs.z.ai/devpack/mcp/search-mcp-server) [Zread MCP Server](https://docs.z.ai/devpack/mcp/zread-mcp-server)
---


## File: docs/agents/z_ai/Web Search MCP Server.md

---
title: "Web Search MCP Server"
source: "https://docs.z.ai/devpack/mcp/search-mcp-server"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
Web Search MCP Server is a Z.AI search capability implementation based on the Model Context Protocol (MCP), providing powerful Z.AI search capabilities for MCP-compatible clients such as Claude Code and Cline, including web search, real-time information retrieval, and other features.

## Product Overview

This Remote MCP Server with search capabilities is an exclusive server developed by Z.AI for **GLM Coding Plan users**, empowering your Code Agent with search capabilities and unlimited access to real-time information and web resources.

## Features

## Web Search

Supports comprehensive web search to retrieve the latest web information and resources

## Real-time Information

Retrieves real-time updated information including news, stock prices, weather, and more

## Remote Service

HTTP protocol-based remote MCP service, no local installation required

## Supported Tools

This server implements the Model Context Protocol and can be used with any MCP-compatible client. Currently provides the following tools:
- **`webSearchPrime`** - Search web information, returning results including page titles, URLs, summaries, site names, site icons, and more.

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Code
- Cline (VS Code)
- OpenCode
- Crush
- Goose
- Roo Code, Kilo Code and Other MCP Clients

**One-click Installation Command** Be sure to replace `your_api_key` with the API Key you obtained.**Manual Configuration** Edit Claude Code’s configuration file `.claude.json` in the user directory, MCP section:

## Usage Example

Through the previous step of installing the Search MCP server to the client, you can directly use MCP in your Coding client.  
You can directly use search functionality in conversations:
- “Help me search for the latest AI technology developments”
- “Find best practices for Python asynchronous programming”

## Troubleshooting

Connection Timeout

**Issue:** MCP server connection timeout **Solutions:**
1. Check network connection
2. Confirm firewall settings
3. Verify the server URL is correct
4. Increase timeout settings

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

- [Model Context Protocol (MCP) Official Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [GLM Coding Plan Overview](https://docs.z.ai/devpack/overview)

[Vision MCP Server](https://docs.z.ai/devpack/mcp/vision-mcp-server) [Web Reader MCP Server](https://docs.z.ai/devpack/mcp/reader-mcp-server)
---


## File: docs/agents/z_ai/Zread MCP Server.md

---
title: "Zread MCP Server"
source: "https://docs.z.ai/devpack/mcp/zread-mcp-server#repository-access-failed"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
The Zread MCP Server is a Z.AI implementation based on the Model Context Protocol (MCP). Powered by [zread.ai](https://zread.ai/), it provides Claude Code, Cline, and other MCP-compatible clients with knowledge documentation and code access capabilities for open source repositories.

## Overview

This remote MCP server with open source repository Q&A capability is available to users on **GLM Coding Plan**, enabling your code agent to deeply understand open source projects and efficiently fetch documentation, code structure, and file content.

## Features

## Tools

This server implements the Model Context Protocol and works with any MCP-compatible client. Currently, it provides the following tools:
- **`search_doc`** — Search for knowledge documentation corresponding to the GitHub repository, quickly understanding repository knowledge, news, recent issues, PRs, and contributors.
- **`get_repo_structure`** — Get the directory structure and file list of the GitHub repository to understand project module splitting and directory organization.
- **`read_file`** — Read the complete code content of specified files in the GitHub repository to deeply analyze the implementation details of the file code.

## Example Scenarios

Quickly understand the core concepts, installation steps, and code organization of open source libraries by searching documentation and obtaining repository structures, accelerating the learning curve.

When encountering problems, search the repository’s Issue and Commit history to find solutions or fix records for similar problems.

Directly read the code content of core files, analyze implementation logic, and assist in secondary development or Debugging.

Before introducing a new dependency library, evaluate its activity, code quality, and maintenance status by viewing its repository structure and documentation.

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Code
- Cline (VS Code)
- OpenCode
- Crush
- Goose
- Roo Code, Kilo Code, Others

**One-click install command** Replace `your_api_key` with the API key you obtained in the previous step **Manual configuration** Edit the Claude Code configuration file under your home directory, the MCP section of `.claude.json`:

## Troubleshooting

Connection timeout

**Issue:** Connection to the MCP server timed out **Solutions:**
1. Check your network connection
2. Verify firewall settings
3. Ensure the server URL is correct
4. Increase client timeout settings

**Issue:** Unable to search or read specified repository content **Solutions:**
1. Confirm the repository exists and is open source (public)
2. Check if the repository name is spelled correctly (owner/repo)
3. Visit zread.ai to search if this open source repository is supported

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches, web readers and ZRead MCP calls, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches, web readers and ZRead MCP calls, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches, web readers and ZRead MCP calls, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

## Resources

- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [GLM Coding Plan Overview](https://docs.z.ai/devpack/overview)

[Web Reader MCP Server](https://docs.z.ai/devpack/mcp/reader-mcp-server) [Coding Tool Helper](https://docs.z.ai/devpack/extension/coding-tool-helper)
---


## Original Sources

- `docs/agents/agno/agno/.github/pull_request_template.md`
- `docs/agents/agno/agno/CONTRIBUTING.md`
- `docs/agents/agno/agno/README.md`
- `docs/agents/agno/agno/SKILL_CONTEXT.md`
- `docs/agents/agno/github_repo_analyzer/README.md`
- `docs/agents/agno/KCG_SUMMARY.md`
- `docs/agents/agno/python/examples/README.md`
- `docs/agents/agno/typescript/README.md`
- `docs/agents/google-adk/deployment/README.md`
- `docs/agents/google-adk/examples/academic-research/README.md`
- `docs/agents/google-adk/examples/deep-search/README.md`
- `docs/agents/google-adk/examples/firecrawl/app/README.md`
- `docs/agents/google-adk/examples/firecrawl/docs/agent-team.md`
- `docs/agents/google-adk/examples/firecrawl/docs/quickstart-streaming.md`
- `docs/agents/google-adk/examples/firecrawl/docs/tool-usage-examples.md`
- `docs/agents/google-adk/examples/firecrawl/README.md`
- `docs/agents/google-adk/examples/launchmybakery/google.md`
- `docs/agents/google-adk/examples/launchmybakery/README.md`
- `docs/agents/google-adk/examples/with-adk/a2a/docs/ag_ui.md`
- `docs/agents/google-adk/examples/with-adk/a2a/docs/README.md`
- `docs/agents/google-adk/examples/with-adk/a2a/typescript/README.md`
- `docs/agents/google-adk/examples/with-adk/README.md`
- `docs/agents/google-adk/GEMINI.md`
- `docs/agents/google-adk/KCG_SUMMARY.md`
- `docs/agents/google-adk/README.md`
- `docs/agents/google-adk/tests/load_test/README.md`
- `docs/agents/z_ai/Vision MCP Server.md`
- `docs/agents/z_ai/Web Reader MCP Server.md`
- `docs/agents/z_ai/Web Search MCP Server.md`
- `docs/agents/z_ai/Zread MCP Server.md`
