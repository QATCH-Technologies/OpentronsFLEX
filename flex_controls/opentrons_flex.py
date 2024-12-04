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
from datetime import datetime
import subprocess
from ip_scanner import IPScanner
import asyncio


class OpentronsFlex:
    """
    A class representing an Opentrons Flex system for automating laboratory protocols.

    This class provides methods for managing and executing laboratory runs, including
    creating, pausing, stopping, and deleting runs. It also offers functionality to
    validate configurations, control lighting, and manage labware and pipettes.

    Attributes:
        available_protocols (dict): A dictionary of available protocols and their metadata.
        available_labware (dict): A dictionary of available labware for use in the system.
        gantry (dict): A dictionary representing the gantry configuration for pipettes.
        light_state (str): The current state of the system's lights (e.g., 'on' or 'off').

    The OpentronsFlex class interfaces with the FlexRuns and FlexLights systems, allowing
    users to automate lab tasks with precision and flexibility. It supports error handling
    and logging for better traceability of operations.
    """

    def __init__(self, mac_address: str, ip_address: str = None) -> None:
        """
        Initializes the `OpentronsFlex` instance with the given MAC address and optionally an IP address.

        Args:
            mac_address (str): The MAC address of the Opentrons Flex robot.
            ip_address (str, optional): The IP address of the robot. Defaults to None.

        Returns:
            None
        """
        self._set_robot_mac_address(mac_address)

        self._setup(ip=ip_address)

    def _setup(self, ip: str = None) -> None:
        """
        Configures the Opentrons Flex robot with the provided IP address.

        This method initializes various robot properties, sets up network-related configurations,
        and prepares the robot for operation by defining URLs for runs, protocols, lights, and home.
        It also initializes the available protocols, gantry mounts, and labware locations.

        Args:
            ip (str, optional): The IP address to assign to the robot. Defaults to None.

        Returns:
            None
        """
        self.available_protocols = {}
        self.gantry = {
            FlexMountPositions.LEFT_MOUNT: None,
            FlexMountPositions.RIGHT_MOUNT: None,
        }

        if ip is None:
            ip = self.find_ip()

        self._set_robot_ipv4(ip)
        logging.info(
            "Initializing OpentronsFlex with MAC: %s and IP: %s",
            self._get_robot_mac_address(),
            self._get_robot_ipv4(),
        )
        self._set_base_url(f"http://{self._get_robot_ipv4()}:{ROBOT_PORT}")
        self._set_runs_url(f"{self._get_base_url()}/runs")
        self._set_protocols_url(f"{self._get_base_url()}/protocols")
        self.update_available_protocols()
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
        """
        Loads a pipette onto the specified mount position of the Opentrons Flex robot.

        This method initializes a new pipette, associates it with the specified mount position
        (left or right), and sends the appropriate command to the robot to load the pipette.
        Once the pipette is loaded, its unique ID is retrieved and stored.

        Args:
            pipette (FlexPipettes): The type of pipette to be loaded.
            position (FlexMountPositions): The mount position where the pipette will be loaded
                (LEFT_MOUNT or RIGHT_MOUNT).

        Returns:
            None
        """
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
        """
        Loads labware into a specified location on the Opentrons Flex robot.

        This method checks if a labware is already present at the specified location. If not, it 
        loads the labware based on the provided definition and updates the robot's configuration. 
        The unique ID of the loaded labware is then retrieved and assigned.

        Args:
            location (FlexDeckLocations): The location on the deck where the labware will be loaded.
            labware_definition (Union[str, StandardLabware]): The labware definition, either as a 
                string (name) or as a `StandardLabware` object, that describes the labware to be loaded.

        Raises:
            Exception: If labware is already loaded at the specified location, an exception is raised.

        Returns:
            None
        """
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
        """
        Picks up a tip from a specified labware using the given pipette.

        This method validates that the labware is a tip rack before proceeding. It then sends a 
        command to the robot to pick up a tip from the labware with the provided pipette. If the 
        labware is not a tip rack, an exception is raised.

        Args:
            labware (FlexLabware): The labware object representing the tip rack from which a tip 
                will be picked up.
            pipette (FlexPipette): The pipette object that will pick up the tip from the labware.

        Raises:
            Exception: If the labware is not a tip rack, an exception is raised.

        Returns:
            str: The response from the robot after attempting to pick up the tip, typically a 
                success message or status.
        """
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
        """
        Aspirates a specified volume of liquid from labware using the provided pipette and flow rate.

        This method logs the aspirate operation details, validates the configuration, and then sends 
        a command to the robot to aspirate the specified volume from the labware using the pipette. 
        The robot's response is returned after the operation is performed.

        Args:
            labware (FlexLabware): The labware object from which the liquid will be aspirated.
            pipette (FlexPipette): The pipette object that will perform the aspiration.
            flow_rate (float): The flow rate (µL/s) at which the liquid will be aspirated.
            volume (float): The volume (µL) of liquid to aspirate.

        Returns:
            str: The response from the robot after performing the aspiration, typically indicating 
                success or providing additional status information.

        Raises:
            Exception: If the configuration of the labware or pipette is invalid (via `validate_configuration`).
        """
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
        """
        Dispenses a specified volume of liquid into labware using the provided pipette and flow rate.

        This method logs the dispense operation details, validates the configuration, and then sends 
        a command to the robot to dispense the specified volume into the labware using the pipette. 
        The robot's response is returned after the operation is performed.

        Args:
            labware (FlexLabware): The labware object into which the liquid will be dispensed.
            pipette (FlexPipette): The pipette object that will perform the dispensing.
            flow_rate (float): The flow rate (µL/s) at which the liquid will be dispensed.
            volume (float): The volume (µL) of liquid to dispense.

        Returns:
            str: The response from the robot after performing the dispense, typically indicating 
                success or providing additional status information.

        Raises:
            Exception: If the configuration of the labware or pipette is invalid (via `validate_configuration`).
        """
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
        """
        Drops the tip from the specified pipette at the given labware location.

        This method logs the tip drop operation, validates the configuration of the 
        pipette and labware, and sends a command to the robot to drop the pipette tip 
        at the specified labware location. The robot's response is returned after the 
        operation is performed.

        Args:
            labware (FlexLabware): The labware object from which the pipette tip will be dropped.
            pipette (FlexPipette): The pipette object that will drop the tip.

        Returns:
            str: The response from the robot after performing the tip drop, typically indicating 
                success or providing additional status information.

        Raises:
            Exception: If the configuration of the labware or pipette is invalid (via `validate_configuration`).
        """
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
        """
        Moves the specified pipette to the given (X, Y, Z) coordinates with optional Z height limitation.

        This method logs the movement request, validates the configuration of the pipette, 
        and sends a command to the robot to move the pipette to the specified coordinates. 
        The movement is constrained by a minimum Z height and can be forced to proceed 
        directly if specified. The response from the robot after the movement is performed is returned.

        Args:
            pipette (FlexPipette): The pipette object that will be moved.
            x (float): The target X-coordinate for the pipette's movement.
            y (float): The target Y-coordinate for the pipette's movement.
            z (float): The target Z-coordinate for the pipette's movement.
            min_z_height (float): The minimum Z height constraint for the movement.
            force_direct (bool): If True, the movement will be forced directly to the coordinates, 
                                bypassing any additional checks or adjustments.

        Returns:
            str: The response from the robot after the movement, typically indicating 
                success or additional status information.

        Raises:
            Exception: If the configuration of the pipette is invalid (via `validate_configuration`).
        """
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
        """
        Moves the specified pipette to a specific well in the given labware.

        This method logs the movement request, validates the configuration of the labware 
        and pipette, and sends a command to the robot to move the pipette to the specified 
        well within the labware. The response from the robot after the movement is performed is returned.

        Args:
            labware (FlexLabware): The labware object containing the well to which the pipette will be moved.
            pipette (FlexPipette): The pipette object that will be moved to the well.

        Returns:
            str: The response from the robot after the movement, typically indicating success or additional status information.

        Raises:
            Exception: If the configuration of the labware or pipette is invalid (via `validate_configuration`).
        """
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
        """
        Moves the specified pipette a relative distance along a specified axis.

        This method logs the request for the relative movement, validates the pipette's configuration, 
        and sends a command to the robot to move the pipette along the specified axis by the given distance. 
        The response from the robot after the movement is performed is returned.

        Args:
            pipette (FlexPipette): The pipette object that will be moved.
            distance (float): The distance in millimeters the pipette will move along the specified axis.
            axis (FlexAxis): The axis along which the pipette will move (e.g., X, Y, or Z).

        Returns:
            str: The response from the robot after the relative move, typically indicating success or additional status information.

        Raises:
            Exception: If the configuration of the pipette is invalid (via `validate_configuration`).
        """
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
        """
        Runs a protocol by its name.

        This method checks if the specified protocol is available, retrieves its ID, 
        and initiates the protocol run. If successful, the method logs the run's details 
        and returns the response from the run. If an error occurs, it logs the error 
        and raises an exception.

        Args:
            protocol_name (str): The name of the protocol to run.

        Returns:
            str: The response from the run, typically containing details of the protocol execution.

        Raises:
            ValueError: If the protocol is not available.
            Exception: If the protocol run fails during execution.
        """
        protocol = self.available_protocols.get(protocol_name)
        if protocol is None:
            logging.error(f"Protocol '{protocol_name}' not available.")
            raise ValueError(f"Protocol '{protocol_name}' not available.")
        protocol_id = protocol.get("id")
        logging.info(
            f"Setting up '{protocol_name}' protocol for run with ID: {protocol_id}"
        )
        try:
            run_id = FlexRuns.run_protocol(
                runs_url=self._get_runs_url(), protocol_id=protocol_id
            )
            response = self.play_run(run_id)
            logging.info(f"Protocol {protocol_id} running under {run_id}. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to run protocol with ID {protocol_id}: {e}", exc_info=True
            )
            raise

    def delete_protocol(self, protocol_name: str) -> str:
        """
        Deletes a protocol by its name.

        This method looks for the protocol in the available protocols list, and if found,
        it deletes the protocol using its ID by calling the `FlexRuns.delete_protocol` method.
        If the protocol is not found, it raises a `ValueError`. It also logs the success or failure 
        of the deletion process.

        Args:
            protocol_name (str): The name of the protocol to be deleted.

        Returns:
            str: The response from the deletion operation, typically indicating success or failure.

        Raises:
            ValueError: If the protocol with the specified name is not available.
            Exception: If the deletion operation fails.
        """
        protocol = self.available_protocols.get(protocol_name)
        if protocol is None:
            logging.error(f"Protocol '{protocol_name}' not available.")
            raise ValueError(f"Protocol '{protocol_name}' not available.")
        protocol_id = protocol.get("id")
        logging.info(
            f"Deleting '{protocol_name}' protocol with ID: {protocol_id}")
        try:
            response = FlexRuns.delete_protocol(
                protocols_url=self._get_protocols_url(), protocol_id=protocol_id
            )
            self.update_available_protocols()
            logging.info(f"Protocol {protocol_id} deleted successfully. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to delete protocol with ID {protocol_id}: {e}", exc_info=True
            )
            raise

    def upload_protocol(self, protocol_file_path: str) -> str:
        """
        Deletes a protocol by its name.

        This method checks if the specified protocol is available, retrieves its ID, 
        and deletes it. If the deletion is successful, the available protocols are updated 
        and the method returns the response from the deletion. If an error occurs, 
        it logs the error and raises an exception.

        Args:
            protocol_name (str): The name of the protocol to delete.

        Returns:
            str: The response from the deletion, typically containing details of the deletion process.

        Raises:
            ValueError: If the protocol is not available.
            Exception: If the protocol deletion fails during execution.
        """
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
            self.update_available_protocols()
            logging.info("Protocol uploaded successfully.")
            return response
        except Exception as e:
            logging.error(
                f"Failed to upload protocol from file {protocol_file_path}: {e}",
                exc_info=True,
            )
            raise

    def upload_protocol_custom_labware(
        self, protocol_file_path: str, *custom_labware_file_paths: str
    ) -> str:
        """
        Uploads a protocol file with custom labware files.

        This method checks if the provided protocol file and all custom labware files exist. 
        If they exist, the protocol and labware files are uploaded. After the upload, 
        the available protocols are updated. If any file does not exist or if the upload fails, 
        an error is logged and an exception is raised.

        Args:
            protocol_file_path (str): The file path of the protocol to upload.
            custom_labware_file_paths (str): One or more file paths of custom labware to upload.

        Returns:
            str: The response from the upload, typically containing the status of the upload process.

        Raises:
            Exception: If any of the file paths do not exist or if the upload fails.
        """
        logging.info(
            f"Uploading protocol from file: {protocol_file_path} with custom labware from files: {', '.join(custom_labware_file_paths)}"
        )

        # Check if protocol file and all custom labware files exist
        if not os.path.exists(protocol_file_path):
            logging.error(
                f"Protocol file path does not exist: {protocol_file_path}")
            raise Exception(
                f"Protocol file path does not exist: {protocol_file_path}")

        for labware_file_path in custom_labware_file_paths:
            if not os.path.exists(labware_file_path):
                logging.error(
                    f"Custom labware file path does not exist: {labware_file_path}")
                raise Exception(
                    f"Custom labware file path does not exist: {labware_file_path}")

        try:
            response = FlexRuns.upload_protocol_custom_labware(
                protocols_url=self._get_protocols_url(),
                protocol_file_path=protocol_file_path,
                labware_file_paths=list(
                    custom_labware_file_paths),  # Updated parameter
            )
            self.update_available_protocols()
            logging.info("Protocol uploaded with custom labware successfully.")
            return response
        except Exception as e:
            logging.error(
                f"Failed to upload protocol from file {protocol_file_path} with custom labware from files {', '.join(custom_labware_file_paths)}: {e}",
                exc_info=True,
            )
            raise

    def get_protocol_list(self) -> str:
        """
        Retrieves a list of available protocols.

        This method fetches the list of protocols from the specified URL. If the fetch is
        successful, the list is returned. If an error occurs during the process, an error is
        logged and an exception is raised.

        Returns:
            str: The response containing the protocol list, typically in JSON format.

        Raises:
            Exception: If the attempt to fetch the protocol list fails.
        """
        logging.info("Fetching protocol list.")
        try:
            response = FlexRuns.get_protocols_list(
                protocols_url=self._get_protocols_url()
            )
            logging.info(f"Retrieved protocol list successfully")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch protocol list: {e}", exc_info=True)
            raise

    def update_available_protocols(self) -> None:
        """
        Updates the list of available protocols and stores the most recent version of each protocol.

        This method fetches the list of protocols, processes each protocol entry, and updates
        the internal `available_protocols` dictionary. If multiple versions of a protocol exist,
        it stores the most recent version based on the `createdAt` timestamp.

        The `available_protocols` dictionary will be populated with the protocol names as keys,
        and their corresponding protocol IDs and creation timestamps as values.

        Returns:
            dict: A dictionary mapping protocol names to their corresponding protocol IDs.

        Raises:
            Exception: If fetching the protocol list fails or the protocol entries are malformed.
        """
        logging.info("Updating available protocols.")
        self.available_protocols = {}
        all_protocols = self.get_protocol_list()
        for entry in all_protocols:
            protocol_name = entry["metadata"]["protocolName"]
            protocol_id = entry["id"]
            created_at = datetime.fromisoformat(
                entry["createdAt"].replace("Z", "+00:00")
            )

            # Check if protocol already exists in the dictionary
            if protocol_name not in self.available_protocols:
                self.available_protocols[protocol_name] = {
                    "id": protocol_id,
                    "createdAt": created_at,
                }
            else:
                # Compare the dates and store the most recent one
                if created_at > self.available_protocols[protocol_name]["createdAt"]:
                    self.available_protocols[protocol_name] = {
                        "id": protocol_id,
                        "createdAt": created_at,
                    }

        # Extract only protocol names and their corresponding IDs
        result = {name: data["id"]
                  for name, data in self.available_protocols.items()}

        return result

    def delete_run(self, run_id: int) -> str:
        """
        Deletes a specific run based on the provided run ID.

        This method attempts to delete a run using the provided `run_id`. It communicates with 
        the FlexRuns service to delete the run and logs the result. If the deletion is successful,
        it returns the response from the service.

        Args:
            run_id (int): The ID of the run to delete.

        Returns:
            str: The response from the FlexRuns service after attempting to delete the run.

        Raises:
            Exception: If the deletion fails due to a service error or invalid run ID.
        """
        logging.info(f"Deleting run with ID: {run_id}")
        try:
            response = FlexRuns.delete_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(f"Run {run_id} deleted successfully. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to delete run with ID {run_id}: {e}", exc_info=True)
            raise

    def get_run_status(self, run_id: int) -> str:
        """
        Retrieves the status of a specific run based on the provided run ID.

        This method communicates with the FlexRuns service to fetch the current status 
        of a run using the `run_id`. If successful, it logs and returns the response 
        containing the status. If an error occurs, it logs the error and raises an exception.

        Args:
            run_id (int): The ID of the run whose status is to be retrieved.

        Returns:
            str: The status of the run, as returned by the FlexRuns service.

        Raises:
            Exception: If the status retrieval fails due to a service error or invalid run ID.
        """
        logging.info(f"Fetching status for run ID: {run_id}")
        try:
            response = FlexRuns.get_run_status(
                runs_url=self._get_runs_url(), run_id=run_id
            )
            logging.info(f"Status for run {run_id} retrieved successfully. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to fetch status for run ID {run_id}: {e}", exc_info=True
            )
            raise

    def get_run_list(self) -> str:
        """
        Retrieves the list of all runs from the FlexRuns service.

        This method communicates with the FlexRuns service to fetch the list of all 
        available runs. If successful, it logs and returns the response containing 
        the list of runs. If an error occurs, it logs the error and raises an exception.

        Returns:
            str: The list of runs, as returned by the FlexRuns service.

        Raises:
            Exception: If the run list retrieval fails due to a service error.
        """
        logging.info("Fetching run list.")
        try:
            response = FlexRuns.get_runs_list(runs_url=self._get_runs_url())
            logging.info(f"Run list retrieved successfully. ")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch run list: {e}", exc_info=True)
            raise

    def pause_run(self, run_id: int) -> str:
        """
        Pauses a running protocol with the given run ID.

        This method communicates with the FlexRuns service to pause the run with the
        specified `run_id`. If the operation is successful, it logs the success and
        returns the response. If an error occurs, it logs the error and raises an exception.

        Args:
            run_id (int): The ID of the run to pause.

        Returns:
            str: The response from the FlexRuns service indicating the result of the pause operation.

        Raises:
            Exception: If the run pausing operation fails due to a service error.
        """
        logging.info(f"Pausing run with ID: {run_id}")
        try:
            response = FlexRuns.pause_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(f"Run {run_id} paused successfully. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to pause run with ID {run_id}: {e}", exc_info=True)
            raise

    def play_run(self, run_id: int) -> str:
        """
        Starts the execution of a protocol run with the given run ID.

        This method communicates with the FlexRuns service to start the run with the
        specified `run_id`. If the operation is successful, it logs the success and
        returns the response. If an error occurs, it logs the error and raises an exception.

        Args:
            run_id (int): The ID of the run to start.

        Returns:
            str: The response from the FlexRuns service indicating the result of the play operation.

        Raises:
            Exception: If the run playing operation fails due to a service error.
        """
        logging.info(f"Playing run with ID: {run_id}")
        try:
            response = FlexRuns.play_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(f"Run {run_id} started successfully. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to play run with ID {run_id}: {e}", exc_info=True)
            raise

    def stop_run(self, run_id: str) -> str:
        """
        Stops the execution of a protocol run with the given run ID.

        This method communicates with the FlexRuns service to stop the run with the
        specified `run_id`. If the operation is successful, it logs the success and
        returns the response. If an error occurs, it logs the error and raises an exception.

        Args:
            run_id (str): The ID of the run to stop.

        Returns:
            str: The response from the FlexRuns service indicating the result of the stop operation.

        Raises:
            Exception: If the run stopping operation fails due to a service error.
        """
        logging.info(f"Stopping run with ID: {run_id}")
        try:
            response = FlexRuns.stop_run(
                runs_url=self._get_runs_url(), run_id=run_id)
            logging.info(f"Run {run_id} stopped successfully. ")
            return response
        except Exception as e:
            logging.error(
                f"Failed to stop run with ID {run_id}: {e}", exc_info=True)
            raise

    def lights_on(self) -> str:
        """
        Turns the lights on.

        This method sends a command to turn the lights on by interacting with the 
        FlexLights service. If successful, it logs the success and returns the response.
        If an error occurs, it logs the error and raises an exception.

        Returns:
            str: The response from the FlexLights service indicating the result of the light-on operation.

        Raises:
            Exception: If the light turning-on operation fails due to a service error.
        """
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
        """
        Turns the lights off.

        This method sends a command to turn the lights off by interacting with the 
        FlexLights service. If successful, it logs the success and returns the response.
        If an error occurs, it logs the error and raises an exception.

        Returns:
            str: The response from the FlexLights service indicating the result of the light-off operation.

        Raises:
            Exception: If the light turning-off operation fails due to a service error.
        """
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
        """
        Flashes the lights a specified number of times.

        This method flashes the lights by turning them on and off with a 0.5-second 
        delay between each toggle. The lights will flash the number of times 
        specified by the `number_of_times` parameter. If an error occurs, it logs the 
        error and raises an exception.

        Args:
            number_of_times (int): The number of times to flash the lights.

        Returns:
            str: A string indicating the completion of the flash sequence. This method does not return a response directly,
                but logs the actions taken.

        Raises:
            ValueError: If the number of times requested to flash the lights is less than 1.
            Exception: If the flashing sequence fails due to an error in turning the lights on or off.
        """
        if number_of_times < 1:
            logging.error(f'Cannot flash lights {number_of_times}.')
            raise ValueError(f'Cannot flash lights {number_of_times}.')
        logging.info(f"Flashing lights {number_of_times} times.")
        try:
            for _ in range(number_of_times):
                self.lights_on()
                time.sleep(0.5)
                self.lights_off()
                time.sleep(0.5)
        except Exception as e:
            logging.error("Failed flashing lights", exc_info=True)
            raise

    def lights_status(self) -> str:
        """
        Fetches the current status of the lights.

        This method retrieves the current status of the lights from the system.
        If the request fails, it logs the error and raises an exception.

        Returns:
            str: A string representing the current status of the lights.

        Raises:
            Exception: If the request to fetch the lights status fails.
        """
        logging.info("Fetching lights status.")
        try:
            response = FlexRuns.get_lights(self._get_lights_url())
            logging.info(f"Lights status retrieved successfully. ")
            return response
        except Exception as e:
            logging.error("Failed to fetch lights status.", exc_info=True)
            raise

    def create_run(self) -> str:
        """
        Creates a new run from the protocol.

        This method creates a new run based on the specified protocol, logs the process,
        and sets the run ID upon successful creation.

        Returns:
            str: The ID of the newly created run.

        Raises:
            Exception: If the run creation fails.
        """
        logging.info("Creating a new run.")
        try:
            response = FlexRuns.create_run_from_protocol(self._get_runs_url())
            run_id = response["data"]["id"]
            self._set_run_id(run_id)
            logging.info(f"New run created successfully with ID: {run_id}")
            return run_id
        except Exception as e:
            logging.error("Failed to create a new run.", exc_info=True)
            raise

    def home(self) -> str:
        """
        Sends a command to home the system.

        This method sends a "home" command to the system. If the command is
        executed successfully, it logs the success message. If there is an error,
        it logs the failure and raises an exception.

        Returns:
            str: The response from the system after executing the home command.

        Raises:
            Exception: If the command to home the system fails.
        """
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
        """
        Validates the configuration of labware and pipette.

        This method checks if the provided labware is available in the configured
        slot and if the specified pipette is correctly mounted. If either check fails,
        an exception is raised with an appropriate error message.

        Args:
            labware (FlexLabware, optional): The labware to validate. Defaults to None.
            pipette (FlexPipette, optional): The pipette to validate. Defaults to None.

        Raises:
            Exception: If the labware is not available in the specified slot or if
            the pipette is not mounted correctly.
        """
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

    def find_ip(self) -> str:
        scanner = IPScanner(mac_address=self._get_robot_mac_address())

        # Perform the network scan asynchronously
        asyncio.run(scanner.scan_network())
        return scanner.get_ip_from_mac()

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
        # ipv4_regex = r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|[1-9]?[0-9])$"
        # if not re.match(ipv4_regex, ipv4):
        #     logging.error(f"Invalid IPv4 address: {ipv4}", exc_info=True)
        #     raise ValueError(f"Invalid IPv4 address: {ipv4}")

        # Attempt to ping the IP address to check if it is reachable
        try:
            result = subprocess.run(
                # Use `-n 1` for Windows compatibility
                ["ping", "-n", "1", ipv4],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                logging.error(f"Cannot communicate with IP address: {ipv4}")
                raise ConnectionError(
                    f"Cannot communicate with IP address: {ipv4}")
        except Exception as e:
            logging.error(
                f"Error during communication check for IP address {ipv4}: {e}", exc_info=True)
            raise

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
