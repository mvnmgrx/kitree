
import csv
from datetime import datetime
from os import path
from kiutils.schematic import Schematic

from api.inventree import ITApi
from misc.logger import Logger
from misc.console import Console
from misc.colors import Color
from misc.tools import EnumerateSchematic
from components.part import Part
from main import KiTreeVersion
from external.templates import GenericExporter
from project.project import Project

class JlcAssembly(GenericExporter):
    """Static class that implements the JLC BOM export functionality"""

    Log = Logger.Create(__name__)
    """The logger of the JlcAssembly class"""

    @staticmethod
    def Export(file_name: str, parts: list[str]) -> bool:

        csv_file_name = f'{file_name}.csv'
        JlcAssembly.Log.info(f'Starting JLCPCB BOM export to {csv_file_name}..')
        try:
            with open(csv_file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([f';Exported with KiTree {KiTreeVersion} at {datetime.now()}'])
                csv_writer.writerow([f';Project name: {Project.Name}'])
                csv_writer.writerow([f'sep=,'])

                # Open KiCad project schematic
                Console.Out('Parsing KiCad schematic .. ', newline=False)
                schematicPath = path.join(Project.Path, f'{Project.Name}.kicad_sch')
                try:
                    schematic = Schematic().from_file(schematicPath)
                    Console.Append(f'{Color.OkGreen}Done!')
                except Exception as ex:
                    Console.Log.error(f'Could not parse schematic of project "{Project.Name}" at {schematicPath}!')
                    Console.Log.debug(f'Exception: {str(ex)}')
                    Console.Append(f'{Color.Fail}Failed!')
                    return False

                # Enumerate parts in schematic
                Console.Out('Enumerating KiCad schematic .. ', newline=False)
                enumerated_parts = {}
                enumerated_parts = EnumerateSchematic(schematic, parts)
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
                        Console.Log.error(f'Part {partIpn} not found on Inventree server ..')
                        Console.Append(f'{Color.Fail}Not available in Inventree!')
                        continue

                    part = Part(partIpn)
                    manufacturerPartOfIntrest = None

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
                            break
                        if manufacturerPartOfIntrest is not None:
                            # A manufacturer part of intrest was found, break the outer loop here
                            break
                    else:
                        Console.Out(f'{Color.Warning}No JLCPCB part! Skipping ..')
                        JlcAssembly.Log.warning(f'No part with JLCPCB supplier found for {partIpn}!')
                        continue

                    
                            
                    # Write the row to the CSV file
                    Console.Out(f'{Color.OkGreen}OK')
                    pass

            JlcAssembly.Log.info(f'Successfully exported JLCPCB BOM to {csv_file_name}!')

        except Exception as ex:
            JlcAssembly.Log.error(f'Could not write to CSV file {csv_file_name}!')
            JlcAssembly.Log.debug(f'Exception: {ex}!')
            Console.Out(f'{Color.Fail}Failed!')
            return False
        return True