from opentrons_flex import OpentronsFlex
from flex_constants import FlexDeckLocations, FlexPipettes, FlexMountPositions
from standard_labware import StandardReservoirs
import time

if __name__ == "__main__":
    robot = OpentronsFlex(mac_address="34:6F:24:31:17:EF", ip_address="172.28.24.236")
    robot.upload_protocol_custom_labware(
        protocol_file_path=r"C:\Users\QATCH\dev\OpentronsFLEX\its_alive_dev.py",
        custom_labware_file_path=r"C:\Users\QATCH\dev\OpentronsFLEX\labware\nanovis_q_4x6.json",
    )
    robot.run_protocol(protocol_name="It's Alive! (Dev)")
    # robot.play_run()
