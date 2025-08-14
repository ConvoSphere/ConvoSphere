# Assistants vs Agents

## Summary
- Assistant: produces a direct answer using RAG and optional tool calls; no explicit multi-step planning.
- Agent: plans steps to achieve a goal (LLM-guided), executes and corrects steps, orchestrates tools, and returns a final result after execution.

## Differences
- Planning & Execution
  - Assistant: single-pass or short iterative answer generation
  - Agent: LLM-driven planning patterns (ReAct, Plan-Execute, Tree-of-Thought), configurable per agent with abort criteria (time, steps, no-progress, confidence)
- Tooling
  - Assistant: dynamic tool suggestion and execution within assistant pipeline
  - Agent: curated toolset in AgentConfig; orchestrates multiple tools across steps; MCP-first
- State & Memory
  - Assistant: assistant-managed context/memory
  - Agent: explicit per-conversation `agent_state`, status transitions, histories; memory transfer across handoffs
- Orchestration
  - Assistant: single pipeline
  - Agent: multi-agent workflows (handoff, collaboration: parallel/sequential/hierarchical)
- Observability & Governance
  - Assistant: engine-level runtime stats
  - Agent: detailed per-agent performance metrics, usage counters; policy hooks

## Similarities
- Share the same AI providers and assistant engine foundations
- Both can use tools (MCP-first), benefit from RAG and knowledge context
- Assistants can operate as Agents via the `AssistantAgentAdapter`

## When to use which?
- Use an Assistant when:
  - You need fast, context-aware answers (Q&A, summarization, quick drafting)
  - Minimal or no tool orchestration is required
- Use an Agent when:
  - The task requires goal-directed planning, tool chaining, corrections
  - You need measurable execution (steps, retries, abort criteria) and governance

## Planning Patterns (Agents)
- none: direct answer via assistant engine
- react: iterative think-act-observe, calling tools as needed
- plan_execute: produce a plan, then execute steps
- tree_of_thought: explore alternatives briefly, then choose a path

Configure per agent via:
- planning_strategy: none|react|plan_execute|tree_of_thought
- max_planning_steps: maximum iterations
- abort_criteria: max_time_seconds, max_steps, stop_on_tool_error, no_progress_iterations, confidence_threshold