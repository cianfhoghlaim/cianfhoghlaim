---
title: "LiteLLM - Pydantic Logfire Documentation"
source: "https://logfire.pydantic.dev/docs/integrations/llms/litellm/"
author:
published:
created: 2025-12-29
description: "Pydantic Logfire Documentation"
tags:
  - "clippings"
---
[Skip to content](https://logfire.pydantic.dev/docs/integrations/llms/litellm/#litellm)

## LiteLLM

**Logfire** supports instrumenting calls to the [LiteLLM](https://docs.litellm.ai/) Python SDK with the [`logfire.instrument_litellm()`](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire.instrument_litellm) method.

## Installation

Install `logfire` with the `litellm` extra:

```bash
pip install 'logfire[litellm]'
```

```bash
uv add 'logfire[litellm]'
```

## Usage

```python
import litellm

import logfire

logfire.configure()
logfire.instrument_litellm()

response = litellm.completion(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Hi'}],
)
print(response.choices[0].message.content)
# > Hello! How can I assist you today?
```

Warning

This currently works best if all arguments of instrumented methods are passed as keyword arguments, e.g. `litellm.completion(model=model, messages=messages)`.

This creates a span which shows the conversation in the Logfire UI:

![Logfire LiteLLM conversation](https://logfire.pydantic.dev/docs/images/logfire-screenshot-litellm-llm-panel.png)

Logfire LiteLLM conversation

[`logfire.instrument_litellm()`](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire.instrument_litellm) uses the `LiteLLMInstrumentor().instrument()` method of the [`openinference-instrumentation-litellm`](https://pypi.org/project/openinference-instrumentation-litellm/) package.

Note

[LiteLLM has its own integration with Logfire](https://docs.litellm.ai/docs/observability/logfire_integration), but we recommend using `logfire.instrument_litellm()` instead.