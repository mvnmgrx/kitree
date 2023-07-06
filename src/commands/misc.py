from typing import List
from app import App

def command_show_log(app: App, args: List[str]):
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
