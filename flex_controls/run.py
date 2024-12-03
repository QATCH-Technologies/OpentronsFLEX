from opentrons_flex import OpentronsFlex
from flex_constants import FlexDeckLocations, FlexPipettes, FlexMountPositions
from standard_labware import StandardReservoirs


if __name__ == "__main__":
    robot = OpentronsFlex(mac_address="34:6F:24:31:17:EF",
                          ip_address="172.28.24.236")
    robot.lights_off()
    robot.lights_on()
    robot.lights_off()
    robot.lights_on()
    input()
    robot.upload_protocol(r'C:\Users\QATCH\dev\OpentronsFLEX\its_alive_dev.py')
    # robot.load_labware(location=FlexDeckLocations.A1,
    #                    labware_definition=StandardReservoirs.AGILENT_1_RESERVOIR_290ML)
    # robot.load_labware(location=FlexDeckLocations.A2,
    #                    labware_file_path=r'labware\nanovis_q_4x6.json')
    # robot.load_pipette(FlexPipettes.P50_MULTI_FLEX,
    #                    FlexMountPositions.LEFT_MOUNT)
    # input(robot.gantry.get(FlexMountPositions.LEFT_MOUNT))
    # robot.aspirate(robot.available_labware.get(
    #     FlexDeckLocations.A1), robot.gantry.get(FlexMountPositions.LEFT_MOUNT), 100, 50)
    # print(robot._get_available_labware().get(
    #     FlexDeckLocations.A1).get_display_name())
    # print(robot._get_left_pipette().get_id())
