from os import path
from typing import List
from kiutils.board import Board

from app import App
from misc.colors import Color as C

def command_board(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) < 1:
        app.console.write("")
        app.console.write("board: Manipulate the PCB using kitree")
        app.console.write("")
        app.console.write("Usage:")
        app.console.write("  board hide               Hide stuff on the board")
        app.console.write("")
        return
    
    if args[0] == "hide": command_board_hide(app, args)
    else: app.console.write(f"Unknown option!", color=C.Fail)

def command_board_hide(app: App, args: List[str]):
    if len(args) != 2:
        app.console.write('Usage: board hide [ action ]')
        app.console.write("")
        app.console.write("Actions:")
        app.console.write("  - dnp : Removes graphic elements of DNP components from fab layers")
        app.console.write("")
        return
    
    if args[1] == "dnp":
        # FIXME: This puts all disabled footprints reference and values on F.SilkScreen
        # Parse the board
        try:
            board = Board.from_file(path.join(app.project.path, f"{app.project.name}.kicad_pcb"))
        except Exception as ex:
            return app.console.write(f"Could not parse board! {ex}", color=C.Fail)
        
        # Hide all graphic items and 3d models of footprints that are marked DNP
        for fp in board.footprints:
            if fp.attributes.excludeFromBom:
                fp.graphicItems = [
                    x for x in fp.graphicItems if (not ("Fab" in x.layer))
                ]

                for model in fp.models:
                    model.hide = True

        board.to_file()                    

    else: app.console.write(f"Unknown option!", color=C.Fail)