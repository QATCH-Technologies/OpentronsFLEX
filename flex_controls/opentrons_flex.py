from flex_pipette import FlexPipette
from flex_constants import FlexMountPositions, FlexPipettes, ROBOT_IP, HEADERS
from flex_commands import FlexCommands
import requests
import json


class OpentronsFlex:
    def __init__(self, ip, headers, left_pipette: FlexPipette, right_pipette: FlexPipette) -> None:
        self._setup()

    def _setup(self) -> None:
        self._set_runs_url(f"http://{ROBOT_IP}:31950/runs")

        r = requests.post(
            url=self._get_runs_url(),
            headers=HEADERS
        )

        r_dict = json.loads(r.text)
        self._set_run_id(r_dict["data"]["id"])
        self._set_command_url(
            f"{self._get_runs_url()}/{self._get_run_id()}/commands")

    def load_pipette(self, pipette: FlexPipettes, position: FlexMountPositions) -> None:
        new_pipette = FlexPipette(pipette=pipette, mount_position=position)

        if position is FlexMountPositions.LEFT_MOUNT:
            self._set_left_pipette(new_pipette)
            payload = FlexCommands.load_pipette(self._left_pipette)
            id = FlexCommands.send_command(
                command_url=self._get_command_url(), command_dict=payload)
            new_pipette.set_pipette_id(id)

        if position is FlexMountPositions.RIGHT_MOUNT:
            self._set_right_pipette(new_pipette)
            payload = FlexCommands.load_pipette(self._right_pipette)
            id = FlexCommands.send_command(
                command_url=self._get_command_url(), command_dict=payload)
            new_pipette.set_pipette_id(id)

    def load_labware(self, labware):
        pass

    def find_robot_ip(self, target_mac):
        pass

    # --- ACCESSOR METHODS --- #
    def _set_runs_url(self, runs_url: str) -> None:
        self._runs_url = runs_url

    def _set_command_url(self, command_url: str) -> None:
        self._comand_url = command_url

    def _set_run_id(self, run_id: str) -> None:
        self._run_id = run_id

    def _set_robot_ip(self, ip: str) -> None:
        self._robot_ip = ip

    def _set_left_pipette(self, pipette: FlexPipette) -> None:
        self._left_pipette = pipette

    def _set_right_pipette(self, pipette: FlexPipette) -> None:
        self._right_pipette = pipette

    # --- MUTATOR METHODS --- #
    def _get_robot_ip(self) -> str:
        return self._robot_ip

    def _get_runs_url(self) -> str:
        return self._runs_url

    def _get_command_url(self) -> str:
        return self._comand_url

    def _get_run_id(self) -> str:
        return self._run_id

    def _get_left_pipette(self) -> FlexPipette:
        return self._left_pipette

    def _get_right_pipette(self) -> FlexPipette:
        return self._right_pipette


if __name__ == "__main__":
    robot = OpentronsFlex(1)
