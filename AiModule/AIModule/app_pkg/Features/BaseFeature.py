from abc import ABC, abstractmethod

class BaseFeature(ABC):

    @abstractmethod
    async def process(self):
        pass