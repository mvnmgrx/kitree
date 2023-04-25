"""KiTree - The glue between KiCad and InvenTree

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from app import App
from commands.build import command_build_bom, command_build_libs
from commands.exit import command_exit
from commands.parts import command_add_part, command_list_parts, command_remove_part
from commands.help import command_help
from commands.misc import command_show_log
from commands.projects import command_show_status, command_init_project, command_load_project, \
                              command_list_known_projects
from misc.logger import Logger

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
    app.console.add_command("list parts", command_list_parts)
    app.console.add_command("help", command_help)
    app.console.add_command("log", command_show_log)
    app.console.add_command("list projects", command_list_known_projects)
    app.console.add_command("add", command_add_part)
    app.console.add_command("rm part", command_remove_part)
    app.console.add_command("init", command_init_project)
    app.console.add_command("build libs", command_build_libs)
    app.console.add_command("build bom", command_build_bom)
    
    # app.console.add_command("set master-part", SetMasterPart)
    # app.console.add_command("rm all", RemoveAllParts)
    
    while app.console.isRunning:
        app.console.process_input(app.console.read())



