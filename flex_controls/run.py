from opentrons_flex import OpentronsFlex

if __name__ == "__main__":
    # ip_address="172.28.24.236"
    robot = OpentronsFlex(mac_address="34-6f-24-31-17-ef")
    robot.flash_lights(10)
