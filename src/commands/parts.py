from typing import List
from app import App
from misc.colors import Color
from project.project import DescriptiveError

def command_parts(app: App, args: List[str]):
    if len(args) < 1:
        app.console.write("")
        app.console.write("part: Control the parts list of a project")
        app.console.write("")
        app.console.write("Usage:")
        app.console.write("  part list                Show the parts list")
        app.console.write("  part add                 Add a part to the parts list")
        app.console.write("  part rm <ipn>            Remove a part from the parts list")
        app.console.write("  part rm all              Remove all parts from the parts list")
        app.console.write("")
        return
    
    if args[0] == "list": command_list_parts(app, args)
    elif args[0] == "add": command_add_part(app, args)
    elif args[0] == "rm": command_remove_part(app, args)
    else: app.console.write(f"{Color.Fail}Unknown option!{Color.End}")


def command_list_parts(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    parts_list = app.project.get_parts_list()
    if len(parts_list) == 0:
        return app.console.write('No parts in project\'s part list!')

    app.console.inc()
    for part in parts_list:
        app.console.write(f'- { part }')
    app.console.dec()

def command_add_part(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) != 2:
        return app.console.write('Usage: part add [ IPN ]')

    try:
        app.project.add_part(args[1])
    except DescriptiveError as ex:
        app.console.write(ex)

def command_remove_part(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) != 2:
        app.console.write('Usage: part rm [ IPN | "all" ]')

    try:
        if args[1] == "all":
            app.console.write(f"{Color.Warning}Are you sure? (y/n){Color.End}")
            app.console.inc()
            input = app.console.read()
            app.console.dec()
            if input == "y":
                app.project.remove_all_parts()
                app.console.write("Parts list cleared!")
            else:
                app.console.write("Maybe next time ..")
        else:
            app.project.remove_part(args[1])
    except DescriptiveError as ex:
        app.console.write(ex)