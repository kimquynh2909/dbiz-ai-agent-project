"""Lightweight shared state to let agents exchange context during a run."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from contextvars import ContextVar


@dataclass
class AgentState:
    conversation_id: Optional[str] = None
    user: Optional[str] = None
    user_question: Optional[str] = None
    retry_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)

    def set(self, key: str, value: Any) -> "AgentState":
        self.context[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)

    def update_context(self, **kwargs) -> "AgentState":
        self.context.update(kwargs)
        return self

    def set_user_question(self, question: str) -> "AgentState":
        """Store the latest user input for downstream tools/agents."""
        self.user_question = question
        return self

    def increment_retry(self, step: int = 1) -> int:
        """Increase retry counter and return new value."""
        self.retry_count += max(1, step)
        return self.retry_count

    def reset_retry(self) -> "AgentState":
        self.retry_count = 0
        return self

    def add_tool_result(self, result: Dict[str, Any]) -> "AgentState":
        if isinstance(result, dict):
            self.tool_results.append(result)
        return self


current_agent_state: ContextVar[Optional[AgentState]] = ContextVar(
    "current_agent_state", default=None
)


def get_state(create: bool = True) -> Optional[AgentState]:
    state = current_agent_state.get()
    if state is None and create:
        state = AgentState()
        current_agent_state.set(state)
    return state


def set_state(state: Optional[AgentState]) -> Optional[AgentState]:
    current_agent_state.set(state)
    return state


def clear_state() -> None:
    current_agent_state.set(None)
