"""
Async Processing Pipeline for background task management.

This module provides an async processing pipeline with task queues,
priority management, and background task execution.
"""

import asyncio
import time
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import ConfigurationError


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class TaskStatus(Enum):
    """Task status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskType(Enum):
    """Task type definitions."""
    MESSAGE_PROCESSING = "message_processing"
    AI_RESPONSE_GENERATION = "ai_response_generation"
    TOOL_EXECUTION = "tool_execution"
    CACHE_UPDATE = "cache_update"
    NOTIFICATION = "notification"
    DATA_SYNC = "data_sync"
    CLEANUP = "cleanup"


class TaskRequest(BaseModel):
    """Task request with validation."""

    task_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique task ID")
    task_type: TaskType = Field(..., description="Task type")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    payload: dict[str, Any] = Field(default_factory=dict, description="Task payload")
    user_id: str | None = Field(None, description="User ID")
    conversation_id: str | None = Field(None, description="Conversation ID")
    timeout: float = Field(default=300.0, ge=1.0, le=3600.0, description="Timeout in seconds")
    retry_count: int = Field(default=0, ge=0, le=5, description="Retry count")
    scheduled_at: datetime | None = Field(None, description="Scheduled execution time")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate task ID."""
        if not v or not v.strip():
            raise ValueError("Task ID cannot be empty")
        return v.strip()

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate task payload."""
        if not isinstance(v, dict):
            raise ValueError("Payload must be a dictionary")
        return v

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class TaskResult(BaseModel):
    """Task execution result."""

    task_id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Task status")
    result: Any | None = Field(None, description="Task result")
    error: str | None = Field(None, description="Error message")
    start_time: datetime | None = Field(None, description="Start time")
    end_time: datetime | None = Field(None, description="End time")
    execution_time: float | None = Field(None, ge=0, description="Execution time in seconds")
    retry_count: int = Field(default=0, ge=0, description="Actual retry count")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class TaskInfo(BaseModel):
    """Task information for monitoring."""

    task_id: str = Field(..., description="Task ID")
    task_type: TaskType = Field(..., description="Task type")
    priority: TaskPriority = Field(..., description="Task priority")
    status: TaskStatus = Field(..., description="Task status")
    created_at: datetime = Field(..., description="Creation timestamp")
    scheduled_at: datetime | None = Field(None, description="Scheduled time")
    started_at: datetime | None = Field(None, description="Start time")
    completed_at: datetime | None = Field(None, description="Completion time")
    user_id: str | None = Field(None, description="User ID")
    conversation_id: str | None = Field(None, description="Conversation ID")
    execution_time: float | None = Field(None, description="Execution time")
    retry_count: int = Field(default=0, description="Retry count")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class TaskHandler:
    """Task handler with execution logic."""

    def __init__(self, name: str, handler_func: Callable, max_concurrent: int = 1):
        self.name = name
        self.handler_func = handler_func
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks: dict[str, asyncio.Task] = {}

    async def execute(self, task_request: TaskRequest) -> TaskResult:
        """Execute task with concurrency control."""
        async with self.semaphore:
            return await self._execute_internal(task_request)

    async def _execute_internal(self, task_request: TaskRequest) -> TaskResult:
        """Internal task execution."""
        task_result = TaskResult(
            task_id=task_request.task_id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            # Execute handler function
            result = await self.handler_func(task_request.payload)

            task_result.status = TaskStatus.COMPLETED
            task_result.result = result
            task_result.end_time = datetime.now()
            task_result.execution_time = (task_result.end_time - task_result.start_time).total_seconds()

            logger.info(f"Task {task_request.task_id} completed successfully in {task_result.execution_time:.2f}s")

        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.end_time = datetime.now()
            task_result.execution_time = (task_result.end_time - task_result.start_time).total_seconds()

            logger.error(f"Task {task_request.task_id} failed: {e}")

        return task_result


class PriorityQueue:
    """Priority queue for task management."""

    def __init__(self):
        self.queues: dict[TaskPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in TaskPriority
        }
        self.task_info: dict[str, TaskInfo] = {}

    async def put(self, task_request: TaskRequest) -> None:
        """Add task to priority queue."""
        # Create task info
        task_info = TaskInfo(
            task_id=task_request.task_id,
            task_type=task_request.task_type,
            priority=task_request.priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            scheduled_at=task_request.scheduled_at,
            user_id=task_request.user_id,
            conversation_id=task_request.conversation_id,
        )

        self.task_info[task_request.task_id] = task_info

        # Add to appropriate queue
        await self.queues[task_request.priority].put(task_request)

        logger.debug(f"Task {task_request.task_id} added to queue with priority {task_request.priority.name}")

    async def get(self) -> TaskRequest | None:
        """Get next task from highest priority queue."""
        # Check queues in priority order (highest first)
        for priority in reversed(list(TaskPriority)):
            queue = self.queues[priority]
            if not queue.empty():
                task_request = await queue.get()

                # Update task info
                if task_request.task_id in self.task_info:
                    self.task_info[task_request.task_id].status = TaskStatus.RUNNING
                    self.task_info[task_request.task_id].started_at = datetime.now()

                return task_request

        return None

    def get_task_info(self, task_id: str) -> TaskInfo | None:
        """Get task information."""
        return self.task_info.get(task_id)

    def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics."""
        stats = {}
        for priority in TaskPriority:
            queue = self.queues[priority]
            stats[priority.name] = {
                "size": queue.qsize(),
                "priority": priority.value,
            }

        # Add overall stats
        total_pending = sum(stats[p.name]["size"] for p in TaskPriority)
        stats["total_pending"] = total_pending
        stats["total_tasks"] = len(self.task_info)

        return stats


