"""Commands of the KiTree CLI

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from collections import namedtuple
from genericpath import isfile
from os import listdir, makedirs, path, rmdir, unlink
from shutil import copy
import time

from kiutils.items.common import Coordinate, Position, Property
from kiutils.footprint import Footprint, Model
from kiutils.schematic import Schematic
from kiutils.libraries import LibTable, Library
from kiutils.symbol import Symbol, SymbolLib

from components.part import Part
from misc.colors import Color
from misc.console import Console
from misc.config import Config
from project.project import Project
from api.inventree import ITApi
from external.exporter import Exporter
from config import user


def ShowStatus(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    Console.Out(f'Project "{ Project.Name }" loaded')
    Console.Out(f'  🌐 Path: {Color.OkBlue}{ Project.Path }')
    if Project.MasterPart is None:
        Console.Out(f'  ⭐ Master IPN: undefined')
    else:
        Console.Out(f'  ⭐ Master IPN: {Color.Bold}{ Project.MasterPart }')

def Exit(args: list):
    Console.Out('Goodbye!')
    exit()

def SetMasterPart(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    if len(args) == 0:
        return Console.Out('Usage: set master-part [ IPN ]')

    if not ITApi.PartExists(args[0]):
        return Console.Out(f'Part { args[0] } does not exist in Inventree!')

    Project.MasterPart = args[0]
    Project.Save()
    Console.Log.info(f'Changed master-part of { Project.Name } to { Project.MasterPart }')
    Console.Out(f'Master-part of "{ Project.Name }" set to { Project.MasterPart }')

def RemovePart(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    if len(args) == 0:
        return Console.Out('Usage: rm part [ IPN ]')

    if Project.RemovePart(args[0]):
        if Project.Save():
            Console.Out(f'Part { args[0] } removed from project part list')
        else:
            Console.Out(f'{Color.Fail}Could not save project\'s .kitree file!')
    else:
        Console.Out(f'Part { args[0] } not found in project part list!')

def RemoveAllParts(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    partCount = len(Project.Parts)
    Console.Out(f'Do you really want to remove all parts? (y/n)')
    choice = Console.In()
    if choice.find('y') != -1:
        Project.Parts.clear()
        if Project.Save():
            Console.Out(f'Cleared parts list of project { Project.Name }, removed { partCount } items')
        else:
            Console.Out(f'{Color.Fail}Could not save project\'s .kitree file!')

    else:
        Console.Out('Aborted..')

def AddPart(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    if len(args) == 0:
        return Console.Out('Usage: add [ IPN ]')

    if Project.Parts.count(args[0]) != 0:
        return Console.Out('This part is already in the project\'s part list')

    if Project.AddPart(args[0]):
        if Project.Save():
            Console.Out(f'Added part { args[0] } to project\'s part list')
        else:
            Console.Out(f'{Color.Fail}Could not save project\'s .kitree file!')
    else:
        Console.Out(f'{Color.Fail}Invalid IPN or part is not available in Inventree')

def ListParts(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    if len(Project.Parts) == 0:
        return Console.Out('No parts in project part list!')

    Console.Inc()
    for part in Project.Parts:
        Console.Out(f'- { part }')
    Console.Dec()

def ListKnownProjects(args: list):
    projects = Config.GetKnownProjects()
    if len(projects) == 0:
        return Console.Out("No projects known!")

    for project in projects:
        if project in Config.GetLastProject():
            Console.Out(f' - {project} {Color.OkBlue}<last>')
        else:
            Console.Out(f' - {project}')

def BuildLibs(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    libname = f'{Project.Name}-librarys'
    libpath = path.join(Project.Path, libname)
    symbolpath = path.join(libpath, f"{Project.Name}-symbols.kicad_sym")
    projectSymbolLib = SymbolLib(
        filePath  = symbolpath, 
        generator = 'kitree_build_libs', 
        version   = '20211014'
    )

    Console.Out(f'Building project {Project.Name} ..')
    startTime = time.time()

    # Remove the old library folder, if it exists
    Console.Out(f'Removing old library files ..')
    Console.Log.debug(f'Removing contents of {libpath}, if existing ..')

    if path.isdir(libpath):

        def deleteDirectory(the_path: str) -> bool:
            """Delete all files in a directory as well as its subdirectories and removes the
            given directory from the file system.

            Args:
                the_path (str): Path-like object to the directory

            Returns:
                bool: True if all files were deleted, otherwise False
            """
            if not path.isdir(the_path):
                Console.Log.error(f'Object at {the_path} is not a directory!')
                return False

            for filename in listdir(the_path):
                currentFilePath = path.join(the_path, filename)
                try:
                    Console.Log.debug(f"Removing {currentFilePath}")
                    if path.isfile(currentFilePath) or path.islink(currentFilePath):
                        unlink(currentFilePath)
                    elif path.isdir(currentFilePath):
                        deleteDirectory(currentFilePath)
                except Exception as e:
                    Console.Log.error(f'Error deleting file {filename}!')
                    Console.Log.debug(f'Exception: {e}')
                    return False

            rmdir(the_path)
            return True

        if not deleteDirectory(libpath):
            Console.Out(f'Could not remove files! Check log for more information ..', Color.Fail)

    # Recreate library folder in KiCad project folder
    makedirs(path.join(libpath, f"{Project.Name}-footprints.pretty"), exist_ok=True)
    makedirs(path.join(libpath, "3dmodels"), exist_ok=True)

    Console.Out('Downloading parts..')
    Console.Inc()
    for partIpn in Project.Parts:
        Console.Out(f'Processing {partIpn} .. ', newline=False)

        #     ___     __   __  ____           __        __
        #    / _ |___/ /__/ / / __/_ ____ _  / /  ___  / /
        #   / __ / _  / _  / _\ \/ // /  ' \/ _ \/ _ \/ / 
        #  /_/ |_\_,_/\_,_/ /___/\_, /_/_/_/_.__/\___/_/  
        #                       /___/                     

        # Check if part ID is still valid in Inventree
        # FIXME: What to do when more than one of the same IPN is present on the Inventree server
        #        This is unexpected behavior but might happen accidentally. Saying "not found" on 
        #        the CLI is therefore missleading.
        if not ITApi.PartExists(partIpn):
            Console.Log.error(f'Part {partIpn} not found on Inventree server ..')
            Console.Append(f'{Color.Fail}Not available in Inventree!')
            continue

        # Get part's information
        part = Part(partIpn)
        if not part.DownloadCadData():
            Console.Log.error(f'Part {part.IPN} failed downloading all needed CAD files! Skipping..')
            Console.Append(f'{Color.Fail}Failed downloading CAD data!')
            continue

        # Check if the downloaded symbol library has only one symbol associated
        tempSymLib = SymbolLib().from_file(part.SymbolPath)
        if len(tempSymLib.symbols) != 1:
            Console.Log.error(f'Part {part.IPN} has multiple symbols in its symbol file! Skipping..')
            Console.Append(f'{Color.Fail}Multiple symbols detected!')
            continue
        partSymbol = tempSymLib.symbols[0]

        # Copy 3d model into the KiCad project directory, the footprint is copied later
        if part.ModelPath is not None:
            copy(part.ModelPath, path.join(libpath, "3dmodels"))
        else:
            Console.Append(f'{Color.Warning}No 3D-Model .. ', finish=False)

        # Reuse the first four properties (ref, val, fp, ds) of the component's symbol
        # and extract the KiCad properties found at the end of the properties list (keywords,
        # description and filters)
        # FIXME: Filters is not always present in each symbol!
        if len(partSymbol.properties) < 7:
            Console.Log.error(f'Part {part.IPN}\'s symbol\'s properties are corrupted! Expecting at least the 7 standard properties. Skipping..')
            Console.Append(f'{Color.Fail}Symbol properties corrupted!')
            continue

        basicProperties = partSymbol.properties[0:4]
        kicadProperties = partSymbol.properties[-3:]
        basicEffects = basicProperties[2].effects
        basicEffects.hide = True
        
        def renameSymbol(symbol: Symbol, name: str):
            repname = name.replace('/', '_')
            oldname = symbol.id
            symbol.id = repname
            for subsymbol in symbol.units:
                subsymbol.id = subsymbol.id.replace(oldname, repname)

        # Set the symbol's basic properties to fit the component
        schematicId = part.GetSchematicId()
        if schematicId is None:
            Console.Log.warning(f'Part {part.IPN} has no schematic identifier set! Using IPN of Inventree part instead..')
            Console.Append(f'{Color.Warning}No schematic ID! Using IPN .. ', finish=False)
            basicProperties[1].value = part.IPN.replace('/', '_') # Replace / with _ as KiCad dont likes this as name
            renameSymbol(partSymbol, part.IPN)
        else:
            basicProperties[1].value = schematicId.replace('/', '_') # Replace / with _ as KiCad dont likes this as name
            renameSymbol(partSymbol, schematicId)
        
        basicProperties[2].value = f'{Project.Name}-footprints:{part.GetFootprintName()}'
        basicProperties[2].position = Position(X=0.0, Y=200.0, angle=0.0)
        basicProperties[3].value = part.GetDatasheetUrl()
        basicProperties[3].position = Position(X=0.0, Y=198.08, angle=0.0)

        # TODO: Search for the lowest part of a symbol and put the invisible text there
        # Add additional properties to the symbol that are retrieved from the Inventree part
        additionalProperties = [
            Property(key=user.IPN_FIELD_NAME, value=part.IPN, id=4, effects=basicEffects, position=Position(0.0, 196.14, 0.0)),
            Property(key=user.MF_FIELD_NAME, value=part.GetManufacturerName(), id=5, effects=basicEffects, position=Position(0.0, 194.21, 0.0)),
            Property(key=user.MPN_FIELD_NAME, value=part.GetMPN(), id=6, effects=basicEffects, position=Position(0.0, 192.28, 0.0)),
            Property(key=user.SUPPLIER_FIELD_NAME, value=part.GetSupplierName(), id=7, effects=basicEffects, position=Position(0.0, 190.35, 0.0)),
            Property(key=user.SKU_FIELD_NAME, value=part.GetSKU(), id=8, effects=basicEffects, position=Position(0.0, 188.42, 0.0)),
            Property(key=user.URL_FIELD_NAME, value=part.GetSupplierLink(), id=9, effects=basicEffects, position=Position(0.0, 186.49, 0.0))
        ]
        
        # Search for the Package field that should be kept if its given
        for property in partSymbol.properties:
            if property.key == "Package":
                property.id = 10
                additionalProperties.append(property)
                break
        
        # Adjust IDs of KiCad parameters accordingly and set symbol keywords as well as description
        kicadProperties[0].id = 11
        kicadProperties[0].value = part.Keywords
        kicadProperties[1].id = 12
        kicadProperties[1].value = part.FullName
        kicadProperties[2].id = 13

        # Build properties of final symbol and append it to the project's symbol library
        partSymbol.properties = basicProperties + additionalProperties + kicadProperties
        projectSymbolLib.symbols.append(partSymbol)

        #    _____                 ___          __           _      __ 
        #   / ___/__  ___  __ __  / _/__  ___  / /____  ____(_)__  / /_
        #  / /__/ _ \/ _ \/ // / / _/ _ \/ _ \/ __/ _ \/ __/ / _ \/ __/
        #  \___/\___/ .__/\_, / /_/ \___/\___/\__/ .__/_/ /_/_//_/\__/ 
        #          /_/   /___/                  /_/                    

        # Open and read footprint file in library
        partFootprint = Footprint().from_file(part.FootprintPath)
        footprintPathInProject = path.join(libpath, f"{Project.Name}-footprints.pretty", part.GetFootprintName()+'.kicad_mod')

        # Set correct 3d-model path in footprint, if one was downloaded from InvenTree
        partFootprint.models.clear()
        if part.ModelPath is not None:
            modelName = path.basename(part.ModelPath)
            modelPath = f'${{KIPRJMOD}}/{libname}/3dmodels/{modelName}'

            # Add 3d-model to footprint
            partFootprint.models.append(Model(path=modelPath))
            Console.Log.info(f'Path of 3D model for {part.IPN} is "{modelPath}"')

        # Check if parameters for 3d model position are set
        # TODO: Move this somewhere where it does make sense ..
        def waterfallTo3DModelCoordinateFromParameterName(model: Part, parameterName: str) -> bool:
            if model.Parameters is None:
                return False
            for parameter in model.Parameters:
                if parameter.TemplateDetail.Name == parameterName:
                    match parameter.Data.split(', '):
                        case [x, y, z]:
                            Console.Log.info(f'Using X: {x}, Y: {y}, Z: {z} from {model.IPN} for {partIpn}\'s {parameterName}')
                            if parameterName == '3DModel Scaling':
                                partFootprint.models[0].scale = Coordinate(x, y, z)
                            elif parameterName == '3DModel Rotation':
                                partFootprint.models[0].rotate = Coordinate(x, y, z)
                            elif parameterName == '3DModel Offset':
                                partFootprint.models[0].pos = Coordinate(x, y, z)
                            return True
                        case _:
                            continue
            else:
                if model.VariantPart is not None:
                    return waterfallTo3DModelCoordinateFromParameterName(model.VariantPart, parameterName)
            return False

        waterfallTo3DModelCoordinateFromParameterName(part, '3DModel Scaling')
        waterfallTo3DModelCoordinateFromParameterName(part, '3DModel Rotation')
        waterfallTo3DModelCoordinateFromParameterName(part, '3DModel Offset')

        # Save footprint to project's footprint library
        partFootprint.to_file(footprintPathInProject)

        Console.Append(f'{Color.OkGreen}Done!')

    Console.Dec()

    # Save project library to file system
    Console.Out(f'Writing symbol library to disk .. ', newline=False)
    try:
        projectSymbolLib.to_file()
        Console.Append(f'{Color.OkGreen}Done!')
    except Exception as ex:
        Console.Log.error(f'Could not write symbol library of project "{Project.Name}" to {projectSymbolLib.filePath}!')
        Console.Log.debug(f'Exception: {str(ex)}')
        return Console.Append(f'{Color.Fail}Failed!')

    # Add symbol library to KiCad sym-lib-table, if not done before
    Console.Out('Adding symbol library table entry .. ', newline=False)
    libtablePath = path.join(Project.Path, 'sym-lib-table')
    if isfile(libtablePath):
        symbolLibTable = LibTable().from_file(libtablePath)
    else:
        symbolLibTable = LibTable(type='sym_lib_table', filePath=libtablePath)

    for lib in symbolLibTable.libs:
        if lib.name == f'{Project.Name}-symbols':
            Console.Append(f'{Color.OkBlue}Skipped..')
            break
    else:
        symbolLibTable.libs.append(Library(
            name=f'{Project.Name}-symbols', 
            uri=f'${{KIPRJMOD}}/{libname}/{Project.Name}-symbols.kicad_sym'))
        try:
            symbolLibTable.to_file()
            Console.Append(f'{Color.OkGreen}Done!')
        except Exception as ex:
            Console.Log.error(f'Could not write symbol library table of project "{Project.Name}" to {symbolLibTable.filePath}!')
            Console.Log.debug(f'Exception: {str(ex)}')
            Console.Append(f'{Color.Fail}Failed!')
        
    # Add footprint library to KiCad fp-lib-table, if not done before
    Console.Out('Adding footprint library table entry .. ', newline=False)
    fptablePath = path.join(Project.Path, 'fp-lib-table')
    if isfile(fptablePath):
        fpLibTable = LibTable().from_file(fptablePath)
    else:
        fpLibTable = LibTable(type='fp_lib_table', filePath=fptablePath)

    for lib in fpLibTable.libs:
        if lib.name == f'{Project.Name}-footprints':
            Console.Append(f'{Color.OkBlue}Skipped..')
            break
    else:
        fpLibTable.libs.append(Library(
            name=f'{Project.Name}-footprints', 
            uri=f'${{KIPRJMOD}}/{libname}/{Project.Name}-footprints.pretty'))
        try:
            fpLibTable.to_file()
            Console.Append(f'{Color.OkGreen}Done!')
        except Exception as ex:
            Console.Log.error(f'Could not write footprint library table of project "{Project.Name}" to {fpLibTable.filePath}!')
            Console.Log.debug(f'Exception: {str(ex)}')
            Console.Append(f'{Color.Fail}Failed!')


    endTime = time.time()
    Console.Out(f'{Color.OkGreen}Done! {Color.End}Took {Color.Bold}{endTime-startTime:.2f}s')

def BuildBom(args: list):
    startTime = time.time()
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    if Project.MasterPart is None:
        return Console.Out('No master IPN set. Use "set master-part"')

    if not ITApi.PartExists(Project.MasterPart):
        return Console.Out('Master part does not exist in Inventree!')

    masterPart = Part(Project.MasterPart)

    # Clear BOM of master-part
    Console.Out(f'Clearing master-part\'s BOM .. ', newline=False)
    if masterPart.Bom is None:
            Console.Append(f'{Color.OkBlue}Skipped..')
    else:
        if len(masterPart.Bom) == 0:
            Console.Append(f'{Color.OkBlue}Skipped..')
        else:
            if masterPart.ClearBom():
                Console.Append(f'{Color.OkGreen}Done!')
            else:
                return Console.Append(f'{Color.Fail}Failed!')

    # Open KiCad project schematic
    Console.Out('Parsing KiCad schematic .. ', newline=False)
    schematicPath = path.join(Project.Path, f'{Project.Name}.kicad_sch')
    try:
        schematic = Schematic().from_file(schematicPath)
        Console.Append(f'{Color.OkGreen}Done!')
    except Exception as ex:
        Console.Log.error(f'Could not parse schematic of project "{Project.Name}" at {schematicPath}!')
        Console.Log.debug(f'Exception: {str(ex)}')
        return Console.Append(f'{Color.Fail}Failed!')

    # Count the symbols in schematic that are marked as 'in_bom'
    parts = {}
    Console.Out('Counting symbol references .. ', newline=False)

    # FIXME: Where does this fit better?
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
                    Console.Log.info(f'Symbol {symbol.libraryIdentifier} ({reference}) skipped as its not marked "in_bom"..')
                    return True

                # Check if the symbol is a variant of another symbol or a power unit
                if symbol.unit != 1 or reference.find("#PWR") != -1:
                    Console.Log.info(f'Skipping {reference} as it is either a power symbol or a symbol variant')
                    return True

                # Check if the IPN is in the property list:
                for property in symbol.properties:
                    if property.key == 'Internal Nr.':
                        # Check if the symbol's IPN is on the project's part list
                        if not property.value in Project.Parts:
                            Console.Log.info(f'Skipping {property.value} ({reference}) as it is not on the project\'s part list')
                            return True

                        # Add item to parts dict (property.value := IPN)
                        if property.value in parts_dict.keys():
                            parts_dict[property.value].append(reference)
                        else:
                            parts_dict.update({ property.value: [ reference ] })
                        return True
                else:
                    Console.Log.warning(f'Skipping symbol {symbol.libraryIdentifier} ({reference}) as it has no IPN assigned ..')
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
                Console.Log.error(f'Could not find symbol /{instPath.componentUuid} in schematic {path.basename(schematic.filePath)}')
                
        else:
            # Targeted symbol is somewhere else
            
            # Find path to correct KiCad sheet
            for sheet in schematic.sheets:
                if sheet.uuid in instPath[0]:
                    # Sheet was found, load it
                    subsheetPath = path.join(path.dirname(schematic.filePath), sheet.fileName.value)
                    try:
                        subsheet = Schematic().from_file(subsheetPath)
                    except Exception as ex:
                        Console.Log.error(f'Found {instance.reference} at {sheet.uuid}, but could not its subsheet at "{subsheetPath}!"')
                        Console.Log.debug(f'Exception: {ex}')
                        continue

                    if not check_symbol(subsheet, instPath[1], parts, instance.reference):
                        Console.Log.error(f'Could not find symbol {instPath.sheetUuid}/{instPath.componentUuid} in schematic {path.basename(subsheet.filePath)}')
                    break
            else:
                Console.Log.error(f'No sheet for {instPath.sheetUuid} found!')
    
    # Print counted statistics
    Console.Append(f'{Color.OkGreen}Done!')
    Console.Inc()
    for item in parts.keys():
        Console.Out(f'{item}: {Color.Bold}{", ".join(parts[item])}')
    Console.Dec()

    # Add each part to the Inventree BOM for this project's master part
    Console.Out(f'Adding items to BOM of "{Project.MasterPart}" .. ')
    Console.Inc()
    for part in parts.keys():
        Console.Out(f'Processing {part} .. ', newline=False)
        if ITApi.CreateBomItem(Project.MasterPart, part, len(parts[part]), parts[part]):
            Console.Append(f'{Color.OkGreen}Done!')
        else:
            Console.Append(f'{Color.Fail}Failed!')

    Console.Dec()
    endTime = time.time()
    Console.Out(f'{Color.OkGreen}Done! {Color.End}Took {Color.Bold}{endTime-startTime:.2f}s')
    
def LoadProject(args: list):
    if Project.Loaded:
        return Console.Out("A project is already loaded!")

    if len(args) == 0:
        return Console.Out('Usage: load [ last / <name> / <path> ]')

    path = None

    if args[0] == "last":
        lastProject = Config.GetLastProject()
        if lastProject is None:
            return Console.Out('No last project known!')

        path = Config.GetKnownProjectPath(lastProject)
        if path is None:
            return Console.Out('No path to known project known!')

        Console.Log.info(f'Using path "{ path }" for last known project "{ lastProject }"')

    else:
        # Check if the given argument is a known project, otherwise use it as path
        # for Project.Load()
        path = Config.GetKnownProjectPath(args[0])
        if path is None:
            path = args[0]
            Console.Log.info(f'Given argument is no known project. Using "{ path }" as path')
        else:
            Console.Log.info(f'Using "{ path }" as path for known project { args[0] }')

    if Project.Load(path):
        Console.Out(f'Successfully loaded project \'{Project.Name}\'')
        Config.SetLastProject(Project.Name)
    else:
        Console.Out(f'Could not load project! Check log files for more information..')

def InitProject(args: list):
    if Project.Loaded:
        return Console.Out("A project is already loaded!")

    if len(args) == 0:
        return Console.Out('Usage: init [ path ]')

    # Check if a KiCad project exists at the given path
    suppliedPath = args[0]
    files = [f for f in listdir(suppliedPath) if isfile(path.join(suppliedPath, f))]
    for file in files:
        if '.kicad_pro' in file:
            projectName = file.removesuffix('.kicad_pro')
            projectPath = path.join(suppliedPath, file)
            Console.Out(f'Found valid KiCad project "{projectName}"')
            break
    else:
        return Console.Out(f'{Color.Fail}No valid KiCad project found at this location!')

    if isfile(path.join(projectPath, '.kitree')):
        return Console.Out(f'Project is already initialized! Use "load" instead..')

    # Initialize KiTree project
    Config.SetLastProject(projectName)
    Config.AddKnownProject(projectName, suppliedPath)
    Project.Path = suppliedPath
    Project.Save()
    Console.Out(f'Project "{projectName}" successfully initialized! Use "load last" to load it')

def GetHelp(args: list):
    return Console.Out(f'{Color.Warning}Not yet implemented..')

def ShowLog(args: list):
    level = 'DEBUG' if len(args) == 0 else args[0]
    numLines = 5 if len(args) < 2 else int(args[1])

    Console.Out(f'Showing last {numLines} lines of the logfile..')

    with open('kitree.log', 'r') as logfile:
        lines = logfile.readlines()
        lines.reverse()
        counter = 0
        for line in lines:
            if counter > numLines:
                break
            if level != 'DEBUG' and level not in line:
                continue
            Console.Out(f'{line}', newline=False)
            counter = counter + 1

def ExportToFile(args: list):
    if not Project.Loaded:
        return Console.Out('No project loaded!')

    if len(args) < 2:
        Console.Out('Usage: export [ exporter_name ] [ file_name ]')
        return Console.Out(f'Available exporters: {", ".join(Exporter.GetAvailableExporters())}')

    if len(Project.Parts) == 0:
        return Console.Out('No parts in the project\'s part list')

    return Exporter.Export(exporter_name = args[0], file_name = args[1], parts = Project.Parts)