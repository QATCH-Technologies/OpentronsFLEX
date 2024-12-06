import subprocess


def find_ip_by_mac(mac_address):
    # Run the arp command to get the ARP table
    result = subprocess.run(["arp", "-a"], capture_output=True, text=True)

    # Check if there is any output from arp
    if result.returncode != 0:
        print("Error running arp command")
        return None

    # Get the ARP table output
    arp_table = result.stdout

    # Split the output into lines
    lines = arp_table.splitlines()
    entries = []
    # Iterate over each line in the ARP table
    for line in lines:
        # Skip lines that don't contain the MAC address
        if "dynamic" not in line:
            continue

        # Split the line into parts, removing extra spaces
        parts = line.split()
        entries.append(parts)

    for entry in entries:
        input(entry)
        if str(entry[1]).lower() == mac_address.lower():
            return entry[0]


# Example usage: Replace with the desired MAC address
mac_address = "00-14-2D-6E-70-AD".lower()  # Replace with your MAC address()
ip = find_ip_by_mac(mac_address)

if ip:
    print(f"The IP address associated with MAC {mac_address} is {ip}")
