from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class CareerAgent(ABC):
    """
    Base Agent Interface for all agents in the AI-Powered Agentic Career Guidance System (ACGS).
    Every specialized agent (Self-Assessment, Market Intelligence, Skill Gap, Roadmap, Feasibility)
    implements this contract.
    """

    agent_name: str = "BaseCareerAgent"
    description: str = "Base interface for career guidance agents"

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incoming input data and extract key signals/features."""
        pass

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through agent logic, memory, or LLM reasoning."""
        pass

    @abstractmethod
    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize and format final structured output."""
        pass