class AsyncProcessor:
    """Main async processing pipeline."""

    def __init__(self, max_workers: int = 10, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.priority_queue = PriorityQueue()
        self.task_handlers: dict[TaskType, TaskHandler] = {}
        self.workers: list[asyncio.Task] = []
        self.running = False
        self.stats = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "tasks_completed": 0,
            "average_processing_time": 0.0,
        }

    def register_handler(
        self,
        task_type: TaskType,
        handler_func: Callable,
        max_concurrent: int = 1,
    ) -> None:
        """Register task handler."""
        handler = TaskHandler(task_type.value, handler_func, max_concurrent)
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type.value}")

    async def start(self) -> None:
        """Start the processing pipeline."""
        if self.running:
            logger.warning("Async processor is already running")
            return

        self.running = True

        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)

        logger.info(f"Started async processor with {self.max_workers} workers")

    async def stop(self) -> None:
        """Stop the processing pipeline."""
        if not self.running:
            return

        self.running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("Async processor stopped")

    async def _worker(self, worker_name: str) -> None:
        """Worker task for processing tasks."""
        logger.info(f"Worker {worker_name} started")

        while self.running:
            try:
                # Get next task
                task_request = await self.priority_queue.get()
                if task_request is None:
                    await asyncio.sleep(0.1)  # Small delay if no tasks
                    continue

                # Process task
                await self._process_task(task_request, worker_name)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Delay on error

        logger.info(f"Worker {worker_name} stopped")

    async def _process_task(self, task_request: TaskRequest, worker_name: str) -> None:
        """Process a single task."""
        logger.debug(f"Worker {worker_name} processing task {task_request.task_id}")

        # Get handler
        handler = self.task_handlers.get(task_request.task_type)
        if not handler:
            logger.error(f"No handler registered for task type: {task_request.task_type}")
            return

        # Execute task
        time.time()
        try:
            task_result = await handler.execute(task_request)

            # Update statistics
            self.stats["tasks_processed"] += 1
            if task_result.status == TaskStatus.COMPLETED:
                self.stats["tasks_completed"] += 1
            else:
                self.stats["tasks_failed"] += 1

            # Update average processing time
            execution_time = task_result.execution_time or 0
            current_avg = self.stats["average_processing_time"]
            total_tasks = self.stats["tasks_processed"]
            self.stats["average_processing_time"] = (
                (current_avg * (total_tasks - 1) + execution_time) / total_tasks
            )

            # Update task info
            if task_request.task_id in self.priority_queue.task_info:
                task_info = self.priority_queue.task_info[task_request.task_id]
                task_info.status = task_result.status
                task_info.completed_at = task_result.end_time
                task_info.execution_time = task_result.execution_time
                task_info.retry_count = task_result.retry_count

        except Exception as e:
            logger.error(f"Task {task_request.task_id} processing failed: {e}")
            self.stats["tasks_failed"] += 1

    async def submit_task(self, task_request: TaskRequest) -> str:
        """Submit task for processing."""
        if not self.running:
            raise ConfigurationError("Async processor is not running")

        # Check queue size
        queue_stats = self.priority_queue.get_queue_stats()
        if queue_stats["total_pending"] >= self.max_queue_size:
            raise ConfigurationError("Task queue is full")

        # Add to queue
        await self.priority_queue.put(task_request)

        logger.info(f"Task {task_request.task_id} submitted with priority {task_request.priority.name}")
        return task_request.task_id

    async def submit_batch(self, task_requests: list[TaskRequest]) -> list[str]:
        """Submit multiple tasks for processing."""
        task_ids = []
        for task_request in task_requests:
            task_id = await self.submit_task(task_request)
            task_ids.append(task_id)
        return task_ids

    def get_task_status(self, task_id: str) -> TaskInfo | None:
        """Get task status."""
        return self.priority_queue.get_task_info(task_id)

    def get_stats(self) -> dict[str, Any]:
        """Get processing statistics."""
        queue_stats = self.priority_queue.get_queue_stats()

        return {
            **self.stats,
            "queue_stats": queue_stats,
            "active_workers": len([w for w in self.workers if not w.done()]),
            "total_workers": self.max_workers,
            "running": self.running,
        }

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        # This would need to be implemented with a more sophisticated queue
        # For now, we just mark it as cancelled in the task info
        task_info = self.priority_queue.get_task_info(task_id)
        if task_info and task_info.status == TaskStatus.PENDING:
            task_info.status = TaskStatus.CANCELLED
            return True
        return False

    async def clear_queue(self, task_type: TaskType | None = None) -> int:
        """Clear pending tasks from queue."""
        # This is a simplified implementation
        # In a real system, you'd need to handle this more carefully
        cleared_count = 0

        for priority in TaskPriority:
            queue = self.priority_queue.queues[priority]
            while not queue.empty():
                try:
                    task_request = queue.get_nowait()
                    if task_type is None or task_request.task_type == task_type:
                        cleared_count += 1
                        # Mark as cancelled
                        if task_request.task_id in self.priority_queue.task_info:
                            self.priority_queue.task_info[task_request.task_id].status = TaskStatus.CANCELLED
                except asyncio.QueueEmpty:
                    break

        logger.info(f"Cleared {cleared_count} tasks from queue")
        return cleared_count


