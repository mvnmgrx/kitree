
from external.assembly.jlcpcb import JlcAssemblyBom, JlcAssemblyXY
from external.templates import GenericExporter
from misc.console import Console


exporters: dict[str, GenericExporter] = {
    "jlc_assembly_bom": JlcAssemblyBom,
    "jlc_assembly_xy": JlcAssemblyXY
}
"""Dict of references to available exporters"""

class Exporter():
    """Exporter interface class"""

    @staticmethod
    def Export(exporter_name: str, file_name: str, parts: list[str]) -> bool:
        if not exporter_name in exporters.keys():
            return Console.Out(f'Unknown exporter: "{exporter_name}"')

        return exporters[exporter_name].Export(file_name, parts)

    @staticmethod
    def GetAvailableExporters() -> list[str]:
        return list(exporters.keys())