from typing import List

from app import App
from export.exporter import get_exporters
from misc.colors import Color as C

def command_export(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write(f"{C.Fail}No project loaded!{C.End}")

    if len(args) < 1:
        app.console.write("")
        app.console.write("export: Export project with kitree")
        app.console.write("")
        app.console.write("Usage:")
        app.console.write("  export <exporter>        Export the project using the given exporter")
        app.console.write("")
        app.console.write("Exporters:")
        for name, exporter in get_exporters().items():
            app.console.write(f"  {name} - {exporter.get_description()}")
        app.console.write("")
        return

    if args[0] in get_exporters().keys():
        get_exporters()[args[0]].export(app, args[1:])
    else: app.console.write(f"{C.Fail}Unknown option!{C.End}")
