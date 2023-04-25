from app import App
from project.project import DescriptiveError

def command_list_parts(app: App, args: list):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    parts_list = app.project.get_parts_list()
    if len(parts_list) == 0:
        return app.console.write('No parts in project\'s part list!')

    app.console.inc()
    for part in parts_list:
        app.console.write(f'- { part }')
    app.console.dec()

def command_add_part(app: App, args: list):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) == 0:
        return app.console.write('Usage: add [ IPN ]')

    try:
        app.project.add_part(args[0])
    except DescriptiveError as ex:
        app.console.write(ex)

def command_remove_part(app: App, args: list):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) == 0:
        return app.console.write('Usage: rm [ IPN ]')

    try:
        app.project.remove_part(args[0])
    except DescriptiveError as ex:
        app.console.write(ex)