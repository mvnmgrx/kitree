"""Classes defining an InvenTree part

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass
from os import getcwd, makedirs, path
from types import NoneType

from api.inventree import ITApi
from components.company import ManufacturerPart
from misc.logger import Logger

@dataclass
class PartCategory():
    """This class represents a Part/Category of the Inventree API
    """
    ID: int = 0
    Name: str = ""
    Description: str = ""
    DefaultLocation = NoneType
    DefaultKeywords: str = ""
    Level: int = 0
    Parent: int = 0
    Parts: int = 0
    PathString: str = ""
    Url: str = ""

    def __init__(self, data: dict | None):
        """Initializes a PartCategory object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        if data is None:
            return

        self.ID = data['pk']
        self.Name = data['name']
        self.Description = data['description']
        self.DefaultLocation = data['default_location']
        self.DefaultKeywords = data['default_keywords']
        self.Level = data['level']
        self.Parent = data['parent']
        self.Parts = data['parts']
        self.PathString = data['pathstring']
        self.Url = data['url']

@dataclass
class PartParameterTemplate():
    """This class represents a Part/Parameter/Template of the Inventree API
    """
    ID: int = -1
    Name: str = ""
    Units: str = ""

    def __init__(self, data: dict | None):
        """Initializes a PartParameterTemplate object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        if data is None:
            return

        self.ID = data['pk']
        self.Name = data['name']
        self.Units = data['units']

@dataclass
class PartParameter():
    """This class represents a Part/Parameter of the Inventree API
    """
    ID: int = -1
    Part: int = -1
    Template: int = -1
    TemplateDetail: PartParameterTemplate = None
    Data: str = ""

    def __init__(self, data: dict | None):        
        """Initializes a PartParameter object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        if data is None:
            return

        self.ID = data['pk']
        self.Part = data['part']
        self.Template = data['template']
        self.TemplateDetail = PartParameterTemplate(data['template_detail'])
        self.Data = data['data']

@dataclass
class PartAttachment():
    """This class represents a Part/Attachment of the Inventree API
    """
    ID: int = -1
    Part: int = -1
    Attachment: str = ""
    FileName: str = ""
    Comment: str = ""
    UploadDate: str = ""

    def __init__(self, data: dict | None):        
        """Initializes a PartAttachment object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        if data is None:
            return

        self.ID = data['pk']
        self.Part = data['part']
        self.Attachment = data['attachment']
        self.FileName = data['filename']
        self.Comment = data['comment']
        self.UploadDate = data['upload_date']

@dataclass 
class BomItem():
    """Represents a Bom of the Inventree API
    """
    AllowVariants: bool = False
    Inherited: bool = False
    Note: str = ""
    Optional: bool = False
    Overage: str = ""
    ID: int = -1
    Part: int = -1
    PurchasePriceAvg: str = "-"
    PurchasePriceMax = None
    PurchasePrixeMin = None
    PurchasePriceRange: str = "-"
    Quantity: float = 0.0
    Reference: str = ""
    SubPart: int = -1
    PriceRange = None
    Validated: bool = False

    def __init__(self, data: dict | None):        
        """Initializes a BomItem object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        if data is None:
            return

        self.AllowVariants = data['allow_variants']
        self.Inherited = data['inherited']
        self.Note = data['note']
        self.Optional = data['optional']
        self.Overage = data['overage']
        self.ID = data['pk']
        self.Part = data['part']
        self.PurchasePriceAvg = data['purchase_price_avg']
        self.PurchasePriceMax = data['purchase_price_max']
        self.PurchasePrixeMin = data['purchase_price_min']
        self.PurchasePriceRange = data['purchase_price_range']
        self.Quantity = data['quantity']
        self.Reference = data['reference']
        self.SubPart = data['sub_part']
        self.PriceRange = data['price_range']
        self.Validated = data['validated']

