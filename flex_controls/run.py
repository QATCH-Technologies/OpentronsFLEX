from opentrons_flex import OpentronsFlex

if __name__ == "__main__":
    # ip_address="172.28.24.236"
    robot = OpentronsFlex(mac_address="00-14-2D-6E-70-AD")
    # run_id = robot.upload_protocol_custom_labware(
    #     r"C:\Users\QATCH\dev\OpentronsFLEX\its_alive_dev.py",
    #     r"C:\Users\QATCH\dev\OpentronsFLEX\labware\nanovis_q_4x6.json",
    # )
    robot.run_protocol(protocol_name="Home Protocol")
    # robot.play_run()
