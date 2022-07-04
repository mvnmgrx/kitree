"""KiTree - The glue between KiCad and InvenTree

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from misc.config import Config
from misc.logger import Logger
from misc.console import Console
from misc.commands import *

from api.inventree import ITApi

KiTreeVersion = 'v0.0-rc1'
KiTreeAuthor = '(C) Marvin Mager - @mvnmgrx - 2022'

credentials = {
    "username": "",
    "password": "",
    "domain": ""
}

if __name__ == "__main__":
    Logger.Init()
    Config.Load()

    Console.Print(f'KiTree CLI {KiTreeVersion} {KiTreeAuthor}')

    ITApi.Connect(credentials)
    Console.AddCommand("status", ShowStatus)
    Console.AddCommand("exit", Exit)
    Console.AddCommand("set master-part", SetMasterPart)
    Console.AddCommand("add", AddPart)
    Console.AddCommand("rm part", RemovePart)
    Console.AddCommand("rm all", RemoveAllParts)
    Console.AddCommand("list parts", ListParts)
    Console.AddCommand("list projects", ListKnownProjects)
    Console.AddCommand("build libs", BuildLibs)
    Console.AddCommand("build bom", BuildBom)
    Console.AddCommand("load", LoadProject)
    Console.AddCommand("init", InitProject)
    Console.AddCommand("help", GetHelp)
    Console.AddCommand("log", ShowLog)
    
    while Console.IsRunning:
        Console.ProcessInput(Console.In())



