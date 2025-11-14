# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SecurityChatbot is an AI-based RAG (Retrieval-Augmented Generation) Security Chatbot using Google Gemini File Search API.

**License**: MIT License (Copyright 2025 bluebary)

**Note**: All responses should be in Korean.

**Development Status**: Active development - Initial setup phase

## Technology Stack

- **Python 3.10**: Main development language
- **uv**: Fast, reliable Python package installer and dependency manager
- **Streamlit**: User-friendly web-based UI framework
- **Google Gemini File Search API**: Managed RAG system for document indexing and retrieval
- **python-dotenv**: Environment variable management from `.env` files

## Development Workflow

This project follows a **Gemini-Claude collaborative workflow**:

### Code Implementation
1. **Gemini** (via `mcp__zen__chat` tool): Generates initial code drafts
2. **Claude**: Reviews, refines, and improves the code
3. **Claude**: Writes final code to files using Write/Edit tools
4. **Claude**: Updates [TODO.md](TODO.md) to mark completed items and track progress
5. **Claude**: Creates a git commit when a phase is completed

All code items in [TODO.md](TODO.md) marked with **[Gemini → Claude]** follow this workflow.

**Important**:
- After completing any task or phase, always update the TODO.md checklist to reflect current progress
- **Create a git commit after completing each phase** with a descriptive message (e.g., "Complete Phase 5: Chat interface implementation")

### Documentation
**All documentation is written by Claude**, including:
- README.md
- Architecture documentation (docs/)
- Code comments and docstrings
- API documentation
- User guides

### Using mcp__zen__chat

When requesting code from Gemini:
- Provide clear requirements and context
- Specify the file/module to be created
- Include relevant technical constraints
- Reference existing code patterns when applicable

**Note**: Do not request documentation from Gemini - Claude handles all documentation tasks.

## Development Progress

**Current Phase**: Phase 7 - Advanced Features Implementation

See [TODO.md](TODO.md) for detailed implementation checklist (10 phases, ~60 items).

**Progress Summary**:
- **Completed**: 37/60 items (62%)
- **Completed Phases**: Phase 1 ✅, Phase 2 ✅, Phase 3 ✅, Phase 4 ✅, Phase 5 ✅, Phase 6 ✅
- **In Progress**: Phase 7 🔄

**Recent Milestones**:
- ✅ Project initialization and setup complete
- ✅ Gemini API integration complete
- ✅ Document upload and indexing complete
- ✅ Streamlit UI implementation complete
- ✅ Chat interface implementation complete
- ✅ RAG query handler integration complete

**Important**: Always update [TODO.md](TODO.md) with current progress after completing tasks or phases.

## File Format Support

**Supported Document Formats**:
- PDF (application/pdf)
- TXT (text/plain)
- Markdown (text/markdown)
- HWP (application/x-hwp)
- HWPX (application/x-hwp-v5)

**Limitations**:
- Maximum file size: 100 MB per file
- Files are processed and indexed automatically by Gemini File Search API (no manual preprocessing needed)

## Project Architecture

### RAG Pipeline Architecture

```
User Input (Query / File Upload)
        ↓
  Streamlit UI
        ↓
        ├─ File Upload Flow ─────────────────────────┐
        │       ↓                                     │
        │  Document Validation                        │
        │       ↓                                     │
        │  Upload to Gemini File Search Store        │
        │  (Automatic chunking & indexing)           │
        │       ↓                                     │
        │  Indexed Knowledge Base                     │
        │                                             │
        ├─ Query Flow ───────────────────────────────┘
        │       ↓
        │  RAG Query Handler
        │       ↓
        │  Gemini File Search API
        │  (Retrieval: semantic search)
        │       ↓
        │  Gemini Pro LLM
        │  (Generation: with retrieved context)
        │       ↓
        │  Response + Citations
        │       ↓
  Streamlit UI (Display)
```

### Directory Structure

