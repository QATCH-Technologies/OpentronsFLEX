from scapy.all import ARP, Ether, srp
import socket
from concurrent.futures import ThreadPoolExecutor


def get_local_ip():
    """Get local machine's IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Connect to a remote server to get the local IP
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def send_arp_request(ip):
    """Send an ARP request to a single IP address."""
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    # Return the active IP if response received
    return answered_list[0][1].psrc if answered_list else None


def get_active_ips(network):
    """Get active IP addresses on the network using ARP."""
    active_ips = []

    # Create a list of IP addresses in the network
    ip_list = [
        f"{network.split('/')[0].rsplit('.', 1)[0]}.{i}" for i in range(1, 65535)]

    # Use ThreadPoolExecutor to send ARP requests in parallel
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(send_arp_request, ip_list)

    # Filter out None values (inactive IPs)
    active_ips = [ip for ip in results if ip]

    return active_ips


# Get local IP address and the network
local_ip = get_local_ip()
print(f"Local IP Address: {local_ip}")

# Assuming the subnet is a /16 (255.255.0.0)
subnet = '.'.join(local_ip.split('.')[:2]) + '.0.0/16'

# Get active IP addresses on the network
active_ips = get_active_ips(subnet)
print("Active IPs on the local network:")
for ip in active_ips:
    print(ip)
