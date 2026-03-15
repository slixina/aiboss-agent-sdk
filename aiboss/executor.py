from abc import ABC, abstractmethod
from typing import Dict, Any

class Executor(ABC):
    @property
    @abstractmethod
    def task_type(self) -> str:
        """The type of task this executor handles."""
        pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task and return the result."""
        pass
