from genericpath import isfile
from os import listdir, path
from typing import List

from prettytable import PrettyTable
from app import App
from misc.colors import Color
from project.project import ApiConnectionError, DescriptiveError, InvalidServerIdError, NoProjectFileError, \
                            ProjectLoadError, ProjectNotFoundError

def command_project(app: App, args: List[str]):
    if len(args) < 1:
        app.console.write("")
        app.console.write("project: Control project-related stuff")
        app.console.write("")
        app.console.write("Usage:")
        app.console.write("  project list             List all projects known to kitree")
        app.console.write("  project init             Initialize a new project")
        app.console.write("  project load last        Load the last project")
        app.console.write("  project load <name>      Load an already known project using its name")
        app.console.write("  project load <path>      Load an existing project at given path")
        app.console.write("  project status           Information about the current active project")
        app.console.write("  project set <option>     Set some option in the project")
        app.console.write("")
        return
        
    if args[0] == "load": command_load_project(app, args)
    elif args[0] == "init": command_init_project(app, args)
    elif args[0] == "status": command_show_status(app, args)
    elif args[0] == "list": command_list_known_projects(app, args)
    elif args[0] == "set": command_project_set(app, args)
    else: app.console.write(f"{Color.Fail}Unknown option!{Color.End}")

def command_load_project(app: App, args: List[str]):
    if len(args) != 2:
        return app.console.write('Usage: load [ last / <name> / <path> ]')

    path = None

    if args[1] == "last":
        lastProject = app.config.get_last_known_project_name()
        if lastProject == "":
            return app.console.write('No last project known!')

        path = app.config.get_known_project_path(lastProject)
        if path is None:
            return app.console.write('No path to known project known!')

        app.console.log.info(f'Using path "{path}" for last known project "{lastProject}"')

    else:
        # Check if the given argument is a known project, otherwise use it as path
        # for Project.Load()
        path = app.config.get_known_project_path(args[1])
        if path is None:
            path = args[1]
            app.console.log.info(f'Given argument is no known project. Using "{path}" as path')
        else:
            app.console.log.info(f'Using "{path}" as path for known project {args[1]}')

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
    except ApiConnectionError as ex:
        app.console.write(f"Could not connect to InvenTree server at {ex}!")

def command_list_known_projects(app: App, args: List[str]):
    projects = app.config.get_known_projects()
    if len(projects) == 0:
        return app.console.write("No projects known!")

    t = PrettyTable()
    t.field_names = ["Name", "Path", "Status"]
    t.align = "l"
    for project in projects:
        row = [ f"{Color.Bold}{project.name}{Color.End}", project.path ]
        if project.name == app.config.get_last_known_project_name():
            row.append(f"{Color.OkBlue}<last>{Color.End}")
        else:
            row.append("")
        t.add_row(row)

    app.console.print("\n")
    for row in t.get_string().split("\n"):
        app.console.write(row)

def command_init_project(app: App, args: List[str]):
    if app.project.isLoaded:
        return app.console.write("A project is already loaded!")

    if len(args) != 3:
        return app.console.write('Usage: project init [ path ] [ inventree-server-id ]')

    # Check if a KiCad project exists at the given path
    suppliedPath = args[1]
    files = [f for f in listdir(suppliedPath) if isfile(path.join(suppliedPath, f))]
    for file in files:
        if '.kicad_pro' in file:
            projectName = file.removesuffix('.kicad_pro')
            projectPath = path.join(suppliedPath, file)
            app.console.write(f'Found valid KiCad project "{projectName}"')
            break
    else:
        return app.console.write(f'{Color.Fail}No valid KiCad project found at this location!')

    if isfile(path.join(projectPath, '.kitree')):
        return app.console.write(f'Project is already initialized! Use "load" instead..')

    # TODO: Check if server ID is known to kitree

    try: 
    # Initialize KiTree project
        app.project.set_server_id(args[2])
        app.config.set_last_loaded_project_name(projectName)
        app.config.add_known_project(projectName, suppliedPath)
        app.project.path = suppliedPath
        app.project.save()
        app.console.write(f'Project "{projectName}" successfully initialized! Use "project load last" to load it')
    except DescriptiveError as ex:
        app.console.write(f'{Color.Fail}{ex}{Color.End}')

def command_show_status(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    app.console.write(f'Project "{ app.project.name }" loaded')
    app.console.write(f'  🌐 Path: {Color.OkBlue}{ app.project.path }')
    if app.project.get_master_part() is None:
        app.console.write(f'  ⭐ Master IPN: undefined')
    else:
        app.console.write(f'  ⭐ Master IPN: {Color.Bold}{app.project.get_master_part()}')

def command_project_set(app: App, args: List[str]):
    if len(args) < 2:
        app.console.write("Usage:")
        app.console.write("  project set master       Change the master-part of the active project")
        app.console.write("  project set server-id    Change the InvenTree server ID")
        app.console.write("")
        return
        
    if args[1] == "master": command_set_master_part(app, args)
    elif args[1] == "server-id": command_set_server_id(app, args)
    else: app.console.write(f"{Color.Fail}Unknown option!{Color.End}")

def command_set_master_part(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) != 3:
        return app.console.write('Usage: project set master [ IPN ]')

    master_part = args[2]

    if not app.project.api.part_exists(master_part):
        return app.console.write(f'Part {master_part} does not exist in Inventree!')

    app.project.set_master_part(master_part)
    app.console.log.info(f'Changed master-part of {app.project.name} to {master_part}')
    app.console.write(f'Master-part of "{app.project.name}" set to {master_part}')

def command_set_server_id(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) != 3:
        return app.console.write('Usage: project set server-id [ server-id ]')

    server_id = args[2]

    # TODO: Check if this server ID is known to kitree

    app.project.set_server_id(server_id)
    app.console.log.info(f'Changed server-id of {app.project.name} to {server_id}')
    app.console.write(f'Server ID of "{app.project.name}" set to {server_id}')