from opentrons_flex import OpentronsFlex
from flex_constants import FlexDeckLocations, FlexPipettes, FlexMountPositions
from standard_labware import StandardReservoirs
import time

if __name__ == "__main__":
    robot = OpentronsFlex(mac_address="34:6F:24:31:17:EF", ip_address="172.28.24.236")
    robot.upload_protocol(r"C:\Users\QATCH\dev\OpentronsFLEX\home_protocol.py")
    robot.run_protocol("Home Protocol")
