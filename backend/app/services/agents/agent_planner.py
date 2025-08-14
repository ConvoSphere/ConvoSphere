"""
Agent Planner Service.

Provides LLM-guided planning strategies like ReAct, Plan-Execute, Tree-of-Thought.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from loguru import logger

from backend.app.schemas.agent import AgentAbortCriteria, AgentConfig
from backend.app.services.agents.agent_runner import AssistantAgentAdapter


@dataclass
class PlanStep:
    index: int
    thought: str
    action: str | None
    tool_name: str | None
    tool_args: dict[str, Any]
    observation: Any | None
    success: bool | None


@dataclass
class PlanResult:
    success: bool
    steps: list[PlanStep]
    final_output: str
    metadata: dict[str, Any]


class AgentPlannerService:
    def __init__(self):
        self.runner = AssistantAgentAdapter()

    async def run(
        self,
        *,
        strategy: Literal["react", "plan_execute", "tree_of_thought"],
        config: AgentConfig,
        conversation_id: str,
        user_id: str,
        user_goal: str,
    ) -> PlanResult:
        if strategy == "react":
            return await self._run_react(config, conversation_id, user_id, user_goal)
        if strategy == "plan_execute":
            return await self._run_plan_execute(
                config, conversation_id, user_id, user_goal
            )
        if strategy == "tree_of_thought":
            return await self._run_tree_of_thought(
                config, conversation_id, user_id, user_goal
            )
        raise ValueError(f"Unsupported strategy: {strategy}")

    async def _run_react(
        self,
        config: AgentConfig,
        conversation_id: str,
        user_id: str,
        user_goal: str,
    ) -> PlanResult:
        steps: list[PlanStep] = []
        abort = config.abort_criteria or AgentAbortCriteria()
        deadline = (
            datetime.now(UTC) + timedelta(seconds=abort.max_time_seconds or 3600)
            if abort.max_time_seconds
            else None
        )

        for idx in range(config.max_planning_steps):
            if deadline and datetime.now(UTC) > deadline:
                logger.info("Planner deadline reached, aborting")
                break

            # Prompt pattern for ReAct: Ask LLM to think then act (choose tool)
            thought_prompt = (
                f"You are planning step {idx + 1} to achieve the goal: {user_goal}.\n"
                f"Think step-by-step (concise). If a tool is needed, specify which and the exact arguments as JSON.\n"
                f"If no tool is needed, respond directly."
            )

            result = await self.runner.process_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message=thought_prompt,
                model=config.model,
                temperature=config.temperature,
                use_tools=True,
            )

            thought = result.get("content", "")
            tool_calls = result.get("tool_calls", []) or []

            if tool_calls:
                # Execute via underlying assistant adapter already handles tools
                observation = result.get("metadata", {}).get("tool_results")
                steps.append(
                    PlanStep(
                        index=idx,
                        thought=thought,
                        action="tool_call",
                        tool_name=tool_calls[0].get("name"),
                        tool_args=tool_calls[0].get("arguments", {}),
                        observation=observation,
                        success=True,
                    )
                )
            else:
                steps.append(
                    PlanStep(
                        index=idx,
                        thought=thought,
                        action="respond",
                        tool_name=None,
                        tool_args={},
                        observation=None,
                        success=True,
                    )
                )
                # If LLM produced a direct answer, consider goal reached
                return PlanResult(
                    success=True,
                    steps=steps,
                    final_output=thought,
                    metadata={"strategy": "react"},
                )

        # Fallback: summarize progress
        summary = "\n".join(s.thought for s in steps[-3:]) if steps else ""
        return PlanResult(
            success=bool(steps),
            steps=steps,
            final_output=summary or "No solution found within limits.",
            metadata={"strategy": "react", "exhausted": True},
        )

    async def _run_plan_execute(
        self,
        config: AgentConfig,
        conversation_id: str,
        user_id: str,
        user_goal: str,
    ) -> PlanResult:
        # Stub: simple two-phase plan then execute via runner
        plan_prompt = (
            f"Create a minimal plan to achieve: {user_goal}. Return numbered steps."
        )
        plan = await self.runner.process_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message=plan_prompt,
            model=config.model,
            temperature=config.temperature,
            use_tools=False,
        )
        execute_prompt = (
            f"Execute the plan above step-by-step. Use tools when needed and provide final result."
        )
        exec_result = await self.runner.process_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message=execute_prompt,
            model=config.model,
            temperature=config.temperature,
            use_tools=True,
        )
        steps = [
            PlanStep(0, plan.get("content", ""), "plan", None, {}, None, True),
            PlanStep(1, exec_result.get("content", ""), "execute", None, {}, None, True),
        ]
        return PlanResult(
            success=True,
            steps=steps,
            final_output=exec_result.get("content", ""),
            metadata={"strategy": "plan_execute"},
        )

    async def _run_tree_of_thought(
        self,
        config: AgentConfig,
        conversation_id: str,
        user_id: str,
        user_goal: str,
    ) -> PlanResult:
        # Stub: for brevity, use single-branch reasoning
        prompt = (
            f"Explore multiple solution paths briefly to achieve: {user_goal}. "
            f"Pick the best and provide the result. Use tools if necessary."
        )
        result = await self.runner.process_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message=prompt,
            model=config.model,
            temperature=config.temperature,
            use_tools=True,
        )
        steps = [
            PlanStep(0, result.get("content", ""), "tot", None, {}, None, True),
        ]
        return PlanResult(
            success=True,
            steps=steps,
            final_output=result.get("content", ""),
            metadata={"strategy": "tree_of_thought"},
        )


agent_planner = AgentPlannerService()