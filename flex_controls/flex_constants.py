from enum import Enum


class FlexPipettes(Enum):
    EMPTY = 'None'
    P50_SINGLE_FLEX = 'p50_single_flex'
    P50_MULTI_FLEX = 'p50_multi_flex'
    P1000_SINGLE_FLEX = 'p1000_single_flex'
    P1000_MULTI_FLEX = 'p1000_multi_flex'


class FlexCommandType(Enum):
    LOAD_PIPETTE = 'loadPipette'
    LOAD_LABWARE = 'loadLabware'


class FlexMountPositions(Enum):
    LEFT_MOUNT = "left"
    RIGHT_MOUNT = "right"


class FlexWells(Enum):
    WellA1: "A1"
    WellA2: "A2"
    WellA3: "A3"
    WellA4: "A4"
    WellB1: "B1"
    WellB2: "B2"
    WellB3: "B3"
    WellB4: "B4"
    WellC1: "C1"
    WellC2: "C2"
    WellC3: "C3"
    WellC4: "C4"
    WellD1: "D1"
    WellD2: "D2"
    WellD3: "D3"
    WellD4: "D4"


ROBOT_IP = "172.28.24.236"
HEADERS = {"opentrons-version": "3"}

TIP_RACK = "opentrons_flex_96_tiprack_50ul"
RESERVOIR = "biorad_96_wellplate_200ul_pcr"
PIPETTE = "p50_multi_flex"
