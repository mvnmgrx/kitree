"""InvenTree API wrapper

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass, field
from typing import Optional
from inventree.api import InvenTreeAPI
from requests import HTTPError
from components.data import Credentials
from misc.logger import Logger

@dataclass
class InvenTreeApi():
    api = None
    connected: bool = False
    credentials: Credentials = field(default_factory=lambda: Credentials())
    log = Logger.Create(__name__)

    def connect(self, credentials: Credentials) -> bool:
        """Connects to an Inventree server

        Args:
            credentials (dict): Credentials for the inventree server as dict. Fields needed:
            "username", "password", "domain

        Returns:
            bool: True, if connection was successfull. Otherwise False
        """
        self.credentials.domain = credentials.domain
        self.credentials.id = credentials.id
        self.credentials.username = credentials.username
        self.credentials.password = credentials.password
        try:
            self.log.debug(f'Connecting to Inventree @ {self.credentials.domain}, Username: {self.credentials.username}, PW: <redacted>')
            self.api = InvenTreeAPI(self.credentials.domain, 
                                    username=self.credentials.username, 
                                    password=self.credentials.password, 
                                    verbose=True)
            self.connected = True
        except Exception as ex:
            self.connected = False
            self.log.error(f'Connecting to Inventree failed! Exception: {ex}')

        return self.connected

    def get_part_detail(self, partIpn: str) -> Optional[dict]:
        """Retrieves details about a part from Inventree

        Args:
            partIpn (str): IPN of the part to retrieve details from

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: Dictionary containting information about the part as documented by api-doc
            None: Part does not exist
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        partId = self.get_part_id(partIpn)
        if partId == -1:
            return None

        query = f"part/{partId}/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if type(result) != type({}) or len(result) == 0:
            return None

        return result

    def get_part_id(self, partIpn: str) -> int:
        """Gets the unique ID of an active part's IPN

        Args:
            partIpn (str): IPN of the part

        Raises:
            ConnectionError: API is not connected

        Returns:
            int: Unique ID of the part or -1, if the part does not exist, is not marked as active or
            the IPN is not unique
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        query = f'part/?IPN={partIpn}&active=true'
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) != 1:
            self.log.error(f"Received multiple variants of {partIpn}! Expected: 1, got: {len(result)}")
            return -1

        return int(result[0]["pk"])

    def get_part_ipn(self, partId: int) -> Optional[str]:
        """Retrieves the part IPN of the given part ID

        Raises:
            ConnectionError: API is not connected

        Returns:
            str: IPN of the given part ID
            None: Part ID is negative or no part IPN was found
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"part/{partId}/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if type(result) != type({}) or len(result) == 0:
            return None

        return result['IPN']

    def get_part_parameters(self, partId: int) -> Optional[list]:
        """Retrieves a part ID's parameters

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: Part parameters as a list of dicts
            None: Part ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"part/parameter/?template=&limit=&part={partId}&offset=/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) == 0:
            return None

        return result

    def get_part_attachments(self, partId: int) -> Optional[list]:
        """Retrieves a part ID's attachments

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: Part attachments as a list of dicts
            None: Part ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"part/attachment/?part={partId}&offset=/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) == 0:
            return None

        return result

    def get_part_bom_items(self, partId: int) -> Optional[list]:
        """Retrieves a part ID's BOM items

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: Part BOM items as a list of dicts
            None: Part ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"bom/?part={partId}&offset=/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) == 0:
            return None

        return result

    def get_manufacturer_part(self, id: int) -> Optional[dict]:
        """Retrieves a manufacturer part from Company/Part/Manufacturer/ID

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: ManufacturerPart as dictionary
            None: ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if id <= 0:
            return None

        query = f"company/part/manufacturer/{id}/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')


        if len(result) == 0 or type(result) != type({}):
            return None

        # This key is set when no results were found:
        if "detail" in result.keys():
            return None

        return result

    def get_company(self, id: int) -> Optional[dict]:
        """Retrieves a company from Company/ID/

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: Company as dictionary
            None: ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if id <= 0:
            return None

        query = f"company/{id}/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type({}):
            return None

        # This key is set when no results were found:
        if "detail" in result.keys():
            return None

        return result

    def get_supplier_part(self, id: int) -> Optional[dict]:
        """Retrieves a company from Company/Part/ID/

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: SupplierPart as dictionary
            None: ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if id <= 0:
            return None

        query = f"company/part/{id}/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type({}):
            return None

        # This key is set when no results were found:
        if "detail" in result.keys():
            return None

        return result

    def get_supplier_part_list(self, partMpn: str) -> Optional[list]:
        """Retrieves a list of all SupplierParts for a given part MPN

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: A list of SupplierParts as dicts
            None: ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        query = f"company/part/?search={partMpn}&offset=/"
        result = self.api.get(query)
        self.log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type([]):
            return None

        return result

    def get_manufacturer_part_list(self, partId: int) -> Optional[list]:
        """Retrieves a list of all ManufacturerParts for a given part ID

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: A list of ManufacturerParts as dicts
            None: ID is negative or query did not yield any results
        """
        if not self.is_connected():
            self.log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId < 0:
            return None

        query = f"company/part/manufacturer/?part={partId}&ordering=/"
        self.log.debug(f'Requesting API at { query }')
        try:
            result = self.api.get(query)
        except HTTPError:
            return None

        if len(result) == 0 or type(result) != type([]):
            return None

        return result

    def part_exists(self, partIpn: str) -> bool:
        """Checks if a part exists

        Args:
            partIpn (str): IPN of the part

        Returns:
            bool: True if the part exists. False if not or if the API is not connected
        """
        partId = -1
        try:
            partId = self.get_part_id(partIpn)
        except:
            partId = -1
        return partId != -1

    def is_connected(self) -> bool:
        """Check if the API was connected

        Returns:
            bool: True, if the connect() function was called and succeeded. Otherwise False
        """
        return self.connected

    def delete_bom_item(self, bomItemId: int) -> bool:
        """Deletes a BOM item with the given ID

        Args:
            bomItemId (int): ID of the BOM item to delete

        Returns:
            bool: True if successfull, otherwise False
        """
        if not self.is_connected:
            self.log.critical(f'Not connected to Inventree API!')
            return False

        # TODO: Guard this more
        self.log.debug(f'Deleting BOM item at /bom/{bomItemId}/')
        self.api.delete(f'bom/{bomItemId}/')
        return True

    def create_bom_item(self, partIpn: str, bomItemIpn: str, quantity: int, references: list[str]) -> bool:
        """Creates a BOM item for the given part

        Args:
            partIpn (str): IPN of the parent part
            bomItemIpn (str): IPN of the part that should be added to the BOM
            quantity (int): Ammount of that part on the BOM
            references (list[str]): Schematic references as list of strings

        Returns:
            bool: True if the item was added. Otherwise False
        """
        if not self.is_connected:
            self.log.critical(f'Not connected to Inventree API!')
            return False

        partId = self.get_part_id(partIpn)
        if partId == -1:
            self.log.error(f'Part ID of {partIpn} could not be retrieved!')
            return False

        bomItemId = self.get_part_id(bomItemIpn)
        if partId == -1:
            self.log.error(f'Part ID of {bomItemIpn} could not be retrieved!')
            return False

        partData = {
            "part": partId,
            "quantity": quantity,
            "sub_part": bomItemId,
            "reference": ", ".join(references)
        }
        self.log.debug(f'Adding {quantity}x {bomItemIpn} to BOM of part {partIpn} ({partId})')
        try:
            self.api.post("bom/", partData)
        except:
            return False
        return True