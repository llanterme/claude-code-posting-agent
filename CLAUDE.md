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

# Multi-Agent LLM System

A multi-agent LLM system that automates content generation using typed models, LangGraph orchestration, and OpenAI completions. This system uses a pipeline of specialized agents to research a topic, transform that research into platform-optimized content

## Features

- **Research Agent**: Generates 5-7 factual bullet points on a given topic
- **Content Agent**: Creates platform-specific content based on research with appropriate tone
- **LangGraph orchestration**: Structured workflow between agents
- **PydanticAI**: Strong typing and structured LLM outputs

## Core Technologies

| Library        | Version     | Purpose                                                           |
|----------------|-------------|-------------------------------------------------------------------|
| PydanticAI     | 0.2.15      | Declarative prompt modeling & structured LLM output parsing       |
| LangGraph      | 0.4.8       | DAG-style multi-agent orchestration                              |
| OpenAI SDK     | 1.84.0      | Call GPT-4o and other models through API endpoints               |
| Logfire        | 3.18.0      | Structured tracing and logging for all prompt/response cycles    |
| Poetry         | 1.8.4       | Dependency, packaging, and virtualenv management                 |


## Project Structure
.
├── agents/           # Agent implementations
│   ├── research.py   # ResearchAgent using PydanticAI
│   ├── content.py    # ContentAgent using PydanticAI
├── flow/             # LangGraph workflow
│   └── graph.py      # Agent orchestration graph
├── models/           # Typed models
│   └── schema.py     # Pydantic models for agent I/O
├── utils/            # Utility modules
│   ├── logging.py    # Logfire integration for structured logging
├── main.py           # CLI entrypoint
├── pyproject.toml    # Poetry configuration



