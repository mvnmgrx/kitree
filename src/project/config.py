"""Project configuration 

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import json
from datetime import date
from dataclasses import dataclass

from misc.logger import Logger
from misc.types import Credentials

@dataclass
class ProjectConfig():
    """This class represents a KiTree project config (.kitree file) in a KiCad
       project folder. It provides a basic abstraction from the JSON syntax in 
       the file.
    """
    Data = {}
    Data["CreatedDate"] = str(date.today())
    Data["LastEditedDate"] = str(date.today())
    Data["InventreeCredentials"] = { 
        "Username": "", 
        "Password": "",
        "Domain": ""
    }
    Data["MasterPart"] = None
    Data["Parts"] = []
    Log = Logger.Create(__name__)
    FilePath: str | None = None

    def Load(self, filepath: str) -> bool:
        """Load a project config file from the given path-like object and sets the file path 
        attribute as given. This attribute can then be used for successive calls to `Save`
        without a parameter given.

        Args:
            filepath (str): Path-like object to the .kitree file

        Returns:
            bool: True if the file was loaded correctly, otherwise False
        """
        try:
            with open(filepath) as infile:
                self.Data = json.load(infile)
                self.Log.info(f'Loaded project config from { filepath }')
                self.FilePath = filepath
            self.Log.info(f'Loading project configuration from {filepath} was successfull')
 
        except Exception as ex:
            self.Log.error(f'Failed to load project config file at { filepath }!')
            self.Log.debug(f'Exception: { ex }')
            return False
        return True

    def Save(self, filepath: str) -> bool:
        """Save a project's config to the file given as a path-like object

        Args:
            filepath (str): Path-like object to the .kitree file

        Returns:
            bool: True if the file was written successful, otherwise False
        """
        if filepath is None:
            if self.FilePath is not None:
                filepath = self.FilePath
            else:
                self.Log.error('Failed to load project config file! No path given or set.')
                return False
        try:
            with open(filepath, 'w') as outfile:
                self.Data["LastEditedDate"] = str(date.today())
                json.dump(self.Data, outfile, indent=4)
            self.Log.info(f'Saved project configuration to {filepath} was successfull')
        except Exception as ex:
            self.Log.error(f'Failed to save project config file at { filepath }!')
            self.Log.debug(f'Exception: { ex }')
            return False
        return True

    def SetMasterPart(self, masterPart: str):
        self.Data["MasterPart"] = masterPart

    def GetMasterPart(self, ) -> str:
        return self.Data["MasterPart"]

    def SetPartsList(self, partsList: list):
        self.Data["Parts"] = partsList
        
    def GetPartsList(self) -> list:
        return self.Data["Parts"]

    def GetShortName(self) -> str:
        return self.Data["ShortName"]

    def GetFullName(self) -> str:
        return self.Data["FullName"]

    def SetInventreeCredentials(self, creds: Credentials):
        self.Data["InventreeCredentials"]["Username"] = creds.Username
        self.Data["InventreeCredentials"]["Password"] = creds.Password
        self.Data["InventreeCredentials"]["Domain"] = creds.Domain

    def GetInventreeCredentials(self) -> Credentials:
        return Credentials(
            self.Data["InventreeCredentials"]["Username"], 
            self.Data["InventreeCredentials"]["Password"],
            self.Data["InventreeCredentials"]["Domain"]
        )