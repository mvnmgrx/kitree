"""Project-specific stuff

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass, field
from os import listdir, path
from genericpath import isdir, isfile
from typing import TYPE_CHECKING

from api.inventree import InvenTreeApi
from misc.logger import Logger
from project.config import ProjectConfig

if TYPE_CHECKING:
    from app import App

class ProjectNotFoundError(Exception): pass
class NoProjectFileError(Exception): pass
class ProjectLoadError(Exception): pass
class InvalidServerIdError(Exception): pass
class ApiConnectionError(Exception): pass

@dataclass
class Project():
    path: str = ""
    name: str = ""
    isLoaded: bool = False
    log = Logger.Create(__name__)
    config: ProjectConfig = field(default_factory=lambda: ProjectConfig())
    api: InvenTreeApi = field(default_factory=lambda: InvenTreeApi())
    parent_app = None

    def load(self, thePath: str) -> bool:
        filepath = path.join(thePath, ".kitree")
        projectName = ""

        # Check if the given path is a directory
        if not isdir(thePath):
            self.log.error(f'Path to {thePath} is not a directory!')
            raise ProjectNotFoundError("Path is not a directory")

        # Check if a KiCad project is present in given folder
        files = [f for f in listdir(thePath) if isfile(path.join(thePath, f))]
        for file in files:
            if file.find('.kicad_pro') != -1:
                projectName = file.removesuffix('.kicad_pro')
                self.log.info(f'Found KiCad project {projectName}.kicad_pro')
                break
        else:
            self.log.error(f'No KiCad project found at {thePath}!')
            raise ProjectNotFoundError("No KiCad project found")

        # Check and load .kitree project file
        if not isfile(filepath):
            self.log.error(f'No KiTree project file at {thePath} found!')
            raise NoProjectFileError()

        if not self.config.load(filepath):
            self.log.error(f'Could not load KiTree project at { filepath }')
            raise ProjectLoadError()
        
        # Check if a server is configured
        credentials = self.parent_app.config.get_credentials_from_id(self.config.data.inventreeServerId)
        if credentials is None:
            self.log.error(f'Could not find InvenTree server ID "{self.config.data.inventreeServerId}" in configured servers!')
            raise InvalidServerIdError(self.config.data.inventreeServerId)

        if not self.api.connect(credentials):
            self.log.error(f'Could not connect to InvenTree server at {credentials.domain}')
            raise ApiConnectionError(credentials.domain)

        self.name = projectName
        self.path = thePath
        self.log.info(f'Successfully loaded project "{ self.name }"')
        self.isLoaded = True
        return True
        
    def save(self):
        if not self.config.save(path.join(Project.path, '.kitree')):
            self.log.error(f'Could not save KiTree project at { Project.path }')
            return False
        return True

    def get_master_part(self) -> str:
        return self.config.data.masterPart