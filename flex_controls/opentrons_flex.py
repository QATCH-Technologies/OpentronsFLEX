from flex_pipette import FlexPipette
from flex_constants import FlexMountPositions, FlexPipettes, FlexDeckLocations, FlexAxis, FlexLights, ROBOT_IP, HEADERS
from flex_commands import FlexCommands
from flex_runs import FlexRuns
from flex_labware import FlexLabware
import requests
import json
import os
# from scapy.all import ARP, Ether, srp
import socket


class OpentronsFlex:
    def __init__(self, mac_address: str, ip_address: str = None) -> None:
        self._set_robot_mac_address(mac_address)

        self._setup(ip=ip_address)

    def _setup(self, ip: str = None) -> None:
        self.gantry = {FlexMountPositions.LEFT_MOUNT: None,
                       FlexMountPositions.RIGHT_MOUNT: None}
        # if ip is None:
        #     ip = self.find_robot_ip()

        self._set_robot_ip(ip)
        self._set_base_url(f'http://{self._get_robot_ip()}:31950')
        self._set_runs_url(f"{self._get_base_url()}/runs")
        self.create_run()
        self._set_command_url(
            f"{self._get_runs_url()}/{self._get_run_id()}/commands")
        self._set_protocols_url(f"{self._get_base_url()}/protocols")
        self._set_lights_url(f"{self._get_base_url()}/robot/lights")
        self._set_home_url(f"{self._get_base_url()}/robot/home")
        # self.lights_on()
        self.available_labware = {FlexDeckLocations.A1: None,
                                  FlexDeckLocations.A2: None,
                                  FlexDeckLocations.A3: None,
                                  FlexDeckLocations.A4: None,
                                  FlexDeckLocations.B1: None,
                                  FlexDeckLocations.B2: None,
                                  FlexDeckLocations.B3: None,
                                  FlexDeckLocations.B4: None,
                                  FlexDeckLocations.C1: None,
                                  FlexDeckLocations.C2: None,
                                  FlexDeckLocations.C3: None,
                                  FlexDeckLocations.C4: None,
                                  FlexDeckLocations.D1: None,
                                  FlexDeckLocations.D2: None,
                                  FlexDeckLocations.D3: None,
                                  FlexDeckLocations.D4: None, }

    def load_pipette(self, pipette: FlexPipettes, position: FlexMountPositions) -> None:
        new_pipette = FlexPipette(pipette=pipette, mount_position=position)

        if position is FlexMountPositions.LEFT_MOUNT:
            self._set_left_pipette(new_pipette)
            payload = FlexCommands.load_pipette(self._left_pipette)
            response = FlexCommands.send_command(
                command_url=self._get_command_url(), command_dict=payload)
            new_pipette.set_pipette_id(response["data"]["result"]["pipetteId"])

        if position is FlexMountPositions.RIGHT_MOUNT:
            self._set_right_pipette(new_pipette)
            payload = FlexCommands.load_pipette(self._right_pipette)
            response = FlexCommands.send_command(
                command_url=self._get_command_url(), command_dict=payload)
            new_pipette.set_pipette_id(response["data"]["result"]["pipetteId"])

    def load_labware(self, location: FlexDeckLocations, labware_file_path: str):
        labware = FlexLabware(location=location,
                              file_path=labware_file_path)
        if self.available_labware.get(location) is not None:
            raise Exception(
                f'Labware {labware.get_display_name()} not available in slot {labware.get_location().value}.')
        self.available_labware[location] = labware
        payload = FlexCommands.load_labware(
            location=location, load_name=labware.get_display_name(), name_space=labware.get_namespace(), version=labware.get_version())
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        labware.set_id(response["data"]["result"]["labwareId"])

    def pickup_tip(self, labware: FlexLabware, pipette: FlexPipette) -> str:
        self.validate_configuration(labware=labware, pipette=pipette)
        if not labware.is_tiprack():
            raise Exception(
                f"Cannot pickup tip from non-tiprack labware {labware.get_display_name()}")
        payload = FlexCommands.pickup_tip(labware=labware, pipette=pipette)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def aspirate(self, labware: FlexLabware, pipette: FlexPipette, flow_rate: float, volume: float) -> str:
        self.validate_configuration(labware=labware, pipette=pipette)

        payload = FlexCommands.aspirate(
            labware=labware, pipette=pipette, flow_rate=flow_rate, volume=volume)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def dispense(self, labware: FlexLabware, pipette: FlexPipette, flow_rate: float, volume: float) -> str:
        self.validate_configuration(labware=labware, pipette=pipette)

        payload = FlexCommands.dispense(
            labware=labware, pipette=pipette, flow_rate=flow_rate, volume=volume)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def blowout(self, labware: FlexLabware, pipette: FlexPipette, flow_rate: float) -> str:
        self.validate_configuration(labware=labware, pipette=pipette)

        payload = FlexCommands.blowout(
            labware=labware, pipette=pipette, flow_rate=flow_rate)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def drop_tip(self, labware: FlexLabware, pipette: FlexPipette):
        self.validate_configuration(labware=labware, pipette=pipette)

        payload = FlexCommands.drop_tip(labware=labware, pipette=pipette)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def move_to_coordiantes(self, pipette: FlexPipette, x: float, y: float, z: float, min_z_height: float, force_direct: bool):
        self.validate_configuration(labware=None, pipette=pipette)
        payload = FlexCommands.move_to_coordiantes(
            pipette=pipette, x=x, y=y, z=z, min_z_height=min_z_height, force_direct=force_direct)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def move_to_well(self, labware: FlexLabware, pipette: FlexPipette):
        self.validate_configuration(labware=labware, pipette=pipette)
        payload = FlexCommands.move_to_well(labware=labware, pipette=pipette)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def move_relative(self, pipette: FlexPipette, distance: float, axis: FlexAxis):
        self.validate_configuration(pipette=pipette)
        payload = FlexCommands.move_relative(
            pipette=pipette, distance=distance, axis=axis)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload)
        return response

    def run_protocol(self, protocol_id: int) -> str:
        return FlexRuns.run_protocol(
            runs_url=self._get_runs_url(), protocol_id=protocol_id)

    def delete_protocol(self, protocol_id: int) -> str:
        return FlexRuns.delete_protocol(
            runs_url=self._get_runs_url(), protocol_id=protocol_id)

    def upload_protocol(self, protocol_file_path: str) -> str:
        if not os.path.exists(protocol_file_path):
            raise Exception(
                f'Protocol path {protocol_file_path} does not exist')
        return FlexRuns.run_protocol(
            runs_url=self._get_runs_url(), protocol_file_path=protocol_file_path)

    def get_protocol_list(self) -> str:
        return FlexRuns.get_protocols_list(
            runs_url=self._get_runs_url())

    def delete_run(self, run_id: int) -> str:
        return FlexRuns.delete_run(runs_url=self._get_runs_url(), run_id=run_id)

    def get_run_status(self, run_id: int) -> str:
        return FlexRuns.get_run_status(runs_url=self._get_runs_url(), run_id=run_id)

    def get_run_list(self) -> str:
        return FlexRuns.get_runs_list(runs_url=self._get_runs_url())

    def pause_run(self, run_id: int) -> str:
        return FlexRuns.pause_run(runs_url=self._get_runs_url(), run_id=run_id)

    def play_run(self, run_id: int) -> str:
        return FlexRuns.play_run(runs_url=self._get_runs_url(), run_id=run_id)

    def stop_run(self, run_id: int) -> str:
        return FlexRuns.stop_run(runs_url=self._get_runs_url(), run_id=run_id)

    def lights_on(self) -> str:
        self.light_state = FlexLights.ON
        return FlexRuns.set_lights(lights_url=self._get_lights_url(), light_status=FlexLights.ON)

    def lights_off(self) -> str:
        self.light_state = FlexLights.OFF
        return FlexRuns.set_lights(lights_url=self._get_lights_url(), light_status=FlexLights.OFF)

    def lights_status(self) -> str:
        return FlexRuns.get_lights(self._get_lights_url())

    def create_run(self) -> str:
        response = FlexRuns.create_run(self._get_runs_url())
        run_id = response["data"]["id"]
        self._set_run_id(run_id)
        return run_id

    def home(self) -> str:
        return FlexRuns.home(self._get_home_url())

    def validate_configuration(self, labware: FlexLabware = None, pipette: FlexPipette = None) -> None:

        if labware is None or self.available_labware.get(labware.get_location()) is None:
            raise Exception(
                f'Labware {labware.get_display_name()} not available in slot {labware.get_location().value}.')

        if pipette is None or self.gantry.get(pipette.get_mount_position()).get_id() != pipette.get_id():
            raise Exception(
                f'Pipette {pipette.get_pipette()} not mounted.')

    # def find_robot_ip(self):
    #     target_mac_address = self._get_robot_mac_address()
    #     hostname = socket.gethostname()
    #     local_ip = socket.gethostbyname(hostname)
    #     ip_range = '.'.join(local_ip.split('.')[:3]) + ".0/24"

    #     arp_request = ARP(pdst=ip_range)
    #     broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    #     packet = broadcast / arp_request

    #     # Send the packet and get responses
    #     result = srp(packet, timeout=3, verbose=0)[0]

    #     # Iterate over responses
    #     for sent, received in result:
    #         if received.hwsrc.lower() == target_mac_address.lower():
    #             print(
    #                 f"Device found! IP: {received.psrc}, MAC: {received.hwsrc}")
    #             self._set_robot_ip(received.psrc)
    #             return received.psrc

    #     print("Device not found on the network.")
    #     return None

    # --- ACCESSOR METHODS --- #
    def _set_runs_url(self, runs_url: str) -> None:
        self._runs_url = runs_url

    def _set_base_url(self, base_url: str) -> None:
        self._base_url = base_url

    def _set_home_url(self, home_url: str) -> None:
        self._home_url = home_url

    def _set_command_url(self, command_url: str) -> None:
        self._comand_url = command_url

    def _set_protocols_url(self, protocols_url: str) -> None:
        self._protocols_url = protocols_url

    def _set_lights_url(self, lights_url: str) -> None:
        self._lights_url = lights_url

    def _set_run_id(self, run_id: str) -> None:
        self._run_id = run_id

    def _set_robot_ip(self, ip: str) -> None:
        self._robot_ip = ip

    def _set_robot_mac_address(self, mac_address: str) -> None:
        self._robot_mac_address = mac_address

    def _set_left_pipette(self, pipette: FlexPipette) -> None:
        current_pipette = self.gantry.get(FlexMountPositions.LEFT_MOUNT)
        if current_pipette is None:
            self.gantry[FlexMountPositions.LEFT_MOUNT] = pipette
            self._left_pipette = pipette
        else:
            raise Exception(
                f"Gantry mount position {FlexMountPositions.LEFT_MOUNT.value} is occupied by {current_pipette.get_pipette()}.")

    def _set_right_pipette(self, pipette: FlexPipette) -> None:
        current_pipette = self.gantry.get(FlexMountPositions.RIGHT_MOUNT)
        if current_pipette is None:
            self.gantry[FlexMountPositions.RIGHT_MOUNT] = pipette
            self._right_pipette = pipette
        else:
            raise Exception(
                f"Gantry mount position {FlexMountPositions.RIGHT_MOUNT.value} is occupied by {current_pipette.get_pipette()}.")

    # --- MUTATOR METHODS --- #

    def _get_robot_ip(self) -> str:
        return self._robot_ip

    def _get_robot_mac_address(self) -> str:
        return self._robot_mac_address

    def _get_runs_url(self) -> str:
        return self._runs_url

    def _get_home_url(self) -> str:
        return self._home_url

    def _get_base_url(self) -> str:
        return self._base_url

    def _get_command_url(self) -> str:
        return self._comand_url

    def _get_protocols_url(self) -> str:
        return self._protocols_url

    def _get_lights_url(self) -> str:
        return self._lights_url

    def _get_run_id(self) -> str:
        return self._run_id

    def _get_left_pipette(self) -> FlexPipette:
        return self.gantry.get(FlexMountPositions.LEFT_MOUNT)

    def _get_right_pipette(self) -> FlexPipette:
        return self.gantry.get(FlexMountPositions.RIGHT_MOUNT)

    def _get_available_labware(self) -> dict:
        return self.available_labware


if __name__ == "__main__":
    robot = OpentronsFlex(mac_address="34:6F:24:31:17:EF",
                          ip_address="127.0.0.1")
    robot.load_labware(location=FlexDeckLocations.A1,
                       labware_file_path=r'labware\nanovis_q_4x6.json')
    robot.load_labware(location=FlexDeckLocations.A2,
                       labware_file_path=r'labware\nanovis_q_4x6.json')
    robot.load_pipette(FlexPipettes.P50_MULTI_FLEX,
                       FlexMountPositions.LEFT_MOUNT)
    input(robot.gantry.get(FlexMountPositions.LEFT_MOUNT))
    robot.aspirate(robot.available_labware.get(
        FlexDeckLocations.A1), robot.gantry.get(FlexMountPositions.LEFT_MOUNT), 100, 50)
    print(robot._get_available_labware().get(
        FlexDeckLocations.A1).get_display_name())
    print(robot._get_left_pipette().get_id())
