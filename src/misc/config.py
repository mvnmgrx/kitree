"""Configuration file wrapper

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import json
import marshmallow_dataclass

from dataclasses import dataclass, field
from os import path, makedirs
from typing import List, Optional
from components.data import Credentials, KnownProject

from misc.logger import Logger

@dataclass
class ConfigData():
    """Class containing all configuration data that shall be exists in the config file"""

    inventreeCredentials: List[Credentials] = field(default_factory=list)
    """List of credentials used to authenticate to InvenTree servers to"""

    lastLoadedProject: str = ""
    """Name of the project that was loaded last"""

    knownProjects: List[KnownProject] = field(default_factory=list)
    """Projects known to kitree"""

class Config():
    """Static class managing and representing the config file"""

    path = path.join(path.expanduser('~'), '.kitree', 'config.json')
    """Path to the global configuration file"""

    data = ConfigData()
    """Configuration data for kitree"""

    dataSchema = marshmallow_dataclass.class_schema(ConfigData)()
    """Data schema of the config data class used for serialization/deserialization"""

    log = Logger.Create(__name__)
    """Logger for the Config() class"""

    def load(self):
        """Load data from the config file or creates it if it does not exist yet.

        See:
            - self.path - Path to config file
        """
        if not path.exists(self.path):
            self.save()

        with open(self.path) as json_file:
            content = json.load(json_file)
            self.data = self.dataSchema.load(content)

        self.log.info(f'Config file at {self.path} loaded successfully')

    def save(self):
        """Save data to the config file

        See:
            - self.path - Path to config file
        """
        # Check if config directory exists
        if not path.exists(path.dirname(self.path)):
            self.log.warning(f"Config directory at {self.path} missing, creating it now ..")
            makedirs(path.dirname(self.path))

        # Write to the file
        with open(self.path, 'w') as outfile:
            content = self.dataSchema.dump(self.data)
            bytes_written = outfile.write(json.dumps(content, indent=4))

        self.log.info(f'Saved configuration to {self.path} was successfull ({bytes_written} bytes written)')

    def add_known_project(self, name: str, path: str):
        """Add a project to the list of known projects and saves the config to disk

        Args:
            - name (str): Name of the project
            - path (str): Path to the project's KiCad root directory
        """
        if self.is_known_project(name):
            self.log.debug(f'Project "{name}" already known')
        else:
            self.log.debug(f'Adding project "{name}" at {path} to list of known objects')
            self.data.knownProjects.append(KnownProject(name=name, path=path))
            self.save()

    def is_known_project(self, name: str) -> bool:
        """Check if a project (not a path) is on the list of known projects

        Args:
            - name (str): Name of the project

        Returns:
            - bool: True if the project is on the list of known projects, otherwise False.
        """
        for project in self.data.knownProjects:
            if project.name == name:
                return True
        return False
    
    def set_last_loaded_project_name(self, name: str):
        self.data.lastLoadedProject = name
        self.save()

    def get_known_project_path(self, name: str) -> Optional[str]:
        """Get the path to the KiCad root folder of a given project

        Args:
            - name (str): Name of the project

        Returns:
            - str: None if either the config file is not loaded or the project is not on the list 
                   of known projects. Otherwise the path to the KiCad root folder of the project.
        """
        for project in self.data.knownProjects:
            if project.name == name:
                return project.path

        self.log.warning(f'Project {name} not known!')
        return None

    def get_last_known_project_name(self) -> str:
        """Get the name of the last known project

        Returns:
            - str: Name of the last known project or an empty string, if no project was ever opened
        """
        return self.data.lastLoadedProject

    def get_credentials_from_id(self, id: str) -> Optional[Credentials]:
        for credential in self.data.inventreeCredentials:
            if credential.id == id:
                return credential
        return None

    def get_known_projects(self) -> List[KnownProject]:
        return self.data.knownProjects
    
    def get_known_servers(self) -> List[str]:
        ret: List[str] = []
        for cred in self.data.inventreeCredentials:
            ret.append(cred.id)
        return ret
