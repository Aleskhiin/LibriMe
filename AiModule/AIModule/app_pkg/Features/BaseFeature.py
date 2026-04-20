from abc import ABC, abstractmethod
from typing import Any


class BaseFeature(ABC):
    """
    Abstract base class for asynchronous feature implementations.

    All concrete feature classes must implement the `process` method.
    """

    @abstractmethod
    async def process(self) -> Any:
        """
        Executes the feature's main logic.

        This method must be implemented by all subclasses and
        should contain the asynchronous processing logic of the feature.

        Returns:
            Any: The result of the feature execution.
        """
        pass