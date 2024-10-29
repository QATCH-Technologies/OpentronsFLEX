from opentrons import protocol_api

# metadata
metadata = {
    "protocolName": "It's Alive!",
    "author": "Paul MacNichol <paulmacnichol@gmail.com>",
    "description": "Simple protocol to get started using the Flex",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}

NUM_ROWS = 6


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_flex_96_tiprack_50ul", "D1")
    reservoir = protocol.load_labware("biorad_96_wellplate_200ul_pcr", "D2")
    nanovis = protocol.load_labware("nanovis_q_4x6", "D3")

    trash = protocol.load_trash_bin("A3")

    left_pipette = protocol.load_instrument(
        "flex_8channel_50", "left", tip_racks=[tips]
    )
    left_pipette.drop_tip(location=trash)