# Global async processor instance
async_processor = AsyncProcessor(max_workers=10, max_queue_size=1000)


# Example task handlers
async def message_processing_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Example handler for message processing tasks."""
    message = payload.get("message", "")
    user_id = payload.get("user_id", "")

    # Simulate processing
    await asyncio.sleep(0.1)

    return {
        "processed": True,
        "message_length": len(message),
        "user_id": user_id,
    }


async def ai_response_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Example handler for AI response generation tasks."""
    message = payload.get("message", "")
    model = payload.get("model", "gpt-4")

    # Simulate AI processing
    await asyncio.sleep(0.5)

    return {
        "response": f"AI response to: {message}",
        "model": model,
        "tokens_used": len(message.split()),
    }


async def tool_execution_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Example handler for tool execution tasks."""
    tool_name = payload.get("tool_name", "")
    arguments = payload.get("arguments", {})

    # Simulate tool execution
    await asyncio.sleep(0.2)

    return {
        "tool_name": tool_name,
        "result": f"Tool {tool_name} executed with arguments: {arguments}",
        "success": True,
    }


async def cache_update_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Example handler for cache update tasks."""
    cache_key = payload.get("cache_key", "")
    data = payload.get("data", {})

    # Simulate cache update
    await asyncio.sleep(0.05)

    return {
        "cache_key": cache_key,
        "updated": True,
        "data_size": len(str(data)),
    }


# Initialize default handlers
def initialize_default_handlers():
    """Initialize default task handlers."""
    async_processor.register_handler(
        TaskType.MESSAGE_PROCESSING,
        message_processing_handler,
        max_concurrent=5,
    )

    async_processor.register_handler(
        TaskType.AI_RESPONSE_GENERATION,
        ai_response_handler,
        max_concurrent=3,
    )

    async_processor.register_handler(
        TaskType.TOOL_EXECUTION,
        tool_execution_handler,
        max_concurrent=10,
    )

    async_processor.register_handler(
        TaskType.CACHE_UPDATE,
        cache_update_handler,
        max_concurrent=20,
    )

    logger.info("Default task handlers initialized")
