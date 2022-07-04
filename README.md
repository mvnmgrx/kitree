# KiTree

⚠⚠ This tool is WIP and theirfore neither stable nor finished ⚠⚠

KiTree is a CLI tool that assists in creating KiCad PCBs with parts tracked on an InvenTree server. 
It can:
- Automate the process of generating project-specific footprint & symbol libraries based on CAD 
  data assigned to the parts on the InvenTree server
- Create BOMs in InvenTree automatically based on the components used in the design
- Export manufacture-specific BOMs e.g. for JLCPCB assembly

It is designed with the following workflow in mind:
1. Create the part on the InvenTree server, along with a symbol, footprint as well as 3D-model 
   assigned. Alternatively use a template part that provides said files.
2. Add information about the supplier and the vendor of the part as well as a datasheet in InvenTree
2. Initialize a KiCad project with the KiTree CLI and add the parts needed for the design
3. When the design is finished, the BOM can be build from the CLI

# Requirements

- Python 3.10 or higher
- [KiUtils](https://github.com/mvnmgrx/kiutils) - `$ pip install kiutils`
- [InvenTree Python](https://github.com/inventree/inventree-python) - `$ pip install inventree`

# Documentation

To be defined at first release. Bookmark the project to stay updated.