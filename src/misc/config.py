"""Configuration file wrapper

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""


import json
from types import NoneType

from misc.logger import Logger

class Config():
    """Static class managing and representing the config file
    """
    Path = 'kitree-cfg.json'        ## Path to config file
    Data = {}                       ## Data of the config file
    Loaded = False                  ## Flag if the config was loaded
    Log = Logger.Create(__name__)

    @staticmethod
    def Load() -> bool:
        """Load data from the config file

        Returns:
            bool: True if the file was loaded and parsed correctly. Otherwise False

        See:
            Config.Path - Path to config file
        """
        try:
            with open(Config.Path) as json_file:
                Config.Data = json.load(json_file)
            Config.Loaded = True
            Config.Log.info(f'Config file at {Config.Path} loaded successfully')
            return True
        except Exception as ex:
            Config.Log.error(f'Failed to parse config file! Exception: {ex}')
            return False

    @staticmethod
    def Save() -> bool:
        """Save data to the config file

        Returns:
            bool: True if the file was saved correctly. Otherwise False

        See:
            Config.Path - Path to config file
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')
            return False

        try:
            with open(Config.Path, 'w') as outfile:
                json.dump(Config.Data, outfile, indent=4)
            Config.Log.info(f'Saved configuration to {Config.Path} was successfull')
            return True
        except Exception as ex:
            Config.Log.error(f'Failed to save config file! Exception: {ex}')
        return False

    ##
    # Verifys the config file to make sure all dict entries are there
    # \return false, if at least one dict entry is missing. Otherwise true
    @staticmethod
    def Verify() -> bool:
        # TODO: Write verification function
        return True

    @staticmethod
    def AddKnownProject(name: str, path: str) -> bool:
        """Add a project to the list of known projects

        Args:
            name (str): Name of the project
            path (str): Path to the project's KiCad root directory

        Returns:
            bool: True if the project was added to the list and saved to 
                  the config file, as well as if the project was already 
                  on the list of known projects. Otherwise False
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')
            return False
        
        if name in Config.Data["KnownProjects"].keys():
            Config.Log.debug(f'Project "{name}" already known')
            return True
        else:    
            Config.Log.debug(f'Adding project "{name}" at {path} to list of known objects')
            Config.Data["KnownProjects"].update({name: path})
            return Config.Save()

    @staticmethod
    def GetKnownProjects() -> dict:
        """Get a list of known projects as a dict of key-value pairs

        Returns:
            dict: Empty dict if the config file was not loaded yet. Otherwise a dict 
                  of known projects with the name as keys and the path as values
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')
            return {}

        return Config.Data["KnownProjects"]

    @staticmethod
    def IsKnownProject(project: str) -> bool:
        """Check if a project (not a path) is on the list of known projects

        Args:
            project (str): Name of the project

        Returns:
            bool: True if the project is on the lsit of known projects, otherwise False
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')
            return False

        return project in Config.Data["KnownProjects"].keys()

    @staticmethod
    def GetKnownProjectPath(project: str) -> str:
        """Get the path to the KiCad root folder of a given project

        Args:
            project (str): Name of the project

        Returns:
            str: None if either the config file is not loaded or the project is not on 
                 the list of known projects. Otherwise the path to the KiCad root folder
                 of the project
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')
            return None

        if not Config.IsKnownProject(project):
            Config.Log.warning(f'Project {project} not known!')
            return None

        return Config.Data["KnownProjects"][project]

    @staticmethod
    def SetLastProject(project: str):
        """Set the name of the last used project

        Args:
            project (str): Name of the project
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')

        Config.Data["LastProject"] = project
        Config.Save()

    @staticmethod
    def GetLastProject() -> str:
        """Get the name of the last project

        Returns:
            str: None if the last project is not known. Otherwise the name of the project
        """
        if not Config.Loaded:
            Config.Log.warning(f'Config file not loaded!')
            return None
            
        if Config.Data["LastProject"] is NoneType:
            return None
        return Config.Data["LastProject"]
