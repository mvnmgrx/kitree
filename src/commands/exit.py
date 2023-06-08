from typing import List
from app import App

def command_exit(app: App, args: List[str]):
    app.console.write('Goodbye!')
    exit()