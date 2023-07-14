from os import path
from typing import List
from app import App
from components.part import Part
from misc.colors import Color as C
from kiutils.board import Board
from kiutils.items.fpitems import FpText
from kiutils.footprint import Footprint
from misc.constants import KITREE_CONFIG_DIR, KITREE_KEYWORD_FP, KITREE_KEYWORD_FP_OLD
from misc.logger import Logger

from project.project import DescriptiveError

def command_parts(app: App, args: List[str]):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    if len(args) < 1:
        app.console.write("")
        app.console.write("part: Control the parts list of a project")
        app.console.write("")
        app.console.write("Usage:")
        app.console.write("  part list                Show the parts list")
        app.console.write("  part add                 Add a part to the parts list")
        app.console.write("  part rm <ipn>            Remove a part from the parts list")
        app.console.write("  part rm all              Remove all parts from the parts list")
        app.console.write("  part update              Update some property of a part (symbol, footprint, etc.)")
        app.console.write("")
        return
    
    if args[0] == "list": command_list_parts(app, args)
    elif args[0] == "add": command_add_part(app, args)
    elif args[0] == "rm": command_remove_part(app, args)
    elif args[0] == "update": command_update_part(app, args)
    else: app.console.write(f"{C.Fail}Unknown option!{C.End}")


def command_list_parts(app: App, args: List[str]):
    parts_list = app.project.get_parts_list()
    if len(parts_list) == 0:
        return app.console.write('No parts in project\'s part list!')

    app.console.inc()
    for part in parts_list:
        app.console.write(f'- { part }')
    app.console.dec()

def command_add_part(app: App, args: List[str]):
    if len(args) != 2:
        return app.console.write('Usage: part add [ IPN ]')

    try:
        app.project.add_part(args[1])
    except DescriptiveError as ex:
        app.console.write(ex)

def command_remove_part(app: App, args: List[str]):
    if len(args) != 2:
        app.console.write('Usage: part rm [ IPN | "all" ]')

    try:
        if args[1] == "all":
            app.console.write(f"{C.Warning}Are you sure? (y/n){C.End}")
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

def command_update_part(app: App, args: List[str]):
    if len(args) != 4:
        app.console.write('Usage: part update [ action ] [ IPN ] <args>')
        app.console.write("")
        app.console.write("Actions:")
        app.console.write("  - fp    : Update footprint from board. Args: <ref>")
        app.console.write("  - sym   : Update symbol from schematic. Args: <ref>")
        return

    action, partIpn, ref = args[1:]
    if not app.project.api.part_exists(partIpn):
        return app.console.write(f"{C.Fail}Part {partIpn} does not exist in InvenTree server!{C.End}")
    
    log = Logger.Create(__file__)
    if action == "fp":
        # Parse the board
        try:
            board = Board().from_file(path.join(app.project.path, f"{app.project.name}.kicad_pcb"))
        except Exception as ex:
            return app.console.write(f"{C.Fail}Could not parse board! {ex}{C.End}")
        
        fpToUpdate: Footprint = None
        attachmentOldName: str = None

        # Retrieve the footprint with the correct reference
        for fp in board.footprints:
            for item in fp.graphicItems:
                if isinstance(item, FpText):
                    if item.type == 'reference':
                        if item.text == ref:
                            fpToUpdate = fp
        if fpToUpdate is None:
            return app.console.write(f"{C.Fail}No footprint with ref {ref} found!{C.End}")

        # Footprint always on F.Cu
        fpToUpdate.layer = "F.Cu"

        # Remove all properties
        fpToUpdate.properties.clear()

        # # Sanitize pads
        # new_pads: List[Pad] = []
        # for pad in fpToUpdate.pads:
        #     new_pads.append(Pad(
        #         number=pad.number,
        #         type = pad.type,
        #         shape = pad.shape,
        #         position = pad.position,
        #         size = pad.size,
        #         layers = pad.layers,
        #         roundrectRatio = pad.roundrectRatio,
        #         tstamp = pad.tstamp
        #     ))
        # fpToUpdate.pads = new_pads

        # Check if some file with description "Footprint" is already present for partIpn
        # Delete it, if yes
        part = Part(partIpn=partIpn, api=app.project.api)

        if part.Attachments is not None:
            # Delete old Footprint (old) if present:
            for attachment in part.Attachments:
                if attachment.Comment == KITREE_KEYWORD_FP_OLD:
                    if not app.project.api.delete_attachment(attachment.ID):
                        return app.console.write(f"{C.Fail}Could not delete old attachment!{C.End}")

            for attachment in part.Attachments:
                if attachment.Comment == KITREE_KEYWORD_FP:
                    attachmentOldName = attachment.FileName
                    log.info(f"Deleting {attachment} ..")
                    app.project.api.update_attachment_comment(attachment.ID, 'Footprint (old)')
                    app.project.api.update_attachment_filename(attachment.ID, f"{attachmentOldName}.old")
                    break
            else:
                log.info(f"No footprint found in part {partIpn}, creating new one now ..")
        else:
            log.info(f"No attachments in {partIpn}, creating new footprint now ..")

        # Create a file from it
        attachmentName = f"{partIpn}.kicad_mod" if attachmentOldName is None else attachmentOldName
        attachmentPath = path.join(KITREE_CONFIG_DIR, attachmentName)
        fpToUpdate.to_file(filepath=attachmentPath)
        
        # Upload new footprint
        app.project.api.upload_attachment(partIpn, attachmentPath, KITREE_KEYWORD_FP)

        app.console.write(f"Successfully updated footprint of {partIpn}!")
    elif action == "sym":
        ...
    else:
        return app.console.write(f"{C.Fail}Unknown option!{C.End}")
