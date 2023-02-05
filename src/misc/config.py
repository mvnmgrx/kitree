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
from typing import List

from misc.logger import Logger

@dataclass
class Credentials():
    """Simple credential store"""

    id: str = ""
    """Identifier of the credential"""

    username: str = ""
    """The username to use for login"""

    password: str = ""
    """The password to use for login"""

    domain: str = ""
    """The domain to authenticate to"""

@dataclass
class KnownProject():
    """A project known to kitree"""

    name: str = ""
    """Name of the project"""

    path: str = ""
    """Path to the project"""

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

    def load():
        """Load data from the config file or creates it if it does not exist yet.

        See:
            - Config.path - Path to config file
        """
        if not path.exists(Config.path):
            Config.save()

        with open(Config.path) as json_file:
            content = json.load(json_file)
            Config.data = Config.dataSchema.load(content)

        Config.log.info(f'Config file at {Config.path} loaded successfully')

    @staticmethod
    def save():
        """Save data to the config file

        See:
            - Config.path - Path to config file
        """
        # Check if config directory exists
        if not path.exists(path.dirname(Config.path)):
            Config.log.warning(f"Config directory at {Config.path} missing, creating it now ..")
            makedirs(path.dirname(Config.path))

        # Write to the file
        with open(Config.path, 'w') as outfile:
            content = Config.dataSchema.dump(Config.data)
            bytes_written = outfile.write(json.dumps(content, indent=4))

        Config.log.info(f'Saved configuration to {Config.path} was successfull ({bytes_written} bytes written)')

    @staticmethod
    def add_known_project(name: str, path: str):
        """Add a project to the list of known projects and saves the config to disk

        Args:
            - name (str): Name of the project
            - path (str): Path to the project's KiCad root directory
        """
        if Config.is_known_project(name):
            Config.log.debug(f'Project "{name}" already known')
        else:
            Config.log.debug(f'Adding project "{name}" at {path} to list of known objects')
            Config.data.knownProjects.append(KnownProject(name=name, path=path))

    @staticmethod
    def is_known_project(name: str) -> bool:
        """Check if a project (not a path) is on the list of known projects

        Args:
            - name (str): Name of the project

        Returns:
            - bool: True if the project is on the list of known projects, otherwise False.
        """
        for project in Config.data.knownProjects:
            if project.name == name:
                return True
        return False

    @staticmethod
    def get_known_project_path(name: str) -> str:
        """Get the path to the KiCad root folder of a given project

        Args:
            - name (str): Name of the project

        Returns:
            - str: None if either the config file is not loaded or the project is not on the list 
                   of known projects. Otherwise the path to the KiCad root folder of the project.
        """
        for project in Config.data.knownProjects:
            if project.name == name:
                return project.path

        Config.log.warning(f'Project {project} not known!')
        return None

