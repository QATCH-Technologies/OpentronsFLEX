import opentrons.execute
from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, ALL
import subprocess
# os.system("systemctl stop opentrons-robot-server")
# os.system("systemctl start opentrons-robot-server")


# metadata
metadata = {
    "protocolName": "External Control",
    "author": "Paul MacNichol <paulmacnichol@gmail.com>",
    "description": "Testing external control on the opentron.",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

NUM_COLS = 6


def start_service(service_name):
    try:
        # Run the command to start the service
        subprocess.run(["net", "start", service_name], check=True)
        print(f"Service '{service_name}' started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start service '{service_name}'. Error: {e}")


def stop_service(service_name):
    try:
        # Run the command to stop the service
        subprocess.run(["net", "stop", service_name], check=True)
        print(f"Service '{service_name}' stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop service '{service_name}'. Error: {e}")


def run(protocol: protocol_api.ProtocolContext):
    reservoir = protocol.load_labware("biorad_96_wellplate_200ul_pcr", "D2")
    nanovis = protocol.load_labware("nanovis_q_4x6", "D3")
    trash = protocol.load_trash_bin("A3")

    partial_rack = protocol.load_labware(
        load_name="opentrons_flex_96_tiprack_50ul", location="D1"
    )

    left_pipette = protocol.load_instrument("flex_8channel_50", "left")
    left_pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end="E1")
    tips_by_row = partial_rack.rows_by_name()["D"] + partial_rack.rows_by_name()["H"]

    for i in range(NUM_COLS):
        pickup_location = tips_by_row.pop(0)
        left_pipette.pick_up_tip(location=pickup_location)
        left_pipette.aspirate(3, reservoir[f"D{i+1}"])
        left_pipette.dispense(3, nanovis[f"D{i+1}"])
        protocol.delay(seconds=1)
        left_pipette.drop_tip(location=trash)


if __name__ == "__main__":
    start_service("opentrons-robot-server")
    protocol = opentrons.execute.get_protocol_api("2.20")
    protocol.set_rail_lights(on=True)
    protocol.home()
    run(protocol)
    protocol.set_rail_lights(on=False)
