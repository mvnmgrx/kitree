"""Project-specific stuff

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from os import listdir, path
from genericpath import isdir, isfile

from api.inventree import ITApi
from misc.logger import Logger
from misc.types import Credentials
from project.config import ProjectConfig

class Project():
    Path = ""
    Name = ""
    Loaded = False
    CreatedDate = "" # str(date.today())
    EditedDate = "" # str(date.today())
    Inventree = ""# Credentials()
    MasterPart = None
    Parts = []
    Log = Logger.Create(__name__)
    Config = ProjectConfig()
    ItCredentials = Credentials()

    @staticmethod
    def Load(thePath: str) -> bool:
        filepath = path.join(thePath, ".kitree")
        projectName = ""

        # Check if the given path is a directory
        if not isdir(thePath):
            Project.Log.error(f'Path to {thePath} is not a directory!')
            return False

        # Check if a KiCad project is present in given folder
        try:
            files = [f for f in listdir(thePath) if isfile(path.join(thePath, f))]
        except Exception as ex:
            Project.Log.error(f'Could not locate KiCad project at {thePath}!')
            Project.Log.debug(f'Exception: {ex}')
            return False

        for file in files:
            if file.find('.kicad_pro') != -1:
                projectName = file.removesuffix('.kicad_pro')
                Project.Log.info(f'Found KiCad project {projectName}.kicad_pro')
                break
        else:
            Project.Log.error(f'No KiCad project found at {thePath}!')
            return False

        # Check and load .kitree project file
        if not isfile(filepath):
            Project.Log.error(f'No KiTree project file at {thePath} found!')
            return False

        if not Project.Config.Load(filepath):
            Project.Log.error(f'Could not load KiTree project at { filepath }')
            return False

        
        Project.Name = projectName
        Project.Path = thePath
        # TODO: Let project config take part of this all ..
        Project.Parts = Project.Config.GetPartsList()
        Project.MasterPart = Project.Config.GetMasterPart()
        Project.ItCredentials = Project.Config.GetInventreeCredentials()
        Project.Log.info(f'Successfully loaded project "{ Project.Name }"')
        Project.Loaded = True
        return True
        
    @staticmethod
    def Save():
        Project.Config.SetMasterPart(Project.MasterPart)
        Project.Config.SetPartsList(Project.Parts)
        Project.Config.SetInventreeCredentials(Project.ItCredentials)
        if not Project.Config.Save(path.join(Project.Path, '.kitree')):
            Project.Log.error(f'Could not save KiTree project at { Project.Path }')
            return False
        return True

    def RemovePart(partIpn: str) -> bool:
        """Removes a part from the project's part list, if it is found in 
           said list.

        Args:
            partIpn (str): Part to remove from part list

        Returns:
            bool: True if removed, otherwise False if not found
        """
        if partIpn in Project.Parts:
            Project.Parts.remove(partIpn)
            return True

        return False

    def AddPart(partIpn: str) -> bool:
        """Adds a part to the projects part list

        Args:
            partIpn (str): IPN of part to add

        Returns:
            bool: True if the part was added, False if it is already in the project's
                  part list or if it is not found in Inventree database
        """
        if partIpn in Project.Parts:
            Project.Log.warning(f'Part { partIpn } does already exist in project\'s part list')
            return False

        if not ITApi.PartExists(partIpn):
            Project.Log.warning(f'Part { partIpn } does not exist in Inventree database!')
            return False

        Project.Parts.append(partIpn)
        Project.Log.info(f'Added part { partIpn } to project\'s part list')
        return True