"""InvenTree API wrapper

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from inventree.api import InvenTreeAPI
from misc.logger import Logger

class ITApi():
    User = ""
    Passwd = ""
    Domain = ""
    Api = None
    Connected = False
    Log = Logger.Create(__name__)

    @staticmethod
    def Connect(credentials: dict) -> bool:
        """Connects to an Inventree server

        Args:
            credentials (dict): Credentials for the inventree server as dict. Fields needed:
            "username", "password", "domain

        Returns:
            bool: True, if connection was successfull. Otherwise False
        """
        ITApi.User = credentials["username"]
        ITApi.Passwd = credentials["password"]
        ITApi.Domain = credentials["domain"]
        try:
            ITApi.Log.debug(f'Connecting to Inventree @ {ITApi.Domain}, Username: {ITApi.User}, PW: {ITApi.Passwd}')
            ITApi.Api = InvenTreeAPI(ITApi.Domain, username=ITApi.User, password=ITApi.Passwd, verbose=True)
            ITApi.Connected = True
        except Exception as ex:
            ITApi.Connected = False
            ITApi.Log.error(f'Connecting to Inventree failed! Exception: {ex}')

        return ITApi.Connected

    @staticmethod
    def GetPartDetails(partIpn: str) -> dict | None:
        """Retrieves details about a part from Inventree

        Args:
            partIpn (str): IPN of the part to retrieve details from

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: Dictionary containting information about the part as documented by api-doc
            None: Part does not exist
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        partId = ITApi.GetPartId(partIpn)
        if partId == -1:
            return None

        query = f"part/{partId}/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if type(result) != type({}) or len(result) == 0:
            return None

        return result

    @staticmethod
    def GetPartId(partIpn: str) -> int:
        """Gets the unique ID of an active part's IPN

        Args:
            partIpn (str): IPN of the part

        Raises:
            ConnectionError: API is not connected

        Returns:
            int: Unique ID of the part or -1, if the part does not exist, is not marked as active or
            the IPN is not unique
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        query = f'part/?IPN={partIpn}&active=true'
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) != 1:
            ITApi.Log.error(f"Received multiple variants of {partIpn}! Expected: 1, got: {len(result)}")
            return -1

        return int(result[0]["pk"])

    @staticmethod
    def GetPartIpn(partId: int) -> str | None:
        """Retrieves the part IPN of the given part ID

        Raises:
            ConnectionError: API is not connected

        Returns:
            str: IPN of the given part ID
            None: Part ID is negative or no part IPN was found
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"part/{partId}/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if type(result) != type({}) or len(result) == 0:
            return None

        return result['IPN']

    @staticmethod
    def GetPartParameters(partId: int) -> list | None:
        """Retrieves a part ID's parameters

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: Part parameters as a list of dicts
            None: Part ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"part/parameter/?template=&limit=&part={partId}&offset=/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0:
            return None

        return result

    @staticmethod
    def GetPartAttachments(partId: int) -> list | None:
        """Retrieves a part ID's attachments

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: Part attachments as a list of dicts
            None: Part ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"part/attachment/?part={partId}&offset=/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0:
            return None

        return result

    @staticmethod
    def GetPartBomItems(partId: int) -> list | None:
        """Retrieves a part ID's BOM items

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: Part BOM items as a list of dicts
            None: Part ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId <= 0:
            return None

        query = f"bom/?part={partId}&offset=/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0:
            return None

        return result

    @staticmethod
    def GetManufacturerPart(id: int) -> dict | None:
        """Retrieves a manufacturer part from Company/Part/Manufacturer/ID

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: ManufacturerPart as dictionary
            None: ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if id <= 0:
            return None

        query = f"company/part/manufacturer/{id}/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')


        if len(result) == 0 or type(result) != type({}):
            return None

        # This key is set when no results were found:
        if "detail" in result.keys():
            return None

        return result

    @staticmethod
    def GetCompany(id: int) -> dict | None:
        """Retrieves a company from Company/ID/

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: Company as dictionary
            None: ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if id <= 0:
            return None

        query = f"company/{id}/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type({}):
            return None

        # This key is set when no results were found:
        if "detail" in result.keys():
            return None

        return result

    @staticmethod
    def GetSupplierPart(id: int) -> dict | None:
        """Retrieves a company from Company/Part/ID/

        Raises:
            ConnectionError: API is not connected

        Returns:
            dict: SupplierPart as dictionary
            None: ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if id <= 0:
            return None

        query = f"company/part/{id}/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type({}):
            return None

        # This key is set when no results were found:
        if "detail" in result.keys():
            return None

        return result

    @staticmethod
    def GetSupplierPartList(partMpn: str) -> list | None:
        """Retrieves a list of all SupplierParts for a given part MPN

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: A list of SupplierParts as dicts
            None: ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        query = f"company/part/?search={partMpn}&offset=/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type([]):
            return None

        return result

    @staticmethod
    def GetManufacturerPartList(partId: int) -> list | None:
        """Retrieves a list of all ManufacturerParts for a given part ID

        Raises:
            ConnectionError: API is not connected

        Returns:
            list: A list of ManufacturerParts as dicts
            None: ID is negative or query did not yield any results
        """
        if not ITApi.IsConnected():
            ITApi.Log.critical(f'Not connected to Inventree API!')
            raise ConnectionError("Inventree API not connected")

        if partId < 0:
            return None

        query = f"company/part/manufacturer/?part={partId}&ordering=/"
        result = ITApi.Api.get(query)
        ITApi.Log.debug(f'Requesting API at { query }')

        if len(result) == 0 or type(result) != type([]):
            return None

        return result

    @staticmethod
    def PartExists(partIpn: str) -> bool:
        """Checks if a part exists

        Args:
            partIpn (str): IPN of the part

        Returns:
            bool: True if the part exists. False if not or if the API is not connected
        """
        partId = -1
        try:
            partId = ITApi.GetPartId(partIpn)
        except:
            partId = -1
        return partId != -1

    @staticmethod
    def IsConnected() -> bool:
        """Check if the API was connected

        Returns:
            bool: True, if the Connect() function was called and succeeded. Otherwise False
        """
        return ITApi.Connected

    @staticmethod
    def DeleteBomItem(bomItemId: int) -> bool:
        """Deletes a BOM item with the given ID

        Args:
            bomItemId (int): ID of the BOM item to delete

        Returns:
            bool: True if successfull, otherwise False
        """
        if not ITApi.IsConnected:
            ITApi.Log.critical(f'Not connected to Inventree API!')
            return False

        # TODO: Guard this more
        ITApi.Log.debug(f'Deleting BOM item at /bom/{bomItemId}/')
        ITApi.Api.delete(f'bom/{bomItemId}/')
        return True

    @staticmethod
    def CreateBomItem(partIpn: str, bomItemIpn: str, quantity: int, references: list[str]) -> bool:
        """Creates a BOM item for the given part

        Args:
            partIpn (str): IPN of the parent part
            bomItemIpn (str): IPN of the part that should be added to the BOM
            quantity (int): Ammount of that part on the BOM
            references (list[str]): Schematic references as list of strings

        Returns:
            bool: True if the item was added. Otherwise False
        """
        if not ITApi.IsConnected:
            ITApi.Log.critical(f'Not connected to Inventree API!')
            return False

        partId = ITApi.GetPartId(partIpn)
        if partId == -1:
            ITApi.Log.error(f'Part ID of {partIpn} could not be retrieved!')
            return False

        bomItemId = ITApi.GetPartId(bomItemIpn)
        if partId == -1:
            ITApi.Log.error(f'Part ID of {bomItemIpn} could not be retrieved!')
            return False

        partData = {
            "part": partId,
            "quantity": quantity,
            "sub_part": bomItemId,
            "reference": ", ".join(references)
        }
        ITApi.Log.debug(f'Adding {quantity}x {bomItemIpn} to BOM of part {partIpn} ({partId})')
        try:
            ITApi.Api.post("bom/", partData)
        except:
            return False
        return True