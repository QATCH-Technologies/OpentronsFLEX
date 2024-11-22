import json
import requests
from flex_constants import FlexCommandType, HEADERS, ROBOT_IP
from flex_pipette import FlexPipette


class FlexCommands:

    @staticmethod
    def _create_base_command(command_type, params):
        """Creates the base structure for the command with common functionality."""
        return {
            "data": {
                "commandType": command_type,
                "params": params,
                "intent": "setup"
            }
        }

    @staticmethod
    def load_labware(location, load_name, name_space, version):
        """Creates a command body for loading labware."""
        params = {
            "location": location,
            "loadName": load_name,
            "namespace": name_space,
            "version": version
        }
        return FlexCommands._create_base_command(FlexCommandType.LOAD_LABWARE, params)

    @staticmethod
    def load_pipette(pipette: FlexPipette):
        """Creates a command body for loading a pipette."""
        params = {
            "pipetteName": pipette._get_pipette(),
            "mount": pipette._get_mount_position(),
        }
        return FlexCommands._create_base_command(FlexCommandType.LOAD_PIPETTE, params)

    @staticmethod
    def send_command(command_url: str, command_dict: dict):
        """Send the command to the server and return the command id."""
        # Convert command_dict to JSON payload
        command_payload = json.dumps(command_dict, indent=4)
        print(f"Command:\n{command_payload}")

        # Send POST request
        try:
            response = requests.post(
                url=command_url,
                headers=HEADERS,
                params={"waitUntilComplete": True},
                data=command_payload
            )
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Extract 'id' from response JSON
            response_json = response.json()
            id = [key for key in response_json["data"]
                  ["result"].keys() if 'Id' in key]
            if id:
                return id
            else:
                print(f"Error: 'id' not found in response: {response_json}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
            return None
