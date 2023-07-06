import csv
from datetime import datetime
from os import path
from typing import List
from kiutils.board import Board
from app import App
from misc.constants import KITREE_VERSION

from misc.logger import Logger
from misc.colors import Color as C
from misc.tools import enumerate_board
from components.part import Part
from export.templates import GenericExporter

class JlcAssemblyBom(GenericExporter):
    """Class that implements the JLC BOM export functionality"""

    log = Logger.Create(__name__)
    """The logger of the JlcAssembly class"""

    def get_description(self) -> bool:
        """Get the description of the exporter"""
        return "JLCPCB assembly bill of materials (BOM)"

    def export(self, app: App, args: List[str]) -> bool:
        if len(args) == 0:
            app.console.write('Usage: export jlc_assembly_bom [ output_folder ]')
            return False
        
        csv_file_name = path.join(args[0], f'{app.project.name}_jlc_bom.csv')
        self.log.info(f'Starting JLCPCB BOM export to {csv_file_name}..')
        try:
            with open(csv_file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csv_writer.writerow([f';Exported with KiTree {KITREE_VERSION} at {datetime.now()}'])
                csv_writer.writerow([f';Project name: {app.project.name}'])
                csv_writer.writerow([f'sep=,'])
                csv_writer.writerow(["MPN", "Comment", "Designator", "Footprint", "JLCPCB Part #"])

                # Open KiCad project schematic
                app.console.write('Parsing KiCad board .. ', newline=False)
                boardPath = path.join(app.project.path, f'{app.project.name}.kicad_pcb')
                try:
                    board = Board().from_file(boardPath)
                    app.console.append(f'{C.OkGreen}Done!')
                except Exception as ex:
                    self.log.error(f'Could not parse board of project "{app.project.name}" at {boardPath}!')
                    self.log.debug(f'Exception: {str(ex)}')
                    app.console.append(f'{C.Fail}Failed!')
                    return False

                # Enumerate parts in schematic
                app.console.write('Enumerating KiCad board .. ', newline=False)
                enumerated_parts = {}
                enumerated_parts = enumerate_board(app, board, use_tht=False)
                app.console.append(f'{C.OkGreen}Done!')
                app.console.write('Found the following parts:')
                app.console.inc()
                for part in enumerated_parts.keys():
                    app.console.write(f'- {C.Bold}{part}{C.End}: {", ".join(enumerated_parts[part])}')
                app.console.dec()

                for partIpn in enumerated_parts.keys():
                    app.console.write(f'Processing {partIpn} ..', newline=False)

                    # Get part information from API
                    if not app.project.api.part_exists(partIpn):
                        self.log.error(f'Part {partIpn} not found on InvenTree server ..')
                        app.console.append(f'{C.Fail}Not available in InvenTree!')
                        continue

                    part = Part(app.project.api, partIpn)
                    manufacturerPartOfIntrest = None
                    supplierPartOfIntrest = None

                    # Check if a manufacturer part with JLC/LCSC as vendor is available
                    for manufacturerPart in part.ManufacturerParts:
                        for supplierPart in manufacturerPart.SupplierParts:
                            # Check each supplier part to be a LCSC or JLCPCB supplier
                            if supplierPart.Supplier.Name != 'LCSC' and \
                               supplierPart.Supplier.Name != 'JLCPCB':
                               continue

                            # This manufacturer part is the first to have LCSC or JLCPCB as 
                            # a vendor. Use it then
                            manufacturerPartOfIntrest = manufacturerPart
                            supplierPartOfIntrest = supplierPart
                            break
                        if manufacturerPartOfIntrest is not None:
                            # A manufacturer part of intrest was found, break the outer loop here
                            break
                    else:
                        app.console.write(f'{C.Warning}No JLCPCB part! Skipping ..')
                        self.log.warning(f'No part with JLCPCB supplier found for {partIpn}!')
                        continue

                    partFootprint = "xxxx:n.a."
                    for footprint in board.footprints:
                        if footprint.graphicItems[0].text == enumerated_parts[partIpn][0]:
                            partFootprint = footprint.libId

                    partFootprint = partFootprint.split(':')[1]

                    # Write the row to the CSV file
                    csv_writer.writerow([
                        manufacturerPartOfIntrest.MPN, 
                        part.Name, 
                        ', '.join(enumerated_parts[partIpn]), 
                        partFootprint, 
                        supplierPartOfIntrest.SKU
                    ])

                    app.console.write(f'{C.OkGreen}OK')

            self.log.info(f'Successfully exported JLCPCB BOM to {csv_file_name}!')

        except Exception as ex:
            self.log.error(f'Could not write to CSV file {csv_file_name}!')
            self.log.debug(f'Exception: {ex}!')
            app.console.write(f'{C.Fail}Failed!')
            return False
        return True

class JlcAssemblyXY(GenericExporter):
    """Class that implements the JLC BOM export functionality"""

    log = Logger.Create(__name__)
    """The logger of the JlcAssembly class"""

    def get_description(self) -> bool:
        """Get the description of the exporter"""
        return "JLCPCB assembly XY data"

    def export(self, app: App, args: List[str]) -> bool:        
        if len(args) == 0:
            app.console.write('Usage: export jlc_assembly_xy [ output_folder ]')
            return False

        csv_file_name = path.join(args[0], f'{app.project.name}_jlc_xy.csv')
        self.log.info(f'Starting JLCPCB XY position export to {csv_file_name}..')
        try:
            with open(csv_file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csv_writer.writerow([f';Exported with KiTree {KITREE_VERSION} at {datetime.now()}'])
                csv_writer.writerow([f';Project name: {app.project.name}'])
                csv_writer.writerow([f'sep=,'])
                csv_writer.writerow(["Designator", "Mid X", "Mid Y", "´Layer", "Rotation"])

                # Open KiCad project schematic
                app.console.write('Parsing KiCad board .. ', newline=False)
                boardPath = path.join(app.project.path, f'{app.project.name}.kicad_pcb')
                try:
                    board = Board().from_file(boardPath)
                    app.console.append(f'{C.OkGreen}Done!')
                except Exception as ex:
                    self.log.error(f'Could not parse board of project "{app.project.name}" at {boardPath}!')
                    self.log.debug(f'Exception: {str(ex)}')
                    app.console.append(f'{C.Fail}Failed!')
                    return False

                for footprint in board.footprints:
                    reference = footprint.graphicItems[0].text
                    app.console.write(f'Processing {reference} ..', newline=False)

                    if not app.config.get_ipn_field_name() in footprint.properties:
                        app.console.write(f'{C.Warning}IPN field missing! Skipping ..')
                        self.log.warning(f'{reference} misses IPN field in footprint properties, skipping ..')
                        continue

                    if not footprint.properties[app.config.get_ipn_field_name()] in app.project.get_parts_list():
                        app.console.write(f'{C.Warning}Not in project parts list! Skipping ..')
                        self.log.warning(f'{reference} not in projects part list, skipping ..')
                        continue

                    # Check if the symbol is a variant of another symbol or a power unit
                    if footprint.attributes.boardOnly:
                        app.console.write(f'{C.Warning}On board only! Skipping ..')
                        self.log.info(f'Skipping {reference} as it was found only on the board!')
                        continue

                    if footprint.attributes.excludeFromBom:
                        app.console.write(f'{C.Warning}Excluded from BOM! Skipping ..')
                        self.log.info(f'Skipping {reference} as it was excluded from the BOM!')
                        continue

                    if footprint.attributes.excludeFromPosFiles:
                        app.console.write(f'{C.Warning}Excluded from POS files! Skipping ..')
                        self.log.info(f'Skipping {reference} as it was excluded from POS files!')
                        continue

                    if footprint.attributes.type != 'smd':
                        app.console.write(f'{C.Warning}No SMD part! Skipping ..')
                        self.log.info(f'Skipping {reference} as only SMD components shall be used!')
                        continue

                    layer = 'Top' if footprint.layer == 'F.Cu' else 'Bottom'
                    rotation = footprint.position.angle if footprint.position.angle is not None else 0
                    csv_writer.writerow([reference, footprint.position.X, footprint.position.Y, layer, rotation])

                    app.console.write(f'{C.OkGreen}OK')

            self.log.info(f'Successfully exported JLCPCB BOM to {csv_file_name}!')

        except Exception as ex:
            self.log.error(f'Could not write to CSV file {csv_file_name}!')
            self.log.debug(f'Exception: {ex}!')
            app.console.write(f'{C.Fail}Failed!')
            return False
        return True