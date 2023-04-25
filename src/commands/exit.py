from app import App

def command_exit(app: App, args: list):
    app.console.write('Goodbye!')
    exit()