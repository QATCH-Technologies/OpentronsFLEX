from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, ALL

# metadata
metadata = {
    "protocolName": "It's Alive! (Dev)",
    "author": "Paul MacNichol <paulmacnichol@gmail.com>",
    "description": "Simple protocol to get started using the Flex",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

NUM_COLS = 6


def run(protocol: protocol_api.ProtocolContext):
    reservoir = protocol.load_labware("biorad_96_wellplate_200ul_pcr", "D2")
    pool = protocol.load_labware("biorad_96_wellplate_200ul_pcr", "B2")
    swamp = protocol.load_labware("biorad_96_wellplate_200ul_pcr", "B3")
    # swamp = protocol.load_trash_bin("B3")
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
        left_pipette.aspirate(6, reservoir[f"D{i+1}"])
        left_pipette.dispense(3, nanovis[f"D{i+1}"])
        # protocol.delay(minute=2, seconds=1)
        protocol.pause(msg="Pausing for measurements...")
        left_pipette.aspirate(47, pool[f"D{i+1}"])
        left_pipette.dispense(50, swamp[f"D{i+1}"])
        # left_pipette.blow_out(location=swamp)
        # left_pipette.return_tip()
        left_pipette.drop_tip(location=trash)
