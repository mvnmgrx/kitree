

from abc import ABC, abstractmethod

class GenericExporter(ABC):
    """Template class for any exporter"""

    @abstractmethod
    def Export(file_name: str, parts: list[str]) -> bool:
        """Export to the given format

        Args:
            file_name (str): Name the file that the exporter creates should have (without extention)
            parts (list[str]): List of part IPN of the currently active project

        Returns:
            bool: True if the file was exported correctly, otherwise false
        """
        pass