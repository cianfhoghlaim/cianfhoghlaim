
# 🦄 ai that works: Dynamic Schemas

> In this episode, Dex and Vaibhav explore the concept of dynamic UIs and how to build systems that can adapt to unknown data structures. They discuss the importance of dynamic schema generation, meta programming with LLMs, and the potential for creating dynamic React components.

[Video](https://youtu.be/bak7-C--azc) (1h27m)

[![Dynamic Schemas](https://img.youtube.com/vi/bak7-C--azc/0.jpg)](https://youtu.be/bak7-C--azc)


## Episode Overview

BAML can be leveraged to build a pipeline that can extract anything without knowing the schema in advance.

This is done via 2 steps:

1. Ask an LLM to describe a schema that could represent the content of the document.

2. Use the schema to extract the content by leveraging dynamic types.

## Whiteboards

<img width="8727" height="4644" alt="image" src="https://github.com/user-attachments/assets/410097e4-c2dd-490c-9ab2-c795ee80f0af" />


## Architecture

Backend is python + FASTAPI + BAML

Frontend is React

We try and stream whatever possible!

```bash
# Start the backend
cd backend
uv run fastapi run server.py --reload

```

```bash
# Start the frontend
cd frontend
pnpm dev
```

## Key Takeaways

- Dynamic schema generation enables systems to adapt to unknown data structures
- Meta programming with LLMs opens new possibilities for creating flexible components
- Building robust workflows around schema management is critical for production systems
- The execution and rendering of dynamic schemas presents both challenges and opportunities

## Resources

- [Session Recording](https://youtu.be/bak7-C--azc)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)
