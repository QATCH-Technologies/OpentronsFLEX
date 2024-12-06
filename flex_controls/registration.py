import json
import re
import os
import logging
from flex_constants import CONFIG_FILE
from typing import Union
# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


class DeviceRegistration:
    """
    A class responsible for managing device registration, including loading and saving 
    device configuration, validating MAC addresses, and registering a new device.

    Attributes:
        device (dict): A dictionary holding the device information (name and MAC address).
    """

    def __init__(self) -> None:
        """
        Initializes the DeviceRegistration class and attempts to load an existing device configuration.
        If no configuration exists, prompts the user to register a device.
        """
        self.device = {}
        self.load_device()

    def load_device(self) -> Union[dict, None]:
        """
        Loads the device configuration from a file if it exists. If no configuration is found,
        it prompts the user to register a new device.

        If the device configuration file exists, it is loaded into the device attribute.
        If not, the user is prompted to enter device details.
        """
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.device = json.load(file)
                return self.device
        else:
            logging.info("No device configuration found!")
            self.register_device()

    def save_device(self) -> None:
        """
        Saves the current device configuration to a file.

        The device information (name and MAC address) is saved in a JSON format to the
        configuration file defined by CONFIG_FILE.
        """
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.device, file, indent=4)

    @staticmethod
    def is_valid_mac(mac: str) -> bool:
        """
        Validates the format of a given MAC address.

        Args:
            mac (str): The MAC address to validate.

        Returns:
            bool: True if the MAC address is valid, False otherwise.
        """
        pattern = re.compile(r"^([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}$")
        return bool(pattern.match(mac))

    def register_device(self) -> None:
        """
        Prompts the user for device name and MAC address, validates the MAC address, 
        and saves the device information.

        The user is repeatedly prompted to enter the MAC address until a valid format is provided.
        Once valid, the device name and MAC address are saved in the device dictionary and the 
        configuration is stored in a file.
        """
        device_name = input("Enter the device name: ").strip()
        while True:
            mac_address = input(
                "Enter the MAC address (format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX): ").strip()
            if self.is_valid_mac(mac_address):
                break
            logging.error("Invalid MAC address format.")

        self.device = {"name": device_name, "mac": mac_address}
        self.save_device()

    def get_mac_address(self) -> str:
        """
        Retrieves the MAC address of the registered device.

        Returns:
            str: The MAC address of the registered device, or None if not registered.
        """
        return self.device.get("mac")

    def get_device_name(self) -> str:
        """
        Retrieves the name of the registered device.

        Returns:
            str: The name of the registered device, or None if not registered.
        """
        return self.device.get("name")
