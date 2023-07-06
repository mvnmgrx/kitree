from typing import Dict, List
from kiutils.schematic import Schematic
from kiutils.board import Board
from collections import namedtuple
from os import path
from app import App

from misc.logger import Logger

def enumerate_schematic(app: App, schematic: Schematic) -> Dict[str, List[str]]:
    """Searches for all references of the given parts in a root schematic as well as in all its
    sub-schematics. Only uses parts that are marked as `in_bom`.
    
    Params:
        - ``app``: The kitree app
        - ``schematic``: Root schematic parsed by KiUtils
    
    Returns:
        - Dictionary with IPN's as key and a list of references of components that use said IPN as 
          value

    ### Example usage:
    `parts = EnumerateSchematic(Schematic().from_file('my.kicad_sch'), ['IPN1', 'IPN2'])`

    returns something like: `parts = { 'IPN1': ['R1', 'R4'], 'IPN2': ['C1'] }`

    A key will never have an empty list assigned to it. At least one reference will always be
    present for a given key. If a key is not in the return dict, it was not found in the 
    schematic.
    """

    # Count the symbols in schematic that are marked as 'in_bom'
    parts = {}
    logger = Logger().Create(__name__)

    def check_symbol(schematic: Schematic, symbol_uuid: str, parts_dict: dict, reference: str) -> bool:
        """Check if a symbol is in a schematic and, if found, add it to the given parts dictionary with 
        the specified component reference
        Args:
            schematic (Schematic): Schematic to search through
            symbol_uuid (str): UUID of the symbol to search for
            parts_dict (dict): Parts dictionary to add the symbol to if found
            reference (str): Reference (KiCad ID, e.g. "R203") of the component
        Returns:
            bool: True if the symbol was found, otherwise False. Will return True even when the symbol
            is not marked as "in_bom" and the parts dict was not updated. Only returns False when 
            nothing was found at all.
        """
        for symbol in schematic.schematicSymbols:
            if symbol.uuid in symbol_uuid:
                # The symbol was found
                if not symbol.inBom:
                    logger.info(f'Symbol {symbol.libId} ({reference}) skipped as its not marked "in_bom"..')
                    return True

                # Check if the symbol is a variant of another symbol or a power unit
                if symbol.unit > 1 or reference.find("#PWR") != -1:
                    logger.info(f'Skipping {reference} as it is either a power symbol or a symbol variant')
                    return True

                # Check if the IPN is in the property list:
                for property in symbol.properties:
                    if property.key == app.config.get_ipn_field_name():
                        # Check if the symbol's IPN is on the project's part list
                        if not property.value in app.project.get_parts_list():
                            logger.info(f'Skipping {property.value} ({reference}) as it is not on the project\'s part list')
                            return True

                        # Add item to parts dict (property.value := IPN)
                        if property.value in parts_dict.keys():
                            parts_dict[property.value].append(reference)
                        else:
                            parts_dict.update({ property.value: [ reference ] })

                        logger.info(f'Added {property.value} ({reference}) to the parts list')
                        return True
                else:
                    logger.warning(f'Skipping symbol {symbol.libId} ({reference}) as it has no IPN assigned ..')
                    return True
        return False

    # Iterate over every symbol instance in the schematic root to determine every reference to every component
    for instance in schematic.symbolInstances:
        # Split instance path into /(sheet_uuid)/(component_uuid)
        SplitPath = namedtuple("SplitPath", "sheetUuid componentUuid")
        splitInstancePath = instance.path.rsplit('/', 1)
        if len(splitInstancePath) < 2:
            raise Exception("Instance path corrupted")
        instPath = SplitPath(splitInstancePath[0], splitInstancePath[1])

        if not instPath.sheetUuid:
            # Targeted symbol is in root page of schematic

            # Search for the UUID in all symbols
            if not check_symbol(schematic, instPath.componentUuid, parts, instance.reference):
                logger.error(f'Could not find symbol /{instPath.componentUuid} in schematic {path.basename(schematic.filePath)}')

        else:
            # Targeted symbol is somewhere else

            # Find path to correct KiCad sheet
            for sheet in schematic.sheets:
                if sheet.uuid in instPath.sheetUuid:
                    # Sheet was found, load it
                    subsheetPath = path.join(path.dirname(schematic.filePath), sheet.fileName.value)
                    try:
                        subsheet = Schematic().from_file(subsheetPath)
                    except Exception as ex:
                        logger.error(f'Found {instance.reference} at {sheet.uuid}, but could not its subsheet at "{subsheetPath}!"')
                        logger.debug(f'Exception: {ex}')
                        continue

                    if not check_symbol(subsheet, instPath.componentUuid, parts, instance.reference):
                        logger.error(f'Could not find symbol {instPath.sheetUuid}/{instPath.componentUuid} in schematic {path.basename(subsheet.filePath)}')
                    break
            else:
                logger.error(f'No sheet for {instPath.sheetUuid} found!')
    return parts


def enumerate_board(app: App, board: Board, use_smd: bool = True, use_tht: bool = True) -> Dict[str, List[str]]:
    """Searches for all references of the given parts in a board
    
    Params:
        - ``app``: The kitree application
        - ``board``: Board parsed by kiutils
        - ``use_smd``: Use SMD components when enumerating (defaults to True)
        - ``use_tht``: Use THT components when enumerating (defaults to True)

    Returns:
        - Dictionary with IPN's as key and a list of references of components that use said IPN as 
          value
    ### Example usage:
    `parts = EnumerateBoard(Board().from_file('my.kicad_pcb'), ['IPN1', 'IPN2'])`

    returns something like: `parts = { 'IPN1': ['R1', 'R4'], 'IPN2': ['C1'] }`
    
    A key will never have an empty list assigned to it. At least one reference will always be
    present for a given key. If a key is not in the return dict, it was not found in the 
    board.
    """

    # Count the symbols in schematic that are marked as 'in_bom'
    parts = {}
    logger = Logger().Create(__name__)

    for footprint in board.footprints:
        reference = footprint.graphicItems[0].text

        # Check if the symbol is a variant of another symbol or a power unit
        if footprint.attributes.boardOnly:
            logger.info(f'Skipping {reference} as it was found only on the board!')
            continue

        if footprint.attributes.excludeFromBom:
            logger.info(f'Skipping {reference} as it was excluded from the BOM!')
            continue

        if footprint.attributes.excludeFromPosFiles:
            logger.info(f'Skipping {reference} as it was excluded from POS files!')
            continue

        if footprint.attributes.type == 'smd' and not use_smd:
            logger.info(f'Skipping {reference} as SMD components shall not be used!')
            continue

        if footprint.attributes.type == 'through_hole' and not use_tht:
            logger.info(f'Skipping {reference} as THT components shall not be used!')
            continue

        # Check if the IPN is in the property list:
        for property in footprint.properties.keys():
            if property == app.config.get_ipn_field_name():
                # Check if the symbol's IPN is on the project's part list
                if not footprint.properties[property] in app.project.get_parts_list():
                    logger.info(f'Skipping {footprint.properties[property]} ({reference}) as it is not on the project\'s part list')
                    continue

                # Add item to parts dict (property.value := IPN)
                if footprint.properties[property] in parts.keys():
                    parts[footprint.properties[property]].append(reference)
                else:
                    parts.update({ footprint.properties[property]: [ reference ] })

                logger.info(f'Added {footprint.properties[property]} ({reference}) to the parts list')
                continue
        else:
            logger.warning(f'Skipping {reference} as it has no IPN assigned ..')
            continue
    return parts