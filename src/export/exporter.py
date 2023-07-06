from typing import Dict, List
from app import App
from export.assembly.jlcpcb import JlcAssemblyBom, JlcAssemblyXY
from export.templates import GenericExporter

exporters: Dict[str, GenericExporter] = {
    "jlc_assembly_bom": JlcAssemblyBom(),
    "jlc_assembly_xy": JlcAssemblyXY()
}
"""Dict of references to available exporters"""

def export(app: App, exporter_name: str, args: List[str]) -> bool:
    if not exporter_name in exporters.keys():
        return app.console.write(f'Unknown exporter: "{exporter_name}"')

    return exporters[exporter_name].export(app, args)

def get_exporters() -> Dict[str, GenericExporter]:
    return exporters