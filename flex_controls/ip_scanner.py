from scapy.all import ARP, Ether, srp


def scan_network(ip_range):
    """
    Scans the given IP range for devices on the network.
    :param ip_range: The range of IPs to scan (e.g., '192.168.1.1/24').
    :return: List of dictionaries with 'ip' and 'mac' keys.
    """
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and capture the responses
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the responses
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices


if __name__ == "__main__":
    # Define the network range to scan
    # Pull up ipconfig from pc settings
    # Filter by port 31950
    # Check ARP table first for device
    network_range = "172.28.24.0/16"  # Adjust the subnet as needed
    print(f"Scanning network range: {network_range}")

    # Call the scan function
    devices = scan_network(network_range)

    # Print the discovered devices
    if devices:
        print("Discovered devices on the network:")
        for device in devices:
            if device["mac"] == "34:6F:24:31:17:EF":
                print(f"IP: {device['ip']}, MAC: {device['mac']}")
    else:
        print("No devices found.")
