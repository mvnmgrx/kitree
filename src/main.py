"""KiTree - The glue between KiCad and InvenTree

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass, field
from typing import Optional
from misc.config import Config, Credentials
from misc.console import Console
from misc.commands import *
from misc.logger import Logger
from app import App

KiTreeVersion = 'v0.0-rc1'
KiTreeAuthor = '(C) Marvin Mager - @mvnmgrx - 2023'

if __name__ == "__main__":
    Logger.Init()
    app = App()
    app.config.load()
    app.console.print(f"KiTree CLI {KiTreeVersion} {KiTreeAuthor}")

    app.console.add_command("status", command_show_status)
    app.console.add_command("exit",   command_exit)
    app.console.add_command("load", command_load_project)
    
    # app.console.add_command("set master-part", SetMasterPart)
    # app.console.add_command("add", AddPart)
    # app.console.add_command("rm part", RemovePart)
    # app.console.add_command("rm all", RemoveAllParts)
    # app.console.add_command("list parts", ListParts)
    # app.console.add_command("list projects", ListKnownProjects)
    # app.console.add_command("build libs", BuildLibs)
    # app.console.add_command("build bom", BuildBom)
    # app.console.add_command("init", InitProject)
    app.console.add_command("help", command_help)
    app.console.add_command("log", command_show_log)
    
    while app.console.isRunning:
        app.console.process_input(app.console.read())



