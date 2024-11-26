import json
import requests
from flex_constants import FlexCommandType, FlexIntents, FlexAxis, FlexDeckLocations, HEADERS
from flex_pipette import FlexPipette
from flex_labware import FlexLabware


class FlexCommands:

    @staticmethod
    def _create_base_command(command_type: FlexCommandType, params: dict, intents: FlexIntents):
        """Creates the base structure for the command with common functionality."""
        return {
            "data": {
                "commandType": command_type.value,
                "params": params,
                "intent": intents.value
            }
        }

    @staticmethod
    def load_labware(location: FlexDeckLocations, load_name: str, name_space: str, version: int):
        """Creates a command body for loading labware."""
        params = {
            "location": location.value,
            "loadName": load_name,
            "namespace": name_space,
            "version": version
        }
        return FlexCommands._create_base_command(FlexCommandType.LOAD_LABWARE, params, FlexIntents.SETUP)

    @ staticmethod
    def load_pipette(pipette: FlexPipette):
        """Creates a command body for loading a pipette."""
        params = {
            "pipetteName": pipette.get_pipette(),
            "mount": pipette.get_mount_position(),
        }
        return FlexCommands._create_base_command(FlexCommandType.LOAD_PIPETTE, params, FlexIntents.SETUP)

    @staticmethod
    def pickup_tip(labware: FlexLabware, pipette: FlexPipette):
        """Creates a command body for picking up a tip."""
        params = {"labwareId": labware.get_id(),
                  "wellName": labware.get_location(),
                  "wellLocation": {
                      "origin": "top", "offset": labware.get_offsets()},
                  "pipetteId": pipette.get_id()
                  }
        return FlexCommands._create_base_command(FlexCommandType.PICKUP_TIP, params, FlexIntents.SETUP)

    @staticmethod
    def aspirate(labware: FlexLabware, pipette: FlexPipette, flow_rate: float, volume: float):
        """Creates a command aspirating liquid."""
        params = {"labwareId": labware.get_id(),
                  "wellName": labware.get_location(),
                  "wellLocation": {
            "origin": "top", "offset": labware.get_offsets()},
            "flowRate": flow_rate,
            "volume": volume,
            "pipetteId": pipette.get_id()
        }
        return FlexCommands._create_base_command(FlexCommandType.ASPIRATE, params, FlexIntents.SETUP)

    @staticmethod
    def dispense(labware: FlexLabware, pipette: FlexPipette, flow_rate: float, volume: float):
        """Creates a command body for dispensing liquid."""
        params = {"labwareId": labware.get_id(),
                  "wellName": labware.get_location(),
                  "wellLocation": {
            "origin": "top", "offset": labware.get_offsets()},
            "flowRate": flow_rate,
            "volume": volume,
            "pipetteId": pipette.get_id()
        }
        return FlexCommands._create_base_command(FlexCommandType.DISPENSE, params, FlexIntents.SETUP)

    @staticmethod
    def blowout(labware: FlexLabware, pipette: FlexPipette, flow_rate: float):
        """Creates a command body for blowing out tips."""
        params = {"labwareId": labware.get_id(),
                  "wellName": labware.get_location(),
                  "wellLocation": {
            "origin": "top", "offset": labware.get_offsets()},
            "flowRate": flow_rate,
            "pipetteId": pipette.get_id()
        }
        return FlexCommands._create_base_command(FlexCommandType.BLOWOUT, params, FlexIntents.SETUP)

    @staticmethod
    def drop_tip(labware: FlexLabware, pipette: FlexPipette):
        """Creates a command body for drop tips."""
        params = {"labwareId": labware.get_id(),
                  "wellName": labware.get_location(),
                  "wellLocation": {
            "origin": "top", "offset": labware.get_offsets()},
            "pipetteId": pipette.get_id()
        }
        return FlexCommands._create_base_command(FlexCommandType.DROP_TIP, params, FlexIntents.SETUP)

    @staticmethod
    def move_to_well(labware: FlexLabware, pipette: FlexPipette):
        """Creates a command body moving to a well"""
        params = {"labwareId": labware.get_id(),
                  "wellName": labware.get_location(),
                  "wellLocation": {
            "origin": "top", "offset": labware.get_offsets()},
            "pipetteId": pipette.get_id()
        }
        return FlexCommands._create_base_command(FlexCommandType.MOVE_TO_WELL, params, FlexIntents.SETUP)

    @staticmethod
    def move_to_coordiantes(pipette: FlexPipette, x: float, y: float, z: float, min_z_height: float, force_direct: bool):
        """Creates a command body moving to x, y, z coordiantes"""
        params = {"coordinates": {"x": x, "y": y, "z": z},
                  "minimumZHeight": min_z_height,
                  "forceDirect": force_direct,
                  "pipetteId": pipette.get_id()
                  }
        return FlexCommands._create_base_command(FlexCommandType.MOVE_TO_WELL, params, FlexIntents.SETUP)

    @staticmethod
    def move_relative(pipette: FlexPipette, distance: float, axis: FlexAxis):
        """Creates a command body moving pipette relative to  current position."""
        params = {"axis": axis,
                  "distance": distance,
                  "pipetteId": pipette.get_id()
                  }
        return FlexCommands._create_base_command(FlexCommandType.MOVE_TO_WELL, params, FlexIntents.SETUP)

    @staticmethod
    def send_command(command_url: str, command_dict: dict):
        """Send the command to the server and return the command id."""
        # Convert command_dict to JSON payload
        command_payload = json.dumps(command_dict)
        headers = {"Content-Type": "application/json"}
        headers.update(HEADERS)
        # Send POST request
        try:
            response = requests.request(
                method="POST",
                url=command_url,
                headers=headers,
                params={"waitUntilComplete": True},
                data=command_payload
            )
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Extract 'id' from response JSON
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
            return None
