import serial.tools.list_ports
import re


def get_usb_devices():
    """
    Returns a dictionary of {serial_number: port_name} for devices connected via USB.
    This is Windows-compatible and uses pyserial to list devices.
    """
    # Dictionary to store serial number and corresponding COM port
    dev_dict = {}

    # Get a list of all connected devices
    ports = serial.tools.list_ports.comports()

    for port in ports:
        # Each port provides a description and hardware info
        description = port.description
        hwid = port.hwid

        # Use a regex to extract the serial number from the hardware ID (if available)
        match = re.search(r"SER=(\w+)", hwid)
        if match:
            serial_number = match.group(1)
            # Store the serial number and the device port (e.g., "COM3")
            dev_dict[serial_number] = port.device

    return dev_dict


# Usage example
if __name__ == "__main__":
    # Specify the serial number of your device
    my_serial_no = "FLX00000000000000"  # Replace with your actual serial number

    # Get connected USB devices
    my_devices = get_usb_devices()
    print("Connected devices:", my_devices)

    # Get the COM port for your specified serial number
    device_port = my_devices.get(my_serial_no, None)

    if device_port is None:
        raise ValueError(f"Device with serial number {my_serial_no} not found.")
    else:
        print(f"Device port: {device_port}")
