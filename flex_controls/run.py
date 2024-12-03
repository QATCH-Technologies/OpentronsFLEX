from opentrons_flex import OpentronsFlex

if __name__ == "__main__":
    robot = OpentronsFlex(mac_address="34:6F:24:31:17:EF",
                          ip_address="172.28.24.236")
    robot.upload_protocol_custom_labware(
        r"C:\Users\QATCH\dev\OpentronsFLEX\its_alive_dev.py", r"C:\Users\QATCH\dev\OpentronsFLEX\labware\nanovis_q_4x6.json")
