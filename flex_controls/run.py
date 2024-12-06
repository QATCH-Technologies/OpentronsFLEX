from opentrons_flex import OpentronsFlex
from registration import DeviceRegistration
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

if __name__ == "__main__":
    device = DeviceRegistration()
    logging.info(f"Beginning run with device {device.get_device_name()}")
    robot = OpentronsFlex(mac_address=device.get_mac_address())
    # run_id = robot.upload_protocol_custom_labware(
    #     r"C:\Users\QATCH\dev\OpentronsFLEX\its_alive_dev.py",
    #     r"C:\Users\QATCH\dev\OpentronsFLEX\labware\nanovis_q_4x6.json",
    # )
    robot.run_protocol(protocol_name="Home Protocol")
    # robot.play_run()
