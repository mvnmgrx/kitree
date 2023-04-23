"""Commands of the KiTree CLI

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from collections import namedtuple
from genericpath import isfile
from os import listdir, makedirs, path, rmdir, unlink
from shutil import copy
import time

from kiutils.items.common import Coordinate, Position, Property
from kiutils.footprint import Footprint, Model
from kiutils.schematic import Schematic
from kiutils.libraries import LibTable, Library
from kiutils.symbol import Symbol, SymbolLib

from components.part import Part
from misc.colors import Color
from misc.console import Console
from misc.config import Config
from project.project import ApiConnectionError, InvalidServerIdError, NoProjectFileError, Project, ProjectLoadError, ProjectNotFoundError
from api.inventree import InvenTreeApi

from main import App

def command_show_status(app: App, args: list):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    app.console.write(f'Project "{ app.project.name }" loaded')
    app.console.write(f'  🌐 Path: {Color.OkBlue}{ app.project.path }')
    if app.project.get_master_part is None:
        app.console.write(f'  ⭐ Master IPN: undefined')
    else:
        app.console.write(f'  ⭐ Master IPN: {Color.Bold}{app.project.get_master_part()}')

def command_exit(app: App, args: list):
    app.console.write('Goodbye!')
    exit()

def command_load_project(app: App, args: list):
    if len(args) == 0:
        return app.console.write('Usage: load [ last / <name> / <path> ]')

    path = None

    if args[0] == "last":
        lastProject = app.config.get_last_known_project_name()
        if lastProject == "":
            return app.console.write('No last project known!')

        path = app.config.get_known_project_path(lastProject)
        if path is None:
            return app.console.write('No path to known project known!')

        app.console.log.info(f'Using path "{ path }" for last known project "{ lastProject }"')

    else:
        # Check if the given argument is a known project, otherwise use it as path
        # for Project.Load()
        path = app.config.get_known_project_path(args[0])
        if path is None:
            path = args[0]
            app.console.log.info(f'Given argument is no known project. Using "{ path }" as path')
        else:
            app.console.log.info(f'Using "{ path }" as path for known project { args[0] }')

    try:
        app.project.load(path)
        app.console.write(f'Successfully loaded project \'{app.project.name}\'')
        app.config.set_last_loaded_project_name(app.project.name)
        app.config.add_known_project(app.project.name, app.project.path)
    except ProjectNotFoundError as ex:
        app.console.write(f"No project was found! {ex}.")
    except NoProjectFileError:
        app.console.write("No .kitree project file found! Use <init> to initialize a new project.")
    except ProjectLoadError:
        app.console.write(f"Error while loading project .kitree file! Check log for more info.")
    except InvalidServerIdError as ex:
        app.console.write(f"Project server id '{ex}' not found in configured InvenTree servers!")
    except ApiConnectionError:
        app.console.write(f"Could not connect to InvenTree server at {ex}!")

def command_help(app: App, args: list):
    return app.console.write(f'{Color.Warning}Not yet implemented..')

def command_show_log(app: App, args: list):
    level = 'DEBUG' if len(args) == 0 else args[0]
    numLines = 5 if len(args) < 2 else int(args[1])

    app.console.write(f'Showing last {numLines} lines of the logfile..')

    with open('kitree.log', 'r') as logfile:
        lines = logfile.readlines()
        lines.reverse()
        counter = 0
        for line in lines:
            if counter > numLines:
                break
            if level != 'DEBUG' and level not in line:
                continue
            app.console.write(f'{line}', newline=False)
            counter = counter + 1