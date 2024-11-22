import serial
import serial.tools.list_ports


# Windows-compatible port name (adjust as necessary)
DEVICE_NAME = "COM5"  # Replace with the actual port name on your system

# These values should be in the device documentation
BAUDRATE = 9600
BYTESIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE

# Optional timeouts in seconds
READ_TIMEOUT = 0.5
WRITE_TIMEOUT = 0.5


class SerialDriver:
    def __init__(self, device_name=None):
        # Allow specifying the device name or fall back to a default
        self.device_name = device_name or DEVICE_NAME

        # Verify if the specified device exists
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if self.device_name not in available_ports:
            raise ValueError(
                f"Device {self.device_name} not found. Available ports: {available_ports}"
            )

        # Create the serial connection
        self.serial_object = serial.Serial(
            port=self.device_name,
            baudrate=BAUDRATE,
            bytesize=BYTESIZE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=READ_TIMEOUT,
            write_timeout=WRITE_TIMEOUT,
        )

    def _reset_buffers(self):
        """
        Worker function to clear input/output buffers.
        """
        self.serial_object.reset_input_buffer()
        self.serial_object.reset_output_buffer()

    def _read_response(self):
        """
        Worker function to read the response from the serial device.
        """
        output_lines = self.serial_object.readlines()
        output_string = ""

        for line in output_lines:
            output_string += line.decode("utf-8")

        return output_string

    def _send_command(self, my_command):
        """
        Worker function to send a command to the serial device.
        """
        SERIAL_ACK = "\r\n"

        command = my_command + SERIAL_ACK
        self.serial_object.write(command.encode())
        self.serial_object.flush()

    def example_driver_function(self):
        """
        Example driver functionality to send a command and read the response.
        """
        runs_url = f"http://172.28.24.236:31950/runs"
        self._send_command(runs_url)
        info = self._read_response()
        return info


# Example usage
if __name__ == "__main__":
    try:
        # Replace "COM3" with the correct port for your device
        driver = SerialDriver(device_name="COM5")
        print("Connection established.")

        # Example functionality
        response = driver.example_driver_function()
        print(f"Response from device: {response}")

    except ValueError as e:
        print(f"Error: {e}")

    except serial.SerialException as e:
        print(f"Serial error: {e}")
