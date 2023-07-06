from abc import ABC, abstractmethod
from typing import List

from app import App

class GenericExporter(ABC):
    """Template class for any exporter"""

    @abstractmethod
    def export(self, app: App, args: List[str]) -> bool:
        """Export to the given format
        
        Args:
            - ``app``: The kitree application
            - ``args``: List of remaining arguments entered through the console
        
        Returns:
            - True if the file was exported correctly, otherwise false
        """
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> bool:
        """Get the description of the exporter"""
        raise NotImplementedError