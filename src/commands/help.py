from typing import List
from app import App
from misc.colors import Color

def command_help(app: App, args: List[str]):
    return app.console.write(f'{Color.Warning}Not yet implemented..')