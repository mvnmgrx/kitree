"""Project configuration

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import json
import marshmallow_dataclass

from os import path
from datetime import date
from dataclasses import dataclass, field
from typing import List, Optional

from misc.logger import Logger

@dataclass
class ProjectConfigData():
    createdDate: str = str(date.today())
    """Date on which the KiTree project was created"""

    lastEditedDate: str = str(date.today())
    """Date on which the KiTree project was last edited"""

    inventreeServerId: Optional[str] = None
    """ID of the InvenTree server to use (has to be configured on the client's KiTree to work)"""

    masterPart: Optional[str] = None
    """IPN of the master part this project uses"""

    parts: List[str] = field(default_factory=list)
    """List of part IPNs this project uses"""

@dataclass
class ProjectConfig():
    """This class represents a KiTree project config (.kitree file) in a KiCad project folder. It
    provides a basic abstraction from the JSON syntax in the file.
    """

    data: ProjectConfigData = field(default_factory=lambda: ProjectConfigData)
    """Configuration data of the project"""

    dataSchema = marshmallow_dataclass.class_schema(ProjectConfigData)()
    """Data schema of the project config data class used for serialization/deserialization"""

    log = Logger.Create(__name__)
    """Logger of this project config"""

    filePath: Optional[str] = None
    """Path to the project"""

    def load(self, filepath: str) -> bool:
        """Load a project config file from the given path-like object and sets the file path
        attribute as given. This attribute can then be used for successive calls to `Save`
        without a parameter given.

        Args:
            - filepath (str): Path-like object to the .kitree file

        Returns:
            - bool: True if the file was loaded correctly, otherwise False
        """
        if not path.exists(filepath):
            self.log.error(f'No project config at {filepath} found!')
            return False

        with open(filepath) as infile:
            content = json.load(infile)
            self.data = self.dataSchema.load(content)
            self.filePath = filepath
        
        self.log.info(f'Loading project configuration from {filepath} was successfull')
        return True

    def save(self, filepath: Optional[str] = None) -> bool:
        """Save a project's config to the file given as a path-like object

        Args:
            - filepath (str): Path-like object to the .kitree file

        Returns:
            - bool: True if the file was written successful, otherwise False
        """
        if filepath is None:
            if self.filePath is not None:
                filepath = self.filePath
            else:
                self.log.error('Failed to load project config file! No path given or set.')
                return False

        with open(filepath, 'w') as outfile:
            self.data.lastEditedDate = str(date.today())            
            content = self.dataSchema.dump(self.data)
            bytes_written = outfile.write(json.dumps(content, indent=4))

        self.log.info(f'Saved project configuration to {filepath} was successfull ({bytes_written} bytes written)')
        return True
