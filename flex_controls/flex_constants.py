from enum import Enum
import json

ROBOT_IP = "172.28.24.236"
ROBOT_PORT = "31950"
HEADERS = {"opentrons-version": "3"}


class FlexAxis(Enum):
    X = 'x'
    Y = 'y'
    Z = 'z'


class FlexPipettes(Enum):
    EMPTY = 'None'
    P50_SINGLE_FLEX = 'p50_single_flex'
    P50_MULTI_FLEX = 'p50_multi_flex'
    P300_SINGLE_FLEX_GEN2 = "p300_single_gen2"
    P1000_SINGLE_FLEX = 'p1000_single_flex'
    P1000_MULTI_FLEX = 'p1000_multi_flex'


class FlexStandardTipRacks(Enum):
    TR_96_50 = "opentrons_flex_96_tiprack_50ul"
    TR_96_200 = "opentrons_flex_96_tiprack_200ul"
    TR_96_300 = "opentrons_96_tiprack_300ul"
    TR_96_1000 = "opentrons_flex_96_filtertiprack_1000ul"
    FTR_96_50 = "opentrons_flex_96_filtertiprack_50ul"
    FTR_96_200 = "opentrons_flex_96_filtertiprack_200ul"
    FTR_96_300 = "opentrons_96_filtertiprack_300ul"
    FTR_96_1000 = "opentrons_flex_96_filtertiprack_1000ul"


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


class FlexDeckLocations(Enum):
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

    @staticmethod
    def get_slot_name(location):
        slot_names = {FlexDeckLocations.A1: {'slotName': 1},
                      FlexDeckLocations.A2: {'slotName': 2},
                      FlexDeckLocations.A3: {'slotName': 3},
                      FlexDeckLocations.A4: {'slotName': 4},
                      FlexDeckLocations.B1: {'slotName': 5},
                      FlexDeckLocations.B2: {'slotName': 6},
                      FlexDeckLocations.B3: {'slotName': 7},
                      FlexDeckLocations.B4: {'slotName': 8},
                      FlexDeckLocations.C1: {'slotName': 9},
                      FlexDeckLocations.C2: {'slotName': 10},
                      FlexDeckLocations.C3: {'slotName': 11},
                      FlexDeckLocations.C4: {'slotName': 12},
                      FlexDeckLocations.D1: {'slotName': 13},
                      FlexDeckLocations.D2: {'slotName': 14},
                      FlexDeckLocations.D3: {'slotName': 15},
                      FlexDeckLocations.D4: {'slotName': 16}, }
        return slot_names.get(location)


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
