import json
import requests
from flex_constants import FlexActions, FlexLights, HEADERS


class FlexRuns:
    @staticmethod
    def _send_request(method: str, url: str, payload: dict = None):
        """
        Generic method to send HTTP requests and handle responses.

        :param method: HTTP method ('POST', 'DELETE', etc.).
        :param url: Target URL for the request.
        :param payload: Dictionary payload to be sent as JSON.
        :return: Parsed JSON response or None in case of errors.
        """
        headers = {"Content-Type": "application/json"}
        headers.update(HEADERS)
        try:
            # Prepare the payload if provided
            if payload:
                json_payload = json.dumps(payload) if payload else None
                print(f"{method}\n{url},\n{HEADERS},\n{json_payload}\n")
                response = requests.post(url=url, headers=HEADERS, data=json_payload)

            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=HEADERS,
                )
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending {method} request to {url}: {e}")
            return None

    @staticmethod
    def create_run(runs_url: str):
        return FlexRuns._send_request("POST", runs_url, payload=None)

    @staticmethod
    def run_protocol(runs_url: str, protocol_id: int):
        """Send the command to the server and return the command id."""
        payload = {"data": {"protocolId": protocol_id}}
        response_json = FlexRuns._send_request("POST", runs_url, payload)

        if response_json:
            run_id = [key for key in response_json["data"].keys() if "id" in key]
            if run_id:
                return run_id
            else:
                print(f"Error: 'id' not found in response: {response_json}")
        return None

    @staticmethod
    def delete_protocol(protocols_url: str, protocol_id: int):
        """Send the command to delete a protocol by id."""
        delete_protocol_url = f"{protocols_url}/{protocol_id}"
        return FlexRuns._send_request("DELETE", delete_protocol_url)

    @staticmethod
    def upload_protocol(protocols_url: str, protocol_file_path: str):
        protocol_file_payload = open(protocol_file_path, "rb")
        data = {"files": protocol_file_payload}
        response = FlexRuns._send_request("POST", protocols_url, data)
        protocol_file_payload.close()
        return response["data"]["id"]

    @staticmethod
    def upload_protocol_cusom_labware(
        protocols_url: str, protocol_file_path: str, labware_file_path: str
    ):
        protocol_file_payload = open(protocol_file_path, "rb")
        labware_file_payload = open(labware_file_path, "rb")
        data = [("files", protocol_file_payload), ("files", labware_file_payload)]
        response = FlexRuns._send_request("POST", protocols_url, data)
        protocol_file_payload.close()
        labware_file_payload.close()
        return response["data"]["id"]

    @staticmethod
    def delete_run(runs_url: str, run_id: int):
        """Send the command to delete a run by id."""
        delete_run_url = f"{runs_url}/{run_id}"
        return FlexRuns._send_request("DELETE", delete_run_url)

    @staticmethod
    def get_protocols_list(protocols_url: str):
        response = FlexRuns._send_request("GET", protocols_url)
        return [protocol for protocol in response["data"]]

    @staticmethod
    def get_run_status(runs_url: str, run_id: int):
        status_url = f"{runs_url}/{run_id}"
        return FlexRuns._send_request("GET", status_url)

    @staticmethod
    def get_runs_list(runs_url: str):
        response = FlexRuns._send_request("GET", runs_url)
        return [run for run in response["data"]]

    @staticmethod
    def pause_run(runs_url: str, run_id: int):
        actions_url = f"{runs_url}/{run_id}/actions"
        action_payload = json.dumps({"data": {"actionType": FlexActions.PAUSE}})
        return FlexRuns._send_request("POST", actions_url, action_payload)

    @staticmethod
    def play_run(runs_url: str, run_id: int):
        actions_url = f"{runs_url}/{run_id}/actions"
        action_payload = json.dumps({"data": {"actionType": FlexActions.PLAY}})
        return FlexRuns._send_request("POST", actions_url, action_payload)

    @staticmethod
    def stop_run(runs_url: str, run_id: int):
        actions_url = f"{runs_url}/{run_id}/actions"
        action_payload = json.dumps({"data": {"actionType": FlexActions.STOP}})
        return FlexRuns._send_request("POST", actions_url, action_payload)

    @staticmethod
    def set_lights(lights_url: str, light_status: FlexLights):
        return FlexRuns._send_request("POST", lights_url, light_status)

    @staticmethod
    def get_lights(lights_url: str):
        return FlexRuns._send_request("GET", lights_url)

    @staticmethod
    def home(home_url: str):
        command_dict = {"target": "robot"}
        command_payload = json.dumps(command_dict)
        return FlexRuns._send_request("POST", url=home_url, payload=command_payload)
