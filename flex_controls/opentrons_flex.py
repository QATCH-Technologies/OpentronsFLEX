from flex_pipette import FlexPipette
from flex_constants import (
    FlexMountPositions,
    FlexPipettes,
    FlexDeckLocations,
    FlexAxis,
    FlexLights,
    ROBOT_PORT,
)
from flex_commands import FlexCommands
from flex_runs import FlexRuns
from flex_labware import FlexLabware
from standard_labware import StandardLabware
import os
import logging
import re
from typing import Union
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


class OpentronsFlex:
    def __init__(self, mac_address: str, ip_address: str = None) -> None:
        logging.info(
            "Initializing OpentronsFlex with MAC: %s and IP: %s",
            mac_address,
            ip_address,
        )
        self._set_robot_mac_address(mac_address)

        self._setup(ip=ip_address)

    def _setup(self, ip: str = None) -> None:
        logging.info("Setting up the robot with IP: %s", ip)
        self.available_protocols = {}
        self.gantry = {
            FlexMountPositions.LEFT_MOUNT: None,
            FlexMountPositions.RIGHT_MOUNT: None,
        }
        # if ip is None:
        #     ip = self.find_robot_ip()

        self._set_robot_ipv4(ip)
        self._set_base_url(f"http://{self._get_robot_ipv4()}:{ROBOT_PORT}")
        self._set_runs_url(f"{self._get_base_url()}/runs")
        # self.create_run()
        # self._set_command_url(
        #     f"{self._get_runs_url()}/{self._get_run_id()}/commands")
        self._set_protocols_url(f"{self._get_base_url()}/protocols")
        self._set_lights_url(f"{self._get_base_url()}/robot/lights")
        self._set_home_url(f"{self._get_base_url()}/robot/home")
        self.lights_on()
        self.available_labware = {
            FlexDeckLocations.A1: None,
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
            FlexDeckLocations.D4: None,
        }
        logging.debug("Setup complete. Base URL: %s", self._get_base_url())

    def load_pipette(self, pipette: FlexPipettes, position: FlexMountPositions) -> None:
        logging.info(
            "Loading pipette: %s at position: %s", pipette.value, position.value
        )
        new_pipette = FlexPipette(pipette=pipette, mount_position=position)

        if position is FlexMountPositions.LEFT_MOUNT:
            self._set_left_pipette(new_pipette)
            payload = FlexCommands.load_pipette(self._left_pipette)
            response = FlexCommands.send_command(
                command_url=self._get_command_url(), command_dict=payload
            )
            pipette_id = response["data"]["result"]["pipetteId"]
            new_pipette.set_pipette_id(pipette_id)
            logging.debug("Left pipette loaded with ID: %s", pipette_id)

        if position is FlexMountPositions.RIGHT_MOUNT:
            self._set_right_pipette(new_pipette)
            payload = FlexCommands.load_pipette(self._right_pipette)
            response = FlexCommands.send_command(
                command_url=self._get_command_url(), command_dict=payload
            )
            pipette_id = response["data"]["result"]["pipetteId"]
            new_pipette.set_pipette_id(pipette_id)
            logging.debug("Right pipette loaded with ID: %s", pipette_id)

    def load_labware(
        self,
        location: FlexDeckLocations,
        labware_definition: Union[str, StandardLabware],
    ) -> None:
        logging.info(
            "Loading labware at location: %s from definition: %s",
            location.value,
            labware_definition,
        )
        labware = FlexLabware(
            location=location, labware_definition=labware_definition)
        if self.available_labware.get(location) is not None:
            logging.error(
                "Labware already loaded at location: %s", location.value)
            raise Exception(
                f"Labware {labware.get_display_name()} not available in slot {labware.get_location().value}."
            )
        self.available_labware[location] = labware
        payload = FlexCommands.load_labware(
            location=location,
            load_name=labware.get_load_name(),
            name_space=labware.get_name_space(),
            version=labware.get_version(),
        )
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        print(response)
        labware.set_id(response["data"]["result"]["labwareId"])
        logging.debug("Labware loaded with ID: %s", labware.get_id())

    def pickup_tip(self, labware: FlexLabware, pipette: FlexPipette) -> str:
        logging.info(
            "Picking up tip from labware: %s with pipette: %s",
            labware.get_display_name(),
            pipette.get_id(),
        )
        self.validate_configuration(labware=labware, pipette=pipette)
        if not labware.get_is_tiprack():
            logging.error(
                "Attempt to pick up tip from non-tiprack labware: %s",
                labware.get_display_name(),
            )
            raise Exception(
                f"Cannot pickup tip from non-tiprack labware {labware.get_display_name()}"
            )
        payload = FlexCommands.pickup_tip(labware=labware, pipette=pipette)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Tip pickup successful. Response: %s", response)
        return response

    def aspirate(
        self,
        labware: FlexLabware,
        pipette: FlexPipette,
        flow_rate: float,
        volume: float,
    ) -> str:
        logging.info(
            "Aspirating %s µL at flow rate: %s from labware: %s using pipette: %s",
            volume,
            flow_rate,
            labware.get_display_name(),
            pipette.get_id(),
        )
        self.validate_configuration(labware=labware, pipette=pipette)

        payload = FlexCommands.aspirate(
            labware=labware, pipette=pipette, flow_rate=flow_rate, volume=volume
        )
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Aspirate successful. Response: %s", response)
        return response

    def dispense(
        self,
        labware: FlexLabware,
        pipette: FlexPipette,
        flow_rate: float,
        volume: float,
    ) -> str:
        logging.info(
            "Aspirating %s µL at flow rate: %s from labware: %s using pipette: %s",
            volume,
            flow_rate,
            labware.get_display_name(),
            pipette.get_id(),
        )
        self.validate_configuration(labware=labware, pipette=pipette)
        payload = FlexCommands.dispense(
            labware=labware, pipette=pipette, flow_rate=flow_rate, volume=volume
        )
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Dispense successful. Response: %s", response)
        return response

    def blowout(
        self, labware: FlexLabware, pipette: FlexPipette, flow_rate: float
    ) -> str:
        logging.info(
            "Blowing out tips at flow rate: %s from labware: %s using pipette: %s",
            flow_rate,
            labware.get_display_name(),
            pipette.get_id(),
        )
        self.validate_configuration(labware=labware, pipette=pipette)
        payload = FlexCommands.blowout(
            labware=labware, pipette=pipette, flow_rate=flow_rate
        )
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Blowout successful. Response: %s", response)
        return response

    def drop_tip(self, labware: FlexLabware, pipette: FlexPipette):
        logging.info(
            "Dropting tip from pipette %s at location %s",
            pipette.get_id(),
            labware.get_display_name(),
        )
        self.validate_configuration(labware=labware, pipette=pipette)
        payload = FlexCommands.drop_tip(labware=labware, pipette=pipette)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Drop successful. Response: %s", response)
        return response

    def move_to_coordiantes(
        self,
        pipette: FlexPipette,
        x: float,
        y: float,
        z: float,
        min_z_height: float,
        force_direct: bool,
    ):
        logging.info(
            "Moving pipette %s to coordinates (X, Y, Z, Z-Lmit): %f, %f, %f, %f, force-direct=%s",
            pipette.get_id(),
            x,
            y,
            z,
            min_z_height,
            force_direct,
        )
        self.validate_configuration(labware=None, pipette=pipette)
        payload = FlexCommands.move_to_coordiantes(
            pipette=pipette,
            x=x,
            y=y,
            z=z,
            min_z_height=min_z_height,
            force_direct=force_direct,
        )
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Move to coordinates successful. Response: %s", response)
        return response

    def move_to_well(self, labware: FlexLabware, pipette: FlexPipette):
        logging.info(
            "Moving pipette %s to labware %s at well location %s",
            pipette.get_id(),
            labware.get_display_name(),
            labware.get_location().value,
        )
        self.validate_configuration(labware=labware, pipette=pipette)
        payload = FlexCommands.move_to_well(labware=labware, pipette=pipette)
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Move to well successful. Response: %s", response)
        return response

    def move_relative(self, pipette: FlexPipette, distance: float, axis: FlexAxis):
        logging.info(
            "Relative move of pipette %s %fmm along %s axis",
            pipette.get_id(),
            distance,
            axis.value,
        )
        self.validate_configuration(pipette=pipette)
        payload = FlexCommands.move_relative(
            pipette=pipette, distance=distance, axis=axis
        )
        response = FlexCommands.send_command(
            command_url=self._get_command_url(), command_dict=payload
        )
        logging.debug("Relative move successful. Response: %s", response)
        return response

    def run_protocol(self, protocol_name: str) -> str:
        protocol_id = self.available_protocols.get(protocol_name)
        if protocol_id is None:
            raise ValueError(f"Protocol '{protocol_name}' not available.")
        logging.info(
            f"Running '{protocol_name}' protocol with ID: {protocol_id}")
        try:
            response = FlexRuns.run_protocol(
                runs_url=self._get_runs_url(), protocol_id=protocol_id
            )
            logging.info(
                f"Protocol {protocol_id} run successfully. Response: {response}"
            )
            return response
        except Exception as e:
            logging.error(
                f"Failed to run protocol with ID {protocol_id}: {e}", exc_info=True
            )
            raise

    def delete_protocol(self, protocol_name: str) -> str:
        protocol_id = self.available_protocols.get(protocol_name)
        if protocol_id is None:
            raise ValueError(f"Protocol '{protocol_name}' not available.")
        logging.info(
            f"Deleting '{protocol_name}' protocol with ID: {protocol_id}")
        try:
            response = FlexRuns.delete_protocol(
                runs_url=self._get_runs_url(), protocol_id=protocol_id
            )
            logging.info(
                f"Protocol {protocol_id} deleted successfully. Response: {response}"
            )
            return response
        except Exception as e:
            logging.error(
                f"Failed to delete protocol with ID {protocol_id}: {e}", exc_info=True
            )
            raise

    def upload_protocol(self, protocol_file_path: str) -> str:
        logging.info(f"Uploading protocol from file: {protocol_file_path}")
        if not os.path.exists(protocol_file_path):
            logging.error(
                f"Protocol file path does not exist: {protocol_file_path}")
            raise Exception(
                f"Protocol path {protocol_file_path} does not exist")

        try:
            response = FlexRuns.upload_protocol(
                protocols_url=self._get_protocols_url(),
                protocol_file_path=protocol_file_path,
            )
            self.available_protocols[response.get(
                "protocol_name")] = response.get("protocol_id")
            logging.info(
                f"Protocol uploaded successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(
                f"Failed to upload protocol from file {protocol_file_path}: {e}",
                exc_info=True,
            )
            raise

    def get_protocol_list(self) -> str:
        logging.info("Fetching protocol list.")
        try:
            response = FlexRuns.get_protocols_list(
                runs_url=self._get_runs_url())
            logging.info(
                f"Retrieved protocol list successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch protocol list: {e}", exc_info=True)
            raise

    def delete_run(self, run_id: int) -> str:
        logging.info(f"Deleting run with ID: {run_id}")
        try:
            response = FlexRuns.delete_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(
                f"Run {run_id} deleted successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(
                f"Failed to delete run with ID {run_id}: {e}", exc_info=True)
            raise

    def get_run_status(self, run_id: int) -> str:
        logging.info(f"Fetching status for run ID: {run_id}")
        try:
            response = FlexRuns.get_run_status(
                runs_url=self._get_runs_url(), run_id=run_id
            )
            logging.info(
                f"Status for run {run_id} retrieved successfully. Response: {response}"
            )
            return response
        except Exception as e:
            logging.error(
                f"Failed to fetch status for run ID {run_id}: {e}", exc_info=True
            )
            raise

    def get_run_list(self) -> str:
        logging.info("Fetching run list.")
        try:
            response = FlexRuns.get_runs_list(runs_url=self._get_runs_url())
            logging.info(
                f"Run list retrieved successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch run list: {e}", exc_info=True)
            raise

    def pause_run(self, run_id: int) -> str:
        logging.info(f"Pausing run with ID: {run_id}")
        try:
            response = FlexRuns.pause_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(
                f"Run {run_id} paused successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(
                f"Failed to pause run with ID {run_id}: {e}", exc_info=True)
            raise

    def play_run(self, run_id: int) -> str:
        logging.info(f"Playing run with ID: {run_id}")
        try:
            response = FlexRuns.play_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(
                f"Run {run_id} started successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(
                f"Failed to play run with ID {run_id}: {e}", exc_info=True)
            raise

    def stop_run(self, run_id: int) -> str:
        logging.info(f"Stopping run with ID: {run_id}")
        try:
            response = FlexRuns.stop_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(
                f"Run {run_id} stopped successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error(
                f"Failed to stop run with ID {run_id}: {e}", exc_info=True)
            raise

    def lights_on(self) -> str:
        logging.info("Turning lights on.")
        try:
            self.light_state = FlexLights.ON
            response = FlexRuns.set_lights(
                lights_url=self._get_lights_url(), light_status=FlexLights.ON.value
            )
            logging.info("Lights turned on successfully.")
            return response
        except Exception as e:
            logging.error("Failed to turn lights on.", exc_info=True)
            raise

    def lights_off(self) -> str:
        logging.info("Turning lights off.")
        try:
            self.light_state = FlexLights.OFF
            response = FlexRuns.set_lights(
                lights_url=self._get_lights_url(), light_status=FlexLights.OFF.value
            )
            logging.info("Lights turned off successfully.")
            return response
        except Exception as e:
            logging.error("Failed to turn lights off.", exc_info=True)
            raise

    def flash_lights(self, number_of_times: int) -> str:
        logging.info(f"Flashing lights {number_of_times} times.")
        try:
            for i in range(number_of_times):
                self.lights_on()
                time.sleep(0.5)
                self.lights_off()
                time.sleep(0.5)
        except Exception as e:
            logging.error("Failed flashing lights", exc_info=True)
            raise

    def lights_status(self) -> str:
        logging.info("Fetching lights status.")
        try:
            response = FlexRuns.get_lights(self._get_lights_url())
            logging.info(
                f"Lights status retrieved successfully. Response: {response}")
            return response
        except Exception as e:
            logging.error("Failed to fetch lights status.", exc_info=True)
            raise

    def create_run(self) -> str:
        logging.info("Creating a new run.")
        try:
            response = FlexRuns.create_run(self._get_runs_url())
            run_id = response["data"]["id"]
            self._set_run_id(run_id)
            logging.info(f"New run created successfully with ID: {run_id}")
            return run_id
        except Exception as e:
            logging.error("Failed to create a new run.", exc_info=True)
            raise

    def home(self) -> str:
        logging.info("Sending home command.")
        try:
            response = FlexRuns.home(self._get_home_url())
            logging.info("Home command executed successfully.")
            return response
        except Exception as e:
            logging.error("Failed to execute home command.", exc_info=True)
            raise

    def validate_configuration(
        self, labware: FlexLabware = None, pipette: FlexPipette = None
    ) -> None:
        logging.info("Validating configuration for labware and pipette.")

        try:
            if (
                labware is None
                or self.available_labware.get(labware.get_location()) is None
            ):
                error_message = (
                    f"Labware {labware.get_display_name()} not available in slot "
                    f"{labware.get_location().value}."
                )
                logging.error(error_message)
                raise Exception(error_message)

            if (
                pipette is None
                or self.gantry.get(pipette.get_mount_position()).get_id()
                != pipette.get_id()
            ):
                error_message = f"Pipette {pipette.get_pipette()} not mounted."
                logging.error(error_message)
                raise Exception(error_message)

            logging.info("Configuration validated successfully.")

        except Exception as e:
            logging.error("Validation failed.", exc_info=True)
            raise

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

    def _set_robot_ipv4(self, ipv4: str) -> None:
        ipv4_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        if not re.match(ipv4_regex, ipv4):
            logging.error(f"Invalid IPv4 address: {ipv4}", exc_info=True)
            raise ValueError(f"Invalid IPv4 address: {ipv4}")

        self._robot_ipv4 = ipv4

    def _set_robot_mac_address(self, mac_address: str) -> None:
        mac_regex = (
            "^([0-9A-Fa-f]{2}[:-])"
            + "{5}([0-9A-Fa-f]{2})|"
            + "([0-9a-fA-F]{4}\\."
            + "[0-9a-fA-F]{4}\\."
            + "[0-9a-fA-F]{4})$"
        )
        if not re.match(mac_regex, mac_address):
            logging.error(f"Invalid MAC address: {mac_address}", exc_info=True)
            raise ValueError(f"Invalid MAC address: {mac_address}")

        self._robot_mac_address = mac_address

    def _set_left_pipette(self, pipette: FlexPipette) -> None:
        current_pipette = self.gantry.get(FlexMountPositions.LEFT_MOUNT)
        if current_pipette is None:
            self.gantry[FlexMountPositions.LEFT_MOUNT] = pipette
            self._left_pipette = pipette
        else:
            raise Exception(
                f"Gantry mount position {FlexMountPositions.LEFT_MOUNT.value} is occupied by {current_pipette.get_pipette()}."
            )

    def _set_right_pipette(self, pipette: FlexPipette) -> None:
        current_pipette = self.gantry.get(FlexMountPositions.RIGHT_MOUNT)
        if current_pipette is None:
            self.gantry[FlexMountPositions.RIGHT_MOUNT] = pipette
            self._right_pipette = pipette
        else:
            raise Exception(
                f"Gantry mount position {FlexMountPositions.RIGHT_MOUNT.value} is occupied by {current_pipette.get_pipette()}."
            )

    # --- MUTATOR METHODS --- #

    def _get_robot_ipv4(self) -> str:
        return self._robot_ipv4

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
