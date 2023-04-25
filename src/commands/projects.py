from genericpath import isfile
from os import listdir, path
from app import App
from misc.colors import Color
from project.project import ApiConnectionError, DescriptiveError, InvalidServerIdError, NoProjectFileError, \
                            ProjectLoadError, ProjectNotFoundError

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

def command_list_known_projects(app: App, args: list):
    projects = app.config.get_known_projects()
    if len(projects) == 0:
        return app.console.write("No projects known!")

    for project in projects:
        if project.name == app.config.get_last_known_project_name():
            app.console.write(f' - {project.name} at {project.path} {Color.OkBlue}<last>')
        else:
            app.console.write(f' - {project.name} at {project.path}')

def command_init_project(app: App, args: list):
    if app.project.isLoaded:
        return app.console.write("A project is already loaded!")

    if len(args) != 2:
        return app.console.write('Usage: init [ path ] [ inventree-server-id ]')

    # Check if a KiCad project exists at the given path
    suppliedPath = args[0]
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

    try: 
    # Initialize KiTree project
        app.project.set_server_id(args[1])
        app.config.set_last_loaded_project_name(projectName)
        app.config.add_known_project(projectName, suppliedPath)
        app.project.path = suppliedPath
        app.project.save()
        app.console.write(f'Project "{projectName}" successfully initialized! Use "load last" to load it')
    except DescriptiveError as ex:
        app.console.write(f'{Color.Fail}{ex}{Color.End}')

def command_show_status(app: App, args: list):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    app.console.write(f'Project "{ app.project.name }" loaded')
    app.console.write(f'  🌐 Path: {Color.OkBlue}{ app.project.path }')
    if app.project.get_master_part() is None:
        app.console.write(f'  ⭐ Master IPN: undefined')
    else:
        app.console.write(f'  ⭐ Master IPN: {Color.Bold}{app.project.get_master_part()}')
