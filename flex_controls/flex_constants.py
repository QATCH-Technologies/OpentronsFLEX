from enum import Enum
import json

ROBOT_IP = "172.28.24.236"
HEADERS = {"opentrons-version": "3"}


class FlexAxis(Enum):
    X = 'x'
    Y = 'y'
    Z = 'z'


class FlexPipettes(Enum):
    EMPTY = 'None'
    P50_SINGLE_FLEX = 'p50_single_flex'
    P50_MULTI_FLEX = 'p50_multi_flex'
    P1000_SINGLE_FLEX = 'p1000_single_flex'
    P1000_MULTI_FLEX = 'p1000_multi_flex'


class FlexCommandType(Enum):
    LOAD_PIPETTE = 'loadPipette'
    LOAD_LABWARE = 'loadLabware'
    PICKUP_TIP = 'pickUpTip'
    ASPIRATE = 'aspirate'
    DISPENSE = 'dispense'
    BLOWOUT = 'blowout'
    DROP_TIP = 'dropTip'
    MOVE_TO_WELL = 'moveToWell'
    MOVE_TO_COORDINATES = 'moveToCoordinates'
    MOVE_RELATIVE = 'moveRelative'


class FlexMountPositions(Enum):
    LEFT_MOUNT = "left"
    RIGHT_MOUNT = "right"


class FlexLocations(Enum):
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


class FlexIntents(Enum):
    SETUP = "setup"


class FlexActions(Enum):
    PAUSE = "pause"
    PLAY = 'play'
    STOP = 'stop'


class FlexLights(Enum):
    ON = json.dumps({"on": True})
    OFF = json.dumps({"on": False})


TIP_RACK = "opentrons_flex_96_tiprack_50ul"
RESERVOIR = "biorad_96_wellplate_200ul_pcr"
PIPETTE = "p50_multi_flex"
