# Architecture

This project is a local-first multi-agent coding assistant. It is designed to be easy to run on a laptop while preserving patterns that map to production AI systems.

## Runtime Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI / FastAPI
    participant Graph as LangGraph Workflow
    participant RAG as Embedding RAG Retriever
    participant LLM as LLM Provider
    participant MCP as MCP Repository Server
    participant FS as Workspace Files

    User->>CLI: Submit requirement
    CLI->>Graph: Run assistant graph
    Graph->>RAG: Retrieve repository context
    RAG->>FS: Read workspace files
    Graph->>LLM: Architect prompt with context
    Graph->>LLM: Code-generation prompt
    Graph->>LLM: Test-generation prompt
    Graph->>LLM: Review prompt
    Graph->>MCP: write_file generated/feature.py
    MCP->>FS: Persist generated artifact safely
    Graph->>MCP: write_file generated/test_feature.py
    MCP->>FS: Persist generated test artifact safely
    Graph->>CLI: Return design, artifacts, tests, review
```

## Design Choices

- **LangGraph orchestration:** keeps the workflow explicit and testable instead of hiding logic in one large prompt.
- **Agent roles:** separates architecture, implementation, testing, and review responsibilities.
- **Provider abstraction:** supports a local deterministic provider for CI and Vertex AI Gemini for real generation.
- **Embedding RAG:** retrieves relevant workspace context before generation.
- **MCP file tools:** generated artifacts are written through an MCP client/server boundary.
- **Safe repository access:** file writes are constrained to `WORKSPACE_ROOT`.

## Production Roadmap

- Replace local hash embeddings with Vertex AI embeddings.
- Store vectors in Vertex AI Vector Search or pgvector.
- Add a GitHub MCP server for branch creation, commits, and pull requests.
- Run generated tests in an isolated workspace and feed failures back to the graph.
- Add tracing and evaluation metrics for context relevance, faithfulness, and code quality.

