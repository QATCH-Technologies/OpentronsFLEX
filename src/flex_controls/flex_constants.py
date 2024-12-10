"""
Module: flex_constants
=======================

This module contains constants and enumerations used for managing and interacting with the Opentrons Flex device.
It defines configuration details, hardware components, and operational commands.

Constants:
----------
    HTTP_PORT (str): Default HTTP port for communication.
    HEADERS (dict): HTTP headers specifying the Opentrons version.
    CONFIG_FILE (str): Name of the device configuration file.

Enumerations:
-------------
    FlexAxis: Defines the axes (X, Y, Z) used for device movements.
    FlexPipettes: Specifies available pipettes for the Opentrons Flex device.
    FlexStandardTipRacks: Lists the standard tip racks supported by the device.
    FlexCommandType: Contains commands supported by the device for various operations.
    FlexMountPositions: Represents the mount positions (left or right) for pipettes.
    FlexDeckLocations: Defines deck locations on the device for labware or modules.
    FlexIntents: Specifies high-level intents for device operation.
    FlexActions: Contains operational actions like pause, play, and stop.
    FlexLights: Specifies light states (on/off) for the device.

Classes:
--------
    FlexSlotName: 
        Contains utility methods for retrieving slot names based on deck location.

Example Usage:
--------------
    from flex_constants import FlexAxis, FlexPipettes, FlexCommandType

    # Accessing an axis:
    axis = FlexAxis.X.value

    # Using a command:
    command = FlexCommandType.ASPIRATE.value
"""

from enum import Enum
"""str: Default HTTP port for communication."""
HTTP_PORT = "31950"

"""dict: HTTP headers specifying the Opentrons version."""
HEADERS = {"opentrons-version": "3"}

"""str: Name of the device configuration file."""
CONFIG_FILE = "device_config.json"


class FlexAxis(Enum):
    """Enumeration of axes for device movement."""
    X = "x"
    Y = "y"
    Z = "z"


class FlexPipettes(Enum):
    """Enumeration of pipettes supported by the Opentrons Flex device."""
    EMPTY = "None"
    P50_SINGLE_FLEX = "p50_single_flex"
    P50_MULTI_FLEX = "p50_multi_flex"
    P300_SINGLE_FLEX_GEN2 = "p300_single_gen2"
    P1000_SINGLE_FLEX = "p1000_single_flex"
    P1000_MULTI_FLEX = "p1000_multi_flex"


class FlexStandardTipRacks(Enum):
    """Enumeration of standard tip racks for the device."""
    TR_96_50 = "opentrons_flex_96_tiprack_50ul"
    TR_96_200 = "opentrons_flex_96_tiprack_200ul"
    TR_96_300 = "opentrons_96_tiprack_300ul"
    TR_96_1000 = "opentrons_flex_96_filtertiprack_1000ul"
    FTR_96_50 = "opentrons_flex_96_filtertiprack_50ul"
    FTR_96_200 = "opentrons_flex_96_filtertiprack_200ul"
    FTR_96_300 = "opentrons_96_filtertiprack_300ul"
    FTR_96_1000 = "opentrons_flex_96_filtertiprack_1000ul"


class FlexCommandType(Enum):
    """Enumeration of commands supported by the device."""
    LOAD_PIPETTE = "loadPipette"
    LOAD_LABWARE = "loadLabware"
    PICKUP_TIP = "pickUpTip"
    ASPIRATE = "aspirate"
    DISPENSE = "dispense"
    BLOWOUT = "blowout"
    DROP_TIP = "dropTip"
    MOVE_TO_WELL = "moveToWell"
    MOVE_TO_COORDINATES = "moveToCoordinates"
    MOVE_RELATIVE = "moveRelative"


class FlexMountPositions(Enum):
    """Enumeration of pipette mount positions."""
    LEFT_MOUNT = "left"
    RIGHT_MOUNT = "right"


class FlexDeckLocations(Enum):
    """Enumeration of deck locations on the device."""
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"


class FlexSlotName:
    """
    Utility class for mapping deck locations to slot names.

    Methods:
    --------
        get_slot_name(location): Retrieves the slot name corresponding to a deck location.
    """

    @staticmethod
    def get_slot_name(location):
        """
        Retrieve the slot name for a given deck location.

        Args:
            location (FlexDeckLocations): The deck location.

        Returns:
            dict: A dictionary containing the slot name, or None if the location is invalid.
        """
        slot_names = {
            FlexDeckLocations.A1: {"slotName": 1},
            FlexDeckLocations.A2: {"slotName": 2},
            FlexDeckLocations.A3: {"slotName": 3},
            FlexDeckLocations.A4: {"slotName": 4},
            FlexDeckLocations.B1: {"slotName": 5},
            FlexDeckLocations.B2: {"slotName": 6},
            FlexDeckLocations.B3: {"slotName": 7},
            FlexDeckLocations.B4: {"slotName": 8},
            FlexDeckLocations.C1: {"slotName": 9},
            FlexDeckLocations.C2: {"slotName": 10},
            FlexDeckLocations.C3: {"slotName": 11},
            FlexDeckLocations.C4: {"slotName": 12},
            FlexDeckLocations.D1: {"slotName": 13},
            FlexDeckLocations.D2: {"slotName": 14},
            FlexDeckLocations.D3: {"slotName": 15},
            FlexDeckLocations.D4: {"slotName": 16},
        }
        return slot_names.get(location)


class FlexIntents(Enum):
    """Enumeration of high-level intents for device operation."""
    SETUP = "setup"


class FlexActions(Enum):
    """Enumeration of operational actions."""
    PAUSE = "pause"
    PLAY = "play"
    STOP = "stop"
    RESUME = "resume"


class FlexLights(Enum):
    """Enumeration of light states."""
    ON = {"on": True}
    OFF = {"on": False}
