from genericpath import isfile
import time
from os import listdir, makedirs, path, rmdir, unlink
from shutil import copy

from kiutils.items.common import Position, Property, Coordinate
from kiutils.footprint import Footprint, Model
from kiutils.symbol import SymbolLib, Symbol
from kiutils.libraries import LibTable, Library

from app import App
from components.part import Part
from misc.colors import Color


def command_build_libs(app: App, args: list):
    if not app.project.isLoaded:
        return app.console.write('No project loaded!')

    libname = f'{app.project.name}-librarys'
    libpath = path.join(app.project.path, libname)
    symbolpath = path.join(libpath, f"{app.project.name}-symbols.kicad_sym")
    projectSymbolLib = SymbolLib(
        filePath  = symbolpath, 
        generator = 'kitree_build_libs', 
        version   = '20211014'
    )

    app.console.write(f'Building project {app.project.name} ..')
    startTime = time.time()

    # Remove the old library folder, if it exists
    app.console.write(f'Removing old library files ..')
    app.console.log.debug(f'Removing contents of {libpath}, if existing ..')

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
                app.console.log.error(f'Object at {the_path} is not a directory!')
                return False

            for filename in listdir(the_path):
                currentFilePath = path.join(the_path, filename)
                try:
                    app.console.log.debug(f"Removing {currentFilePath}")
                    if path.isfile(currentFilePath) or path.islink(currentFilePath):
                        unlink(currentFilePath)
                    elif path.isdir(currentFilePath):
                        deleteDirectory(currentFilePath)
                except Exception as e:
                    app.console.log.error(f'Error deleting file {filename}!')
                    app.console.log.debug(f'Exception: {e}')
                    return False

            rmdir(the_path)
            return True

        if not deleteDirectory(libpath):
            app.console.write(f'Could not remove files! Check log for more information ..', Color.Fail)

    # Recreate library folder in KiCad project folder
    makedirs(path.join(libpath, f"{app.project.name}-footprints.pretty"), exist_ok=True)
    makedirs(path.join(libpath, "3dmodels"), exist_ok=True)

    app.console.write('Downloading parts..')
    app.console.inc()
    for partIpn in app.project.get_parts_list():
        app.console.write(f'Processing {partIpn} .. ', newline=False)

        #     ___     __   __  ____           __        __
        #    / _ |___/ /__/ / / __/_ ____ _  / /  ___  / /
        #   / __ / _  / _  / _\ \/ // /  ' \/ _ \/ _ \/ / 
        #  /_/ |_\_,_/\_,_/ /___/\_, /_/_/_/_.__/\___/_/  
        #                       /___/                     

        # Check if part ID is still valid in Inventree
        # FIXME: What to do when more than one of the same IPN is present on the Inventree server
        #        This is unexpected behavior but might happen accidentally. Saying "not found" on 
        #        the CLI is therefore missleading.
        if not app.project.api.part_exists(partIpn):
            app.console.log.error(f'Part {partIpn} not found on Inventree server ..')
            app.console.append(f'{Color.Fail}Not available in Inventree!')
            continue

        # Get part's information
        part = Part(app.project.api, partIpn)
        if not part.download_cad_data():
            app.console.log.error(f'Part {part.IPN} failed downloading all needed CAD files! Skipping..')
            app.console.append(f'{Color.Fail}Failed downloading CAD data!')
            continue

        # Check if the downloaded symbol library has only one symbol associated
        tempSymLib = SymbolLib().from_file(part.SymbolPath)
        if len(tempSymLib.symbols) != 1:
            app.console.log.error(f'Part {part.IPN} has multiple symbols in its symbol file! Skipping..')
            app.console.append(f'{Color.Fail}Multiple symbols detected!')
            continue
        partSymbol = tempSymLib.symbols[0]

        # Copy 3d model into the KiCad project directory, the footprint is copied later
        if part.ModelPath is not None:
            copy(part.ModelPath, path.join(libpath, "3dmodels"))
        else:
            app.console.append(f'{Color.Warning}No 3D-Model .. ', finish=False)

        # Reuse the first four properties (ref, val, fp, ds) of the component's symbol
        # and extract the KiCad properties found at the end of the properties list (keywords,
        # description and filters)
        # FIXME: Filters is not always present in each symbol!
        if len(partSymbol.properties) < 7:
            app.console.log.error(f'Part {part.IPN}\'s symbol\'s properties are corrupted! Expecting at least the 7 standard properties. Skipping..')
            app.console.append(f'{Color.Fail}Symbol properties corrupted!')
            continue

        basicProperties = partSymbol.properties[0:4]
        kicadProperties = partSymbol.properties[-3:]
        basicEffects = basicProperties[2].effects
        basicEffects.hide = True
        
        def renameSymbol(symbol: Symbol, name: str):
            repname = name.replace('/', '_')
            oldname = symbol.libId
            symbol.libId = repname
            for subsymbol in symbol.units:
                subsymbol.libId = subsymbol.libId.replace(oldname, repname)

        # Set the symbol's basic properties to fit the component
        schematicId = part.GetSchematicId()
        if schematicId is None:
            app.console.log.warning(f'Part {part.IPN} has no schematic identifier set! Using IPN of Inventree part instead..')
            app.console.append(f'{Color.Warning}No schematic ID! Using IPN .. ', finish=False)
            basicProperties[1].value = part.IPN.replace('/', '_') # Replace / with _ as KiCad dont likes this as name
            renameSymbol(partSymbol, part.IPN)
        else:
            basicProperties[1].value = schematicId.replace('/', '_') # Replace / with _ as KiCad dont likes this as name
            renameSymbol(partSymbol, schematicId)
        
        basicProperties[2].value = f'{app.project.name}-footprints:{part.GetFootprintName()}'
        basicProperties[2].position = Position(X=0.0, Y=200.0, angle=0.0)
        basicProperties[3].value = part.GetDatasheetUrl()
        basicProperties[3].position = Position(X=0.0, Y=198.08, angle=0.0)

        # Add additional properties to the symbol that are retrieved from the Inventree part
        additionalProperties = [
            Property(key="Internal Nr.", value=part.IPN, id=4, effects=basicEffects, position=Position(0.0, 196.14, 0.0)),
            Property(key="Manufacturer", value=part.GetManufacturerName(), id=5, effects=basicEffects, position=Position(0.0, 194.21, 0.0)),
            Property(key="Part Nr.", value=part.GetMPN(), id=6, effects=basicEffects, position=Position(0.0, 192.28, 0.0)),
            Property(key="Supplier", value=part.GetSupplierName(), id=7, effects=basicEffects, position=Position(0.0, 190.35, 0.0)),
            Property(key="Order Nr.", value=part.GetSKU(), id=8, effects=basicEffects, position=Position(0.0, 188.42, 0.0)),
            Property(key="Link", value=part.GetSupplierLink(), id=9, effects=basicEffects, position=Position(0.0, 186.49, 0.0))
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
        footprintPathInProject = path.join(libpath, f"{app.project.name}-footprints.pretty", part.GetFootprintName()+'.kicad_mod')

        # Set correct 3d-model path in footprint, if one was downloaded from InvenTree
        partFootprint.models.clear()
        if part.ModelPath is not None:
            modelName = path.basename(part.ModelPath)
            modelPath = f'${{KIPRJMOD}}/{libname}/3dmodels/{modelName}'

            # Add 3d-model to footprint
            partFootprint.models.append(Model(path=modelPath))
            app.console.log.info(f'Path of 3D model for {part.IPN} is "{modelPath}"')

        # Check if parameters for 3d model position are set
        # TODO: Move this somewhere where it does make sense ..
        def waterfallTo3DModelCoordinateFromParameterName(model: Part, parameterName: str) -> bool:
            if model.Parameters is None:
                return False
            for parameter in model.Parameters:
                if parameter.TemplateDetail.Name == parameterName:
                    match parameter.Data.split(', '):
                        case [x, y, z]:
                            app.console.log.info(f'Using X: {x}, Y: {y}, Z: {z} from {model.IPN} for {partIpn}\'s {parameterName}')
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

        app.console.append(f'{Color.OkGreen}Done!')

    app.console.dec()

    # Save project library to file system
    app.console.write(f'Writing symbol library to disk .. ', newline=False)
    try:
        projectSymbolLib.to_file()
        app.console.append(f'{Color.OkGreen}Done!')
    except Exception as ex:
        app.console.log.error(f'Could not write symbol library of project "{app.project.name}" to {projectSymbolLib.filePath}!')
        app.console.log.debug(f'Exception: {str(ex)}')
        return app.console.append(f'{Color.Fail}Failed!')

    # Add symbol library to KiCad sym-lib-table, if not done before
    app.console.write('Adding symbol library table entry .. ', newline=False)
    libtablePath = path.join(app.project.path, 'sym-lib-table')
    if isfile(libtablePath):
        symbolLibTable = LibTable().from_file(libtablePath)
    else:
        symbolLibTable = LibTable(type='sym_lib_table', filePath=libtablePath)

    for lib in symbolLibTable.libs:
        if lib.name == f'{app.project.name}-symbols':
            app.console.append(f'{Color.OkBlue}Skipped..')
            break
    else:
        symbolLibTable.libs.append(Library(
            name=f'{app.project.name}-symbols', 
            uri=f'${{KIPRJMOD}}/{libname}/{app.project.name}-symbols.kicad_sym'))
        try:
            symbolLibTable.to_file()
            app.console.append(f'{Color.OkGreen}Done!')
        except Exception as ex:
            app.console.log.error(f'Could not write symbol library table of project "{app.project.name}" to {symbolLibTable.filePath}!')
            app.console.log.debug(f'Exception: {str(ex)}')
            app.console.append(f'{Color.Fail}Failed!')
        
    # Add footprint library to KiCad fp-lib-table, if not done before
    app.console.write('Adding footprint library table entry .. ', newline=False)
    fptablePath = path.join(app.project.path, 'fp-lib-table')
    if isfile(fptablePath):
        fpLibTable = LibTable().from_file(fptablePath)
    else:
        fpLibTable = LibTable(type='fp_lib_table', filePath=fptablePath)

    for lib in fpLibTable.libs:
        if lib.name == f'{app.project.name}-footprints':
            app.console.append(f'{Color.OkBlue}Skipped..')
            break
    else:
        fpLibTable.libs.append(Library(
            name=f'{app.project.name}-footprints', 
            uri=f'${{KIPRJMOD}}/{libname}/{app.project.name}-footprints.pretty'))
        try:
            fpLibTable.to_file()
            app.console.append(f'{Color.OkGreen}Done!')
        except Exception as ex:
            app.console.log.error(f'Could not write footprint library table of project "{app.project.name}" to {fpLibTable.filePath}!')
            app.console.log.debug(f'Exception: {str(ex)}')
            app.console.append(f'{Color.Fail}Failed!')


    endTime = time.time()
    app.console.write(f'{Color.OkGreen}Done! {Color.End}Took {Color.Bold}{endTime-startTime:.2f}s')
