
import csv
from datetime import datetime
from os import path
from kiutils.board import Board

from api.inventree import ITApi
from misc.logger import Logger
from misc.console import Console
from misc.colors import Color
from misc.tools import EnumerateBoard
from components.part import Part
from config import system, user
from external.templates import GenericExporter
from project.project import Project

class JlcAssemblyBom(GenericExporter):
    """Static class that implements the JLC BOM export functionality"""

    Log = Logger.Create(__name__)
    """The logger of the JlcAssembly class"""

    @staticmethod
    def Export(file_name: str, parts: list[str]) -> bool:

        csv_file_name = f'{file_name}.csv'
        JlcAssemblyBom.Log.info(f'Starting JLCPCB BOM export to {csv_file_name}..')
        try:
            with open(csv_file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csv_writer.writerow([f';Exported with KiTree {system.CLI_VERSION} at {datetime.now()}'])
                csv_writer.writerow([f';Project name: {Project.Name}'])
                csv_writer.writerow([f'sep=,'])
                csv_writer.writerow(["MPN", "Comment", "Designator", "Footprint", "JLCPCB Part #"])

                # Open KiCad project schematic
                Console.Out('Parsing KiCad board .. ', newline=False)
                boardPath = path.join(Project.Path, f'{Project.Name}.kicad_pcb')
                try:
                    board = Board().from_file(boardPath)
                    Console.Append(f'{Color.OkGreen}Done!')
                except Exception as ex:
                    JlcAssemblyBom.Log.error(f'Could not parse board of project "{Project.Name}" at {boardPath}!')
                    JlcAssemblyBom.Log.debug(f'Exception: {str(ex)}')
                    Console.Append(f'{Color.Fail}Failed!')
                    return False

                # Enumerate parts in schematic
                Console.Out('Enumerating KiCad board .. ', newline=False)
                enumerated_parts = {}
                enumerated_parts = EnumerateBoard(board, parts, use_tht=False)
                Console.Append(f'{Color.OkGreen}Done!')
                Console.Out('Found the following parts:')
                Console.Inc()
                for part in enumerated_parts.keys():
                    Console.Out(f'- {Color.Bold}{part}{Color.End}: {", ".join(enumerated_parts[part])}')
                Console.Dec()

                for partIpn in enumerated_parts.keys():
                    Console.Out(f'Processing {partIpn} ..', newline=False)

                    # Get part information from API
                    if not ITApi.PartExists(partIpn):
                        JlcAssemblyBom.Log.error(f'Part {partIpn} not found on InvenTree server ..')
                        Console.Append(f'{Color.Fail}Not available in InvenTree!')
                        continue

                    part = Part(partIpn)
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
                        Console.Out(f'{Color.Warning}No JLCPCB part! Skipping ..')
                        JlcAssemblyBom.Log.warning(f'No part with JLCPCB supplier found for {partIpn}!')
                        continue

                    partFootprint = "xxxx:n.a."
                    for footprint in board.footprints:
                        if footprint.graphicItems[0].text == enumerated_parts[partIpn][0]:
                            partFootprint = footprint.libraryLink

                    partFootprint = partFootprint.split(':')[1]

                    # Write the row to the CSV file
                    csv_writer.writerow([
                        manufacturerPartOfIntrest.MPN, 
                        part.Name, 
                        ', '.join(enumerated_parts[partIpn]), 
                        partFootprint, 
                        supplierPartOfIntrest.SKU
                    ])

                    Console.Out(f'{Color.OkGreen}OK')

            JlcAssemblyBom.Log.info(f'Successfully exported JLCPCB BOM to {csv_file_name}!')

        except Exception as ex:
            JlcAssemblyBom.Log.error(f'Could not write to CSV file {csv_file_name}!')
            JlcAssemblyBom.Log.debug(f'Exception: {ex}!')
            Console.Out(f'{Color.Fail}Failed!')
            return False
        return True

class JlcAssemblyXY(GenericExporter):

    """Static class that implements the JLC BOM export functionality"""

    Log = Logger.Create(__name__)
    """The logger of the JlcAssembly class"""

    @staticmethod
    def Export(file_name: str, parts: list[str]) -> bool:

        csv_file_name = f'{file_name}.csv'
        JlcAssemblyXY.Log.info(f'Starting JLCPCB XY position export to {csv_file_name}..')
        try:
            with open(csv_file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csv_writer.writerow([f';Exported with KiTree {system.CLI_VERSION} at {datetime.now()}'])
                csv_writer.writerow([f';Project name: {Project.Name}'])
                csv_writer.writerow([f'sep=,'])
                csv_writer.writerow(["Designator", "Mid X", "Mid Y", "´Layer", "Rotation"])

                # Open KiCad project schematic
                Console.Out('Parsing KiCad board .. ', newline=False)
                boardPath = path.join(Project.Path, f'{Project.Name}.kicad_pcb')
                try:
                    board = Board().from_file(boardPath)
                    Console.Append(f'{Color.OkGreen}Done!')
                except Exception as ex:
                    JlcAssemblyXY.Log.error(f'Could not parse board of project "{Project.Name}" at {boardPath}!')
                    JlcAssemblyXY.Log.debug(f'Exception: {str(ex)}')
                    Console.Append(f'{Color.Fail}Failed!')
                    return False

                for footprint in board.footprints:
                    reference = footprint.graphicItems[0].text
                    Console.Out(f'Processing {reference} ..', newline=False)

                    if not user.IPN_FIELD_NAME in footprint.properties:
                        Console.Out(f'{Color.Warning}IPN field missing! Skipping ..')
                        JlcAssemblyXY.Log.warning(f'{reference} misses IPN field in footprint properties, skipping ..')
                        continue

                    if not footprint.properties[user.IPN_FIELD_NAME] in parts:
                        Console.Out(f'{Color.Warning}Not in project parts list! Skipping ..')
                        JlcAssemblyXY.Log.warning(f'{reference} not in projects part list, skipping ..')
                        continue

                    # Check if the symbol is a variant of another symbol or a power unit
                    if footprint.attributes.boardOnly:
                        Console.Out(f'{Color.Warning}On board only! Skipping ..')
                        JlcAssemblyXY.Log.info(f'Skipping {reference} as it was found only on the board!')
                        continue

                    if footprint.attributes.excludeFromBom:
                        Console.Out(f'{Color.Warning}Excluded from BOM! Skipping ..')
                        JlcAssemblyXY.Log.info(f'Skipping {reference} as it was excluded from the BOM!')
                        continue

                    if footprint.attributes.excludeFromPosFiles:
                        Console.Out(f'{Color.Warning}Excluded from POS files! Skipping ..')
                        JlcAssemblyXY.Log.info(f'Skipping {reference} as it was excluded from POS files!')
                        continue

                    if footprint.attributes.type != 'smd':
                        Console.Out(f'{Color.Warning}No SMD part! Skipping ..')
                        JlcAssemblyXY.Log.info(f'Skipping {reference} as only SMD components shall be used!')
                        continue

                    layer = 'Top' if footprint.layer == 'F.Cu' else 'Bottom'
                    rotation = footprint.position.angle if footprint.position.angle is not None else 0
                    csv_writer.writerow([reference, footprint.position.X, footprint.position.Y, layer, rotation])

                    Console.Out(f'{Color.OkGreen}OK')

            JlcAssemblyXY.Log.info(f'Successfully exported JLCPCB BOM to {csv_file_name}!')

        except Exception as ex:
            JlcAssemblyXY.Log.error(f'Could not write to CSV file {csv_file_name}!')
            JlcAssemblyXY.Log.debug(f'Exception: {ex}!')
            Console.Out(f'{Color.Fail}Failed!')
            return False
        return True