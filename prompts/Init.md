# Multi-Agent LangGraph + PydanticAI Project


## 🧠 FIRST STEP

**Read and review the `CLAUDE.md` file** to understand:
- Project scope and constraints  
- File structure and coding conventions  
- Exact library versions and API usage patterns  

---

## ✅ PROJECT REQUIREMENTS

- Use **Poetry** for environment and dependency management (`Python 3.10+`)
- Define all models using `Pydantic.BaseModel` with `Field(description=...)`
- Use `PydanticAI.Agent` objects with:
  - `model="openai:gpt-4o"`
  - `result_type` pointing to a valid Pydantic model
- ❌ Do **not** use deprecated decorators like `@aiconfig` or `ai()`
- Use **LangGraph** to orchestrate the flow from `ResearchAgent` → `ContentAgent`
- Follow **PEP 8**, keep functions ≤50 lines, and follow single-responsibility
- Prefer **pure functions** without side effects

---

## 🛠️ IMPLEMENTATION SEQUENCE

### `models/schema.py`
- Define:
  - `ResearchRequest`, `ResearchResponse`
  - `ContentRequest`, `ContentResponse`
- Use `BaseModel` with `Field(description=...)` and examples
- Follow the **latest PydanticAI syntax**

---

### `agents/research.py` & `agents/content.py`
- Create `Agent` instances:
  - Set `result_type` to the appropriate model
  - Use `.run_sync(...)` for execution
- Inputs and outputs must be in **dict format**

---

### `flow/graph.py`
- Build a LangGraph DAG:
