## Never implement features that are outside the scope of your requirements. If you are unsure, please ask for confirmation. 

## When a feature is complete, please create or update the TASK.md file to represent the state.

# Code & Process Standards (Python)

## 1. General Principles

- **Clean Code:**  
  - Follow PEP 8 and The Zen of Python.  
  - Keep functions/classes small (≤ 50 lines). Single responsibility per function/class.  
  - Use descriptive names.  
  - Delete dead code; avoid commented-out code.  
  - Prioritize readability over cleverness.

- **Functional Style & Immutability:**  
  - Favor pure functions without side effects.  
  - Use immutable structures (tuples, `frozenset`) when data shouldn’t change.  
  - Minimize global mutable state.

## 2. Technology Stack

- **Language:** Python 3.10+  
- **Package Management:** Poetry (`pyproject.toml`, `poetry.lock`).  
  -  Always use the latest compatible dependencies
- **Runtime Environment:**  
  - Always use virtual environments (`poetry shell` or `python -m venv`). No global installs.

## 3. Documentation

- **Use context7 MCP server** for up-to-date language documentation.  
- **Use the Sequential Thinking MCP** to break down complex tasks.

## WHAT WE ARE BUILDING

# Multi-Agent Content Generation Backend API

A FastAPI-based backend service that orchestrates a multi-agent LLM system for automated content generation. The system uses typed models, LangGraph orchestration, and OpenAI completions to create a pipeline of specialized agents that research topics and generate platform-optimized content with accompanying images.

## Features

- **FastAPI Web Service**: RESTful API with WebSocket support for real-time updates
- **Research Agent**: Generates 5-7 factual bullet points on a given topic
- **Content Agent**: Creates platform-specific content based on research with appropriate tone
- **Image Agent**: Generates relevant images using DALL-E 3 based on content
- **LinkedIn Integration**: Post generated content with images directly to LinkedIn
- **LangGraph Orchestration**: Structured workflow coordination between agents
- **Real-time WebSocket Communication**: Progress updates during content generation
- **Static File Serving**: Generated images served via `/static` endpoint

## Core Technologies

| Library        | Version     | Purpose                                                           |
|----------------|-------------|-------------------------------------------------------------------|
| FastAPI        | 0.115.0     | Modern async web framework for APIs                              |
| Uvicorn        | 0.24.0      | ASGI server for FastAPI applications                             |
| PydanticAI     | 0.2.15      | Declarative prompt modeling & structured LLM output parsing       |
| LangGraph      | 0.4.8       | DAG-style multi-agent orchestration                              |
| OpenAI SDK     | 1.84.0      | Call GPT-4o and DALL-E 3 through API endpoints                   |
| Logfire        | 3.18.0      | Structured tracing and logging for all prompt/response cycles    |
| WebSockets     | 13.0        | Real-time bidirectional communication                            |
| Poetry         | 1.8.4       | Dependency, packaging, and virtualenv management                 |

## API Endpoints

### REST Endpoints
- `GET /` - Health check endpoint
- `GET /health` - Detailed health information
- `GET /status` - System status and workflow information
- `POST /generate` - Generate content (topic, platform, tone)
- `GET /platforms` - Supported content platforms
- `GET /tones` - Supported content tones
- `GET /static/{path}` - Serve generated images
- `POST /linkedin/post` - Post content with optional image to LinkedIn
- `GET /linkedin/status` - LinkedIn integration status and configuration

### WebSocket Endpoints
- `WS /ws/generate` - Real-time content generation with progress updates

## Project Structure
```
.
├── api/              # FastAPI application
│   └── app.py        # Main FastAPI app with endpoints and WebSocket
├── agents/           # Agent implementations
│   ├── research.py   # ResearchAgent using PydanticAI
│   ├── content.py    # ContentAgent using PydanticAI
│   └── image.py      # ImageAgent with DALL-E 3 integration
├── linkedin/         # LinkedIn integration
│   ├── __init__.py   # LinkedIn module initialization
│   └── client.py     # LinkedIn API client and posting functionality
├── flow/             # LangGraph workflow
│   └── graph.py      # Agent orchestration graph
├── models/           # Typed models
│   └── schema.py     # Pydantic models for agent I/O and API
├── utils/            # Utility modules
│   └── logging.py    # Logfire integration for structured logging
├── data/             # Generated content storage
│   └── images/       # Generated images (served via /static)
├── main.py           # CLI entrypoint for direct workflow execution
├── run_api.py        # API server startup script
├── post_content_test.py  # LinkedIn posting test script
├── .env.example      # Environment variables template
└── pyproject.toml    # Poetry configuration
```

## Running the Backend

### Development Server
```bash
# Install dependencies
poetry install

# Start the API server
poetry run python run_api.py
# or
poetry run uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

# CLI usage (direct workflow execution)
poetry run python main.py "your topic here"
```

### API Usage
- **Base URL**: http://localhost:8000
- **WebSocket URL**: ws://localhost:8000/ws/generate
- **Static Files**: http://localhost:8000/static/images/

### LinkedIn Integration Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your LinkedIn credentials
LINKEDIN_ACCESS_TOKEN=your_linkedin_bearer_token_here
LINKEDIN_PERSON_ID=your_linkedin_person_id_here

# Test LinkedIn integration
poetry run python post_content_test.py
```

#### LinkedIn API Setup
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new application
3. Generate an access token with `ugc:w_member_social` permissions
4. Find your person ID from your LinkedIn profile URL
5. Add credentials to your `.env` file

#### LinkedIn Posting Examples
```bash
# Post text only
curl -X POST http://localhost:8000/linkedin/post \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello LinkedIn! 🚀", "visibility": "PUBLIC"}'

# Post with image
curl -X POST http://localhost:8000/linkedin/post \
  -H "Content-Type: application/json" \
  -d '{"content": "Check out this AI-generated image!", "image_path": "image_filename.png", "visibility": "PUBLIC"}'

# Check LinkedIn status
curl http://localhost:8000/linkedin/status
```

## Frontend Integration

This backend is designed to work with a separate frontend application. The frontend should:
- Make HTTP requests to the REST endpoints
- Establish WebSocket connections for real-time updates
- Display generated images from the `/static` endpoint
- Provide "Post to LinkedIn" functionality using the `/linkedin/post` endpoint
- Check LinkedIn integration status via `/linkedin/status`
- Handle CORS appropriately (currently configured for development)

### LinkedIn Frontend Integration
The frontend can integrate LinkedIn posting by:
1. Checking if LinkedIn is configured: `GET /linkedin/status`
2. Showing "Post to LinkedIn" button when content is generated
3. Posting content with image: `POST /linkedin/post`
4. Displaying success/error feedback to users
5. Optionally opening the LinkedIn post URL in a new tab