```
SecurityChatbot/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── .python-version               # Python version (3.10)
├── pyproject.toml                # Project metadata and dependencies
├── uv.lock                       # Dependency lockfile
├── README.md                     # User guide
├── LICENSE                       # MIT License
├── CLAUDE.md                     # This file
├── TODO.md                       # Implementation checklist
│
├── src/
│   └── security_chatbot/         # Main application package
│       ├── __init__.py
│       ├── main.py               # Streamlit app entry point
│       ├── config.py             # Configuration and env var management
│       │
│       ├── rag/                  # RAG pipeline modules
│       │   ├── __init__.py
│       │   ├── document_manager.py   # File upload and validation
│       │   ├── store_manager.py      # File Search Store operations
│       │   └── query_handler.py      # RAG query processing
│       │
│       ├── chat/                 # Chat interface modules
│       │   ├── __init__.py
│       │   ├── session.py        # Session state management
│       │   └── ui_components.py  # Reusable UI components
│       │
│       └── utils/                # Utility modules
│           ├── __init__.py
│           └── api_client.py     # Gemini API client wrapper
│
├── data/
│   └── documents/                # Uploaded documents (gitignored)
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_api_client.py
│   ├── test_store_manager.py
│   ├── test_document_manager.py
│   ├── test_query_handler.py
│   └── test_integration.py       # End-to-end tests
│
└── docs/
    └── architecture.md           # Detailed architecture docs (optional)
```

### Module Responsibilities

- **main.py**: Streamlit application entry point, UI layout orchestration
- **config.py**: Load environment variables, define configuration constants
- **api_client.py**: Initialize and manage Gemini API client
- **store_manager.py**: Create, list, retrieve, and delete File Search Stores
- **document_manager.py**: Validate, upload documents to File Search Store, monitor indexing
- **query_handler.py**: Process user queries using RAG pipeline, format responses
- **session.py**: Manage Streamlit session state (chat history, store info)
- **ui_components.py**: Reusable Streamlit UI components (chat messages, file uploader)

## Development Setup

### Prerequisites

1. **Install uv**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or via pip
   pip install uv

   # Or via pipx
   pipx install uv
   ```

2. **Verify Python 3.10** is available:
   ```bash
   python3.10 --version
   ```

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SecurityChatbot
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```
   This installs all dependencies defined in `pyproject.toml`.

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Get Gemini API Key**:
   - Visit https://ai.google.dev/
   - Sign in and navigate to API keys
   - Create a new API key
   - Copy to `.env` file

## Common Commands

### Development

```bash
# Install/sync dependencies
uv sync

# Run Streamlit development server
uv run streamlit run src/security_chatbot/main.py

# Run with auto-reload on code changes
uv run streamlit run src/security_chatbot/main.py --server.runOnSave=true
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src/security_chatbot --cov-report=html

# Run specific test file
uv run pytest tests/test_document_manager.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code with Black
uv run black src/ tests/

# Lint code with Ruff
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Type checking (if mypy is added)
uv run mypy src/
```

### Package Management

```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Update all dependencies
uv lock --upgrade

# Remove a dependency
uv remove <package-name>
```

## Security Best Practices

- **Never commit `.env` file** - Contains sensitive API keys
- **Use `.env.example`** - Provide template for required environment variables
- **Validate file uploads** - Check file size and format before processing
- **Handle API errors gracefully** - Don't expose internal errors to users
- **Rate limit handling** - Implement retry logic with exponential backoff
- **Input sanitization** - Validate and sanitize user queries

## Troubleshooting

### Common Issues

1. **API Key Error**:
   - Ensure `GEMINI_API_KEY` is set in `.env`
   - Verify API key is valid at https://ai.google.dev/

2. **Import Errors**:
   - Run `uv sync` to ensure all dependencies are installed
   - Check Python version is 3.10

3. **Streamlit Not Found**:
   - Use `uv run` prefix: `uv run streamlit run ...`
   - Or activate venv manually and run streamlit

## Next Steps

See [TODO.md](TODO.md) for the complete implementation roadmap.