@dataclass
class Part():    
    """This class represents a Part of the Inventree API
    """
    Active: bool = False
    Assembly: bool = False
    Category: int = 0
    CategoryDetail: PartCategory = PartCategory(None)
    Component: bool = False
    DefaultExpiry: int = 0
    DefaultLocation: str = NoneType
    DefaultSupplier: str = NoneType
    Description: str = NoneType
    FullName: str = NoneType
    ImagePath: str = NoneType
    InStock: float = 0.0
    Ordering: float = 0.0
    Building: float = 0.0
    IPN: str = NoneType
    IsTemplate: bool = False
    Keywords: str = ""
    Link: str = ""
    MinimumStock: int = 0
    Name: str = ""
    Notes: str = NoneType
    ID: int = 0
    Purchaseable: bool = False
    Revision: str = ""
    Salable: bool = False
    Starred: bool = False
    StockItemCount: int = 0
    Suppliers: int = 0
    ThumbnailPath: str = ""
    Trackable: bool = False
    Units: str = ""
    VariantOf: int = NoneType
    VariantPart = None
    Virtual: bool = False
    Parameters: list[PartParameter] = None
    Attachments: list[PartAttachment] = None
    Bom: list[BomItem] = None
    ManufacturerParts: list[ManufacturerPart] = None
    Log: Logger = Logger.Create(__name__)

    # Paths of the temporary files downloaded by KiTree
    ModelPath: str = None
    """Path to the temporary 3D-model file downloaded by DownloadCadData(). None when no 3D-Model was downloaded"""

    FootprintPath: str = None
    """Path to the temporary footprint file downloaded by DownloadCadData()"""

    SymbolPath: str = None
    """Path to the temporary symbol file downloaded by DownloadCadData()"""

    def __init__(self, partIpn: str | None):
        if partIpn is None:
            return 

        data = ITApi.GetPartDetails(partIpn)
        if data is None:
            raise Exception(f'Part {partIpn} does not exist!')

        self.CategoryDetail = PartCategory(data['category_detail'])

        self.Active = data['active']
        self.Assembly = data['assembly']
        self.Category = data['category']
        self.Component = data['component']
        self.DefaultExpiry = data['default_expiry']
        self.DefaultSupplier = data['default_supplier']
        self.Description = data['description']
        self.FullName = data['full_name']
        self.ImagePath = data['image']
        self.InStock = data['in_stock']
        self.Ordering = data['ordering']
        self.Building = data['building']
        self.IPN = data['IPN']
        self.IsTemplate = data['is_template']
        self.Keywords = data['keywords']
        self.Link = data['link']
        self.MinimumStock = data['minimum_stock']
        self.Name = data['name']
        self.Notes = data['notes']
        self.ID = data['pk']
        self.Purchaseable = data['purchaseable']
        self.Revision = data['revision']
        self.Salable = data['salable']
        self.Starred = data['starred']
        self.StockItemCount = data['stock_item_count']
        self.Suppliers = data['suppliers']
        self.ThumbnailPath = data['thumbnail']
        self.Trackable = data['trackable']
        self.Units = data['units']
        self.VariantOf = data['variant_of']
        self.Virtual = data['virtual']

        # Check if the part is a variant of another part and load it
        if self.VariantOf is not NoneType and self.VariantOf is not None:
            self.VariantPart = Part(ITApi.GetPartIpn(self.VariantOf))

        # Retrieve the part's parameter list
        parameterList = ITApi.GetPartParameters(self.ID)
        if parameterList is not None:
            self.Parameters = []
            for data in parameterList:
                self.Parameters.append(PartParameter(data))

        # Retrieve the part's attachment list
        attachmentList = ITApi.GetPartAttachments(self.ID)
        if attachmentList is not None:
            self.Attachments = []
            for data in attachmentList:
                self.Attachments.append(PartAttachment(data))

        # Retrieve the part's BOM items
        bomItems = ITApi.GetPartBomItems(self.ID)
        if bomItems is not None:
            self.Bom = []
            for data in bomItems:
                self.Bom.append(BomItem(data))

        # Get list of manufacturer parts for this Part
        parts = ITApi.GetManufacturerPartList(self.ID)
        if parts is not None:
            self.ManufacturerParts = []
            for part in parts:
                self.ManufacturerParts.append(ManufacturerPart(part))

    def DownloadCadData(self) -> bool:
        """Download the CAD data of the part to KiTree's temp directory
        
        Returns:
            True if at least a symbol and footprint were downloaded, otherwise False

        After successful return, the following will have valid paths to the downloaded files:
         - self.FootprintPath: Path to footprint (.kicad_mod) in KiTree temp folder
         - self.SymbolPath: Path to symbol (.kicad_sym) in KiTree temp folder

        After successful return, the following may be None (no file downloaded):
         - self.ModelPath: Path to 3D-model file in KiTree temp folder
        """

        def waterfallToComponentAttachment(component: Part, type: str) -> str:
            """Search for a component's attachment of given type by recursively checking its or its 
            parents (variants) attachments.

            Args:
                component (Part): Component to search for
                type (str): Type of attachment to get. Available: `3D-Model`, `Footprint`, `Symbol`

            Raises:
                Exception: Attachment of given type not found

            Returns:
                str: Relative path (URL) to the attachment
            """
            if component.Attachments is None:
                # If the component has no attachments registered, its parent may have the 
                # attachments assigned to. Search the parent or return None, if no parent is set.
                if component.VariantOf is not None:
                    return waterfallToComponentAttachment(component.VariantPart, type)
                else:
                    self.Log.warning(f'No asset of type "{type}" for {component.IPN} found!')
                    raise Exception()
            else:
                # Search in the part's attachments for the given attachment type and return its 
                # URL or None, if the requested attachment of the given type is not available.
                for item in component.Attachments:
                    if item.Comment == type:
                        self.Log.info(f'Using this asset of type "{type}" for {component.IPN}: {item.FileName}')
                        return item.Attachment
                else:
                    if component.VariantOf is not None:
                        return waterfallToComponentAttachment(component.VariantPart, type)
                    else:
                        self.Log.warning(f'No asset of type "{type}" for {component.IPN} found!')
                        raise Exception()

        # Footprint and symbol have to be present at all times
        try:
            footprintPath = waterfallToComponentAttachment(self, "Footprint")
            symbolPath = waterfallToComponentAttachment(self, "Symbol")
        except Exception:
            self.Log.error(f'Not all attachments for part "{self.IPN}" found!')
            return False
        
        # 3D-Model may be present, but could be omited
        try:
            modelPath = waterfallToComponentAttachment(self, "3D-Model")
        except Exception: 
            self.Log.warning(f'No 3D-model found for part "{self.IPN}"')
            modelPath = None

        # FIXME: Does this work every time KiTree is called?
        modelFolder = path.join(getcwd(), 'temp/', 'models/')
        fpFolder = path.join(getcwd(), 'temp/', 'footprints/')
        symbolFolder = path.join(getcwd(), 'temp/', 'symbols/')

        # Create temp paths
        makedirs(modelFolder, exist_ok=True)
        makedirs(fpFolder, exist_ok=True)
        makedirs(symbolFolder, exist_ok=True)

        itUrl = ITApi.Domain
        if itUrl[-1] == '/':
            itUrl.removesuffix('/')

        # Set 3D-Model path in part to None, if no 3D-Model was found in InvenTree
        self.ModelPath = (modelFolder + modelPath.split('/')[-1]) if modelPath is not None else None
        self.FootprintPath = fpFolder + footprintPath.split('/')[-1]
        self.SymbolPath = symbolFolder + symbolPath.split('/')[-1]

        # Download the component's files to the KiTree temp directory
        try:
            ITApi.Api.downloadFile(url=itUrl + footprintPath, destination=self.FootprintPath)
            self.Log.info(f'Downloaded footprint for part "{self.IPN}" to "{self.FootprintPath}"')
            ITApi.Api.downloadFile(url=itUrl + symbolPath, destination=self.SymbolPath)
            self.Log.info(f'Downloaded symbol for part "{self.IPN}" to "{self.FootprintPath}"')
        except Exception as ex:
            self.Log.error(f'Downloading attachments from Inventree API failed for part "{self.IPN}"!')
            self.Log.debug(f'Exception: {ex}')
            return False

        # Download the 3D-Model, if one was uploaded to InvenTree
        if self.ModelPath is not None:
            try:
                ITApi.Api.downloadFile(url=itUrl + modelPath, destination=self.ModelPath)
                self.Log.info(f'Downloaded 3D-model for part "{self.IPN}" to "{self.ModelPath}"')
            except Exception as ex:
                self.Log.warning(f'Downloading 3D-Model from Inventree API failed for part "{self.IPN}"!')
                self.Log.debug(f'Exception: {ex}')
        return True

    def GetSchematicId(self) -> str:
        """Retrieves the schematic identifier from the part's parameter list

        Returns:
            str: Schematic identifier or None, if it is not set
        """
        if self.Parameters is None:
            return None
        for item in self.Parameters:
            if item.TemplateDetail.Name == 'Schematic Identifier':
                return item.Data
        else:
            return None

    # FIXME: This only works when DownloadCadData() was called prior to that
    def GetFootprintName(self) -> str:
        return self.FootprintPath.split("/")[-1].removesuffix('.kicad_mod')

    def GetDatasheetUrl(self) -> str:
        """Retrieves the URL of the datasheet of the part

        Returns:
            str: URL to datasheet or contents of "link" parameter of the part if the datasheet 
            was not found in the attachment list (with comment `Datasheet`)
        """
        if self.Attachments is None:
            return ""
        for item in self.Attachments:
            if item.Comment == 'Datasheet':
                itUrl = ITApi.Domain
                if itUrl[-1] == '/':
                    itUrl.removesuffix('/')
                return f'{itUrl}{item.Attachment}'
        else:
            return (self.Link if self.Link is not None else "")

    def GetManufacturerName(self) -> str:
        """Retrieve the name of the manufacturer of the first manufacturer part

        Returns:
            str: Name of the manufacturer
        """
        if self.ManufacturerParts is None:
            return "n/a"
        if len(self.ManufacturerParts) == 0:
            return "n/a"
        return self.ManufacturerParts[0].Manufacturer.Description

    def GetMPN(self) -> str:
        """Retrieve the MPN of the first manufacturer part

        Returns:
            str: MPN of the first manufacturer part
        """
        if self.ManufacturerParts is None:
            return "n/a"
        if len(self.ManufacturerParts) == 0:
            return "n/a"
        return self.ManufacturerParts[0].MPN

    def GetSupplierName(self) -> str:
        """Retrieve the name of the supplier of the first manufacturer part's supplier part

        Returns:
            str: Name of the supplier of the first manufacturer part's supplier part
        """
        if self.ManufacturerParts is None:
            return "n/a"
        if len(self.ManufacturerParts) == 0:
            return "n/a"
        if len(self.ManufacturerParts[0].SupplierParts) == 0:
            return "n/a"
        return self.ManufacturerParts[0].SupplierParts[0].Supplier.Name

    def GetSKU(self) -> str:
        """Retrieve the SKU of the first manufacturer part's supplier part

        Returns:
            str: SKU of the first manufacturer part's supplier part
        """
        if self.ManufacturerParts is None:
            return "n/a"
        if len(self.ManufacturerParts) == 0:
            return "n/a"
        if len(self.ManufacturerParts[0].SupplierParts) == 0:
            return "n/a"
        return self.ManufacturerParts[0].SupplierParts[0].SKU

    def GetSupplierLink(self) -> str:
        """Retrieve the link to the supplier of the first manufacturer part's supplier part

        Returns:
            str: Link to the supplier page the first manufacturer part's supplier part
        """
        if self.ManufacturerParts is None:
            return "n/a"
        if len(self.ManufacturerParts) == 0:
            return "n/a"
        if len(self.ManufacturerParts[0].SupplierParts) == 0:
            return "n/a"
        return self.ManufacturerParts[0].SupplierParts[0].Link

    def ClearBom(self) -> bool:
        if self.Bom is None:
            return False

        for item in self.Bom:
            ITApi.DeleteBomItem(item.ID)
        return True
        