"""Company components of an InvenTree part

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass, field
from types import NoneType
from typing import Optional

from api.inventree import InvenTreeApi

@dataclass
class Company():
    """This class represents a Company of the Inventree API
    """
    ID: int = -1
    Url: str = ""
    Name: str = ""
    Description: str = ""
    Website: str = ""
    Phone: str = ""
    Address: str = ""
    EMail: str = None
    Currency: str = ""
    Contact: str = ""
    Link: str = ""
    ImagePath: str = ""
    IsCustomer: bool = False
    IsManufacturer: bool = False
    IsSupplier: bool = False
    Notes: str = ""
    PartsSupplied: int = 0
    PartsManufactured: int = 0

    def __init__(self, data: dict | None = None):
        """Initializes a Company object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        if data is None:
            return

        self.ID = data['pk']
        self.Url = data['url']
        self.Name = data['name']
        self.Description = data['description']
        self.Website = data['website']
        self.Phone = data['phone']
        self.Address = data['address']
        self.EMail = data['email']
        self.Currency = data['currency']
        self.Contact = data['contact']
        self.Link = data['link']
        self.ImagePath = data['image']
        self.IsCustomer = data['is_customer']
        self.IsManufacturer = data['is_manufacturer']
        self.IsSupplier = data['is_supplier']
        self.Notes = data['notes']
        self.PartsSupplied = data['parts_supplied']
        self.PartsManufactured = data['parts_manufactured']

@dataclass
class SupplierPart():
    """This class represents a Company/Part of the Inventree API
    """
    api: InvenTreeApi = None

    Description: str = ""
    Link: str = ""
    ManufacturerPart: int = -1
    #ManufacturerPart: ManufacturerPart = ManufacturerPart(None)
    Note: str = ""
    ID: int = -1
    Packaging: str = ""
    Part: int = -1
    SKU: str = ""
    Supplier: Company = field(default_factory=lambda: Company(None))

    def __init__(self, api: InvenTreeApi, data: Optional[dict] = None):
        """Initializes a SupplierPart object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        self.api = api
        if data is None:
            return

        self.Description = data['description']
        self.Link = data['link']
        self.ManufacturerPart = data['manufacturer_part']
        self.Note = data['note']
        self.ID = data['pk']
        self.Packaging = data['packaging']
        self.Part = data['part']
        self.SKU = data['SKU']

        # Load supplier data from Inventree
        company = self.api.get_company(data['supplier'])
        if company is not None:
            self.Supplier = Company(company)

        # Get manufacturer part of this supplier part
        #manPart = ITApi.GetManufacturerPart(data['manufacturer_part'])
        #if manPart is not None:
        #    self.ManufacturerPart = ManufacturerPart(manPart)

@dataclass
class ManufacturerPart():
    """This class represents a Company/Part/Manufacturer of the Inventree API
    """
    api: InvenTreeApi = None

    ID: int = -1
    Part: int = -1
    Manufacturer: Company = field(default_factory=lambda: Company(None))
    Description: str = ""
    MPN: str = ""
    Link: str = ""
    SupplierParts: list[SupplierPart] = None

    def __init__(self, api: InvenTreeApi, data: Optional[dict] = None):
        """Initializes a ManufacturerPart object with the data obtained from Inventree API

        Args:
            data (dict): Data from Inventree API or None to create an empty object
        """
        self.api = api
        if data is None:
            return

        self.ID = data['pk']
        self.Part = data['part']
        self.Description = data['description']
        self.MPN = data['MPN']
        self.Link = data['link']

        # Load manufacturer data from Inventree
        company = self.api.get_company(data['manufacturer'])
        if company is not None:
            self.Manufacturer = Company(company)

        # Get a list of supplier parts for this manufacturer part
        parts = self.api.get_supplier_part_list(self.MPN)
        if parts is not None:
            self.SupplierParts = []
            for part in parts:
                self.SupplierParts.append(SupplierPart(self.api, part))




