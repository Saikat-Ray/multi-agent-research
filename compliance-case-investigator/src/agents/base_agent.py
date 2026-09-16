"""
Base class for all agents.

Every agent wraps one or more "skills" (plain functions) and exposes a
single run(context) -> context method. The orchestrator only ever talks
to this interface, which is what makes agents pluggable: to add a new
agent, subclass BaseAgent, register it in AGENT_REGISTRY, and add it to
the orchestrator's pipeline (or route to it dynamically later).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take the shared case context, do this agent's job, and return the
        (possibly updated) context. Agents should only add keys, not
        silently overwrite what another agent wrote, so the orchestrator
        can reconstruct what happened for audit purposes.
        """
        raise NotImplementedError

    def log(self, context: Dict[str, Any], message: str) -> None:
        context.setdefault("trace", []).append(f"[{self.name}] {message}")
