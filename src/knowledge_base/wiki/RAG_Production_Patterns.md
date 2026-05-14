# RAG Production Patterns

## Summary
> [!ABSTRACT]
> Strategies and architectural patterns to mitigate "confident hallucinations" and context blending in production Retrieval-Augmented Generation (RAG) systems.

## Key Insights
- **The "Confident Wrongness" Problem**: Standard retrieve-then-generate pipelines often blend different versions of documents or retrieve low-quality chunks, returning fluent but incorrect answers.
- **Architectural Fixes**:
    - **Routing Layer**: Determines if retrieval is actually necessary to save tokens and avoid noise.
    - **Retrieval Scoring**: Evaluates the quality of retrieved context; triggers query reformulation if scores are too low.
    - **Hallucination Check**: A secondary LLM pass that verifies every claim in the generated answer against the retrieved documents.
    - **Agentic Retry Loop**: Silently reformulates user queries to better match embedding model expectations.

## Connections & Context
- **Related to**: [[reddit_news_2026_05_14.md]]
- **Contradictions/Debates**: Contrasts with the "simple RAG" tutorials which often ignore uncertainty mechanisms.

## Sources
- [[reddit_news_2026_05_14.md]]
- YouTube: SilverConsistent9222 breakdown

---
*Maintained by LLM Agent*