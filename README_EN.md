# CogniForge

> **AI-Era Developer Cognitive Enhancement Engine** — Make AI Tools Remember Every Decision You Make

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/lanekingkong/cogniforge)

[中文](README.md) | [Docs](docs/5W1H_ARCHITECTURE.md)

---

## The Pain: Developer Struggles in the AI Era

| Pain Point | Data Point | CogniForge Solution |
|------------|-----------|---------------------|
| **Cross-session Amnesia** | Devs lose 3.2 hrs/week re-explaining context | Memory Palace Engine - persistent, queryable decision history |
| **Token Bloat** | 40-file project needs 47,450 tokens for context | Smart Context Compressor - saves 60-95% tokens |
| **Multi-tool Silos** | 88% devs report lower efficiency when switching tools | Cross-tool Sync Bridge - unified context across Claude/Cursor/Copilot |
| **Knowledge Decay** | Only 20% of key decisions recallable after 3 months | Knowledge Graph Engine - zero-LLM code structure indexing |

## Core Capabilities

### 1. Memory Palace Engine
```
Palace
 ├── Wing (partitioned by project/module)
 │   ├── Hall (decisions/patterns/knowledge/fixes/context)
 │   │   ├── Room (specific topic)
 │   │   │   ├── Memory (entry)
```
- **Auto-consolidation**: Merge duplicate memories, reduce fragmentation
- **Semantic Search**: LanceDB-powered vector search with keyword fallback
- **Access-heat Ranking**: Most-accessed memories prioritized

### 2. Code Knowledge Graph Engine
- **Zero LLM Calls**: Pure AST parsing, zero token consumption
- **Auto Indexing**: Function/class/module relationship mapping
- **Dependency Tracking**: Inheritance chains, call graphs
- **Incremental Updates**: Re-index only changed files

### 3. Smart Context Compressor
- **Level 1 - Summary** (~200 tokens): Project overview
- **Level 2 - Structural** (~500 tokens): Directory tree + key interfaces
- **Level 3 - Detailed** (on-demand): Memory + focus files
- **Adaptive**: Auto-truncate when exceeding token limits

### 4. Cross-tool Sync Bridge
| Tool | Sync Path | Format |
|------|----------|--------|
| Claude Code | `.claude/skills/cogniforge/` | Markdown Skill |
| Cursor | `.cursor/rules/` | MDC Rule |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown Instructions |
| Generic MCP | `localhost:8765` | JSON-RPC |

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/lanekingkong/cogniforge.git
cd cogniforge
pip install -e .

# Full dependencies
pip install -e ".[dev]"
```

### 30-Second Quickstart

```bash
# 1. Initialize
cogniforge init ./my-project

# 2. Record a memory
cogniforge memory remember "Chose FastAPI for async support" --topic "Tech Stack" --hall decisions

# 3. Recall memories
cogniforge memory recall "FastAPI"

# 4. Build knowledge graph
cogniforge graph build

# 5. Search code
cogniforge graph search "Database"

# 6. Sync to AI tools
cogniforge sync all

# 7. Get compressed context
cogniforge index context --level 2
```

## Architecture

```
cogniforge/
├── src/
│   ├── core/                    # Core Engines
│   │   ├── memory_engine.py     # Memory Palace
│   │   ├── knowledge_graph.py   # Code Graph
│   │   ├── context_compressor.py # Context Compression
│   │   └── sync_bridge.py       # Cross-tool Sync
│   ├── storage/                 # Storage Layer
│   │   ├── vector_store.py      # LanceDB
│   │   ├── graph_store.py       # SQLite Graph
│   │   └── local_db.py          # Local Metadata
│   ├── cli/                     # CLI
│   │   └── main.py              # Typer CLI
│   └── adapters/                # Adapters (reserved)
├── skills_builtin/              # Built-in AI Skills
│   ├── project_onboarding.yaml  # Project Q&A
│   ├── change_tracker.yaml      # Change Tracking
│   ├── prompt_enhancer.yaml     # Prompt Enhancement
│   └── code_review.yaml         # Smart Code Review
├── tests/                       # Tests
│   ├── test_core.py             # Core Engine Tests
│   └── conftest.py              # Test Config
├── examples/                    # Examples
│   └── usage.py                 # Full Usage Demo
└── docs/
    └── 5W1H_ARCHITECTURE.md     # Architecture Docs
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Vector Store | LanceDB + Sentence-Transformers | Semantic Search |
| Graph Store | SQLite + NetworkX | Relationship Queries |
| Parsing | Python AST | Zero-LLM Code Analysis |
| CLI | Typer + Rich | Terminal UI |
| Sync Protocol | MCP (FastMCP) / Watchdog | Cross-tool Communication |
| Testing | Pytest | Unit Tests |

## API Usage

```python
from cogniforge.core.memory_engine import jiyigongdian
from cogniforge.core.knowledge_graph import zhishitupu

# Memory Engine
jiyi = jiyigongdian('./my-project')
jiyi.jilu("Chose Redis for caching", "Caching", hall_type="decisions")
jiyi.huiqu("Redis")

# Knowledge Graph
tupu = zhishitupu('./my-project')
tupu.goujian_suoyin()
tupu.chaxun("cache")
```

## Roadmap

- **v0.1.0** (current): Four core engines + CLI + built-in skills
- **v0.2.0**: Enhanced semantic search + incremental graph updates
- **v0.3.0**: Production MCP server + IDE plugins
- **v1.0.0**: Cross-project recommendations + team-shared memory

## Contributing

Issues and PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License © 2026 lanekingkong

---

> *"A developer's memory shouldn't be confined to a single chat window"*
>
> CogniForge enables AI tools to truly understand your project history — no more starting from scratch.
