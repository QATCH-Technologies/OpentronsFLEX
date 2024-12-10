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
    # Start running the protocol
    robot.upload_protocol_custom_labware(
        r"C:\Users\QATCH\dev\OpentronsFLEX\src\protocols\4x6_measurement.py",
        r"C:\Users\QATCH\dev\OpentronsFLEX\labware\nanovis_q_4x6.json",
    )
    run_id = robot.run_protocol("4x6_measurement")

    # Ask the user whether to continue or remeasure
    while True:
        user_input = (
            input(
                "Do you want to continue the run or remeasure? (continue/remeasure): "
            )
            .strip()
            .lower()
        )

        if user_input == "c":
            print("Continuing the current run.")
            print(robot.get_run_status(run_id))
            robot.resume_run(run_id=run_id)
        elif user_input == "m":
            print("Re-uploading and rerunning the protocol.")
            # Re-upload and rerun the protocol again
            robot.stop_run(run_id)
            robot.upload_protocol_custom_labware(
                r"C:\Users\QATCH\dev\OpentronsFLEX\src\protocols\4x6_measurement.py",
                r"C:\Users\QATCH\dev\OpentronsFLEX\labware\nanovis_q_4x6.json",
            )
            run_id = robot.run_protocol("4x6_measurement")
        else:
            print(
                "Invalid input. Please type 'continue' to continue the run or 'remeasure' to remeasure."
            )
