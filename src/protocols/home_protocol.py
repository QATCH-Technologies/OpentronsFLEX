from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, ALL

# metadata
metadata = {
    "protocolName": "Home Protocol",
    "author": "Paul MacNichol <paulmacnichol@gmail.com>",
    "description": "Protocol to home pipette head.",
}

requirements = {"robotType": "Flex", "apiLevel": "2.20"}


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_flex_96_tiprack_50ul", "D1")

    left_pipette = protocol.load_instrument(
        "flex_8channel_50", "left", tip_racks=[tips]
    )
    left_pipette.home()
