"""KiTree - The glue between KiCad and InvenTree

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from app import App
from commands.board import command_board
from commands.build import command_build
from commands.exit import command_exit
from commands.export import command_export
from commands.parts import command_parts
from commands.help import command_help
from commands.misc import command_show_log
from commands.projects import command_project
from misc.constants import KITREE_AUTHOR, KITREE_VERSION
from misc.logger import Logger

if __name__ == "__main__":
    Logger.Init()
    app = App()
    app.config.load()
    app.console.print(f"KiTree CLI {KITREE_VERSION} {KITREE_AUTHOR}")

    app.console.add_command("project", command_project)
    app.console.add_command("part", command_parts)
    app.console.add_command("build", command_build)
    app.console.add_command("exit", command_exit)
    app.console.add_command("help", command_help)
    app.console.add_command("log", command_show_log)
    app.console.add_command("export", command_export)
    app.console.add_command("board", command_board)

    while app.console.isRunning:
        app.console.process_input(app.console.read())
