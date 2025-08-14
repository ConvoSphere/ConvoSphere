# Agent Implementation: End-to-end Integration

## Overview

The agent implementation provides a modular multi-agent architecture with handoffs, collaboration, state, performance tracking, and MCP-first tool integration. Assistants can also operate as agents via a unified runner/adapter, while agents additionally support LLM-driven planning strategies (ReAct, Plan-Execute, Tree-of-Thought) configurable per agent with abort criteria.

## Components

### 1. Backend Services

- AgentService (`backend/app/services/agent_service.py`)
  - Agent CRUD facade over the modular `AgentManager`
  - Handoff, collaboration, performance, and state retrieval
- AgentManager (`backend/app/services/agents/agent_manager.py`)
  - Registry, State, Handoff, Collaboration, Performance services
  - Integrates the Agent Planner and the AssistantAgentAdapter runner
- Agent Planner (`backend/app/services/agents/agent_planner.py`)
  - LLM-guided strategies: `react`, `plan_execute`, `tree_of_thought`
  - Configurable per agent (`planning_strategy`, `max_planning_steps`, `abort_criteria`)
- Assistant Engine (`backend/app/services/assistants/assistant_engine.py`)
  - Hybrid mode support (chat/agent), RAG integration, tool execution, memory
  - Exposed to agents via `AssistantAgentAdapter` (`agent_runner.py`)
- Tooling
  - Enhanced executor (`tool_executor_v2`) with typed request/result and caching
  - MCP client/manager (`backend/app/tools/mcp_tool.py`)
  - WebSearch (SearxNG preferred) tool (`backend/app/tools/search_tools.py`)

### 2. API Endpoints

- Agents (`backend/app/api/v1/endpoints/agents.py`)
  - `GET /api/v1/agents/` — list agents (includes planning fields)
  - `POST /api/v1/agents/` — create agent
  - `PUT /api/v1/agents/{agent_id}` — update agent (supports nested `abort_criteria`)
  - `DELETE /api/v1/agents/{agent_id}` — delete agent
  - `POST /api/v1/agents/handoff` — handoff
  - `POST /api/v1/agents/collaborate` — collaboration
  - `GET /api/v1/agents/{id}/performance` — performance metrics
  - `GET /api/v1/agents/{id}/state` — state
- MCP (`backend/app/api/v1/endpoints/mcp.py`)
  - Manage MCP servers, list tools, execute tools

### 3. Schemas & Validation

- `backend/app/schemas/agent.py`
  - `AgentConfig` extended with `planning_strategy`, `max_planning_steps`, `abort_criteria`
  - `AgentAbortCriteria`: max_time_seconds, max_steps, stop_on_tool_error, no_progress_iterations, confidence_threshold
  - `AgentState` string IDs and extended statuses

### 4. Frontend

- Agent Management (`frontend-react/src/components/agents/AgentManagement.tsx`)
  - Create/Edit form includes planning strategy, max steps, abort criteria
  - Planning strategy visible in table
- Tools UI
  - MCP Server Manager (`components/mcp/McpServerManager.tsx`) integrated in `pages/tools/Tools.tsx`
  - Tool Execution (`pages/tools/ToolExecution.tsx`) exposes WebSearch params (top_k, time_range, lang, site, safe_mode, sources)

### 5. Persistence

- New model: `backend/app/models/agent.py` (optional DB persistence of agent configs)
- Alembic migration: `backend/alembic/versions/2025_08_14_add_agents_table.py`

## Assistants vs Agents

### Primary Difference
- Assistant: produces a direct answer using RAG and optional tool calls; no explicit multi-step planning.
- Agent: plans steps to achieve a goal (LLM-guided), executes and corrects steps, orchestrates tools, and produces a final result after execution.

### Detailed Comparison
- Scope
  - Assistant: a response-generation pipeline (hybrid chat/agent mode)
  - Agent: an operational, governable entity with identity, lifecycle, and metrics
- Planning & Execution
  - Assistant: no explicit planning loop
  - Agent: LLM planning strategies (ReAct, Plan-Execute, ToT) with abort criteria and iteration control
- Tooling
  - Assistant: dynamic tool suggestion and execution via assistant pipeline
  - Agent: curated toolset in `AgentConfig`; planning loop orchestrates tools across steps; MCP-first integration
- State & Memory
  - Assistant: assistant-managed memory and context
  - Agent: explicit `agent_state` per conversation, status transitions, histories, memory transfer across handoffs
- Orchestration
  - Assistant: single pipeline
  - Agent: multi-agent workflows: handoff, collaboration (parallel/sequential/hierarchical)
- Observability & Governance
  - Assistant: engine-level runtime stats
  - Agent: detailed performance metrics (`agent_performance`), usage counters, policies (planned)

### Similarities
- Both use the same underlying AI services and model providers
- Both can execute tools; both benefit from RAG and knowledge context
- Assistants can operate as Agents via `AssistantAgentAdapter` (shared runner interface)

## Planning Strategies
- `none`: direct assistant response via `AssistantAgentAdapter`
- `react`: iterative “think-act-observe” with tool calls when needed
- `plan_execute`: produce a plan, then execute steps
- `tree_of_thought`: explore alternatives briefly, then choose best path

Each strategy is configurable per agent via:
- `planning_strategy`: none|react|plan_execute|tree_of_thought
- `max_planning_steps`: maximum planning iterations
- `abort_criteria`: timing, max steps, error/quality thresholds

## MCP-first Tooling
- SearxNG WebSearch (`web_search`) with params: query, top_k, time_range, lang, site, safe_mode, sources
- MCP server management API and UI; local tools remain as fallback

## Usage Examples

### Creating an Agent with Planning
```python
from backend.app.services.agent_service import AgentService
from backend.app.schemas.agent import AgentCreate, AgentConfig, AgentAbortCriteria

agent_config = AgentConfig(
    name="Research Agent",
    description="Plans and executes web research",
    system_prompt="You are a rigorous research planner.",
    tools=["web_search"],
    model="gpt-4",
    temperature=0.3,
    planning_strategy="react",
    max_planning_steps=8,
    abort_criteria=AgentAbortCriteria(max_time_seconds=180, max_steps=8, no_progress_iterations=2),
)

agent_create = AgentCreate(
    config=agent_config,
    user_id=user_id,
    is_public=False,
)

service = AgentService()
agent = await service.create_agent(agent_create)
```

### Running a Multi-Agent Collaboration
```python
from backend.app.schemas.agent import AgentCollaborationRequest

req = AgentCollaborationRequest(
    agent_ids=["research_agent", "code_expert"],
    conversation_id=conversation_id,
    user_id=user_id,
    collaboration_type="parallel",
    coordination_strategy="expertise",
)
result = await service.start_collaboration(req)
```

## Monitoring & Performance
- Per-agent metrics: response time, success rate, tokens, errors, satisfaction
- Conversation-level summary and trends

## Security & Validation
- Pydantic v2 schemas and validators
- RBAC-ready, input sanitization, structured error handling

## Next Steps
- Persist agent CRUD fully via DB model (optional), retire in-memory registry
- Policy-driven routing and richer self-correction/critic loops
- MCP tool discovery prioritization and typed schema propagation to UI