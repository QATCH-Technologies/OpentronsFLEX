import os
import re
import subprocess
import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import time


class IPScanner:
    def __init__(self, mac_address, iprange=range(200, 240), subnet_range=(20, 30), port=31950):
        self.mac_address = mac_address
        self.iprange = iprange
        self.subnet_range = subnet_range
        self.port = port
        self.system_ip = self.get_system_ip()

    def get_system_ip(self):
        """Get the system's base IP address."""
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        ip_parts = ip.split(".")  # Split the IP into parts
        ip_parts = ip_parts[:-2]  # Remove the last two parts
        base_ip = ".".join(ip_parts)
        return base_ip

    def is_port_open(self, ip, port):
        """Check if a port is open on a given IP address using socket."""
        try:
            with socket.create_connection((ip, port), timeout=0.5):  # Reduced timeout
                return True
        except (socket.timeout, socket.error):
            return False

    async def ping_ip(self, computer):
        """Ping the IP to check connectivity asynchronously."""
        process = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', computer,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        return process.returncode == 0

    async def discover_device(self, ip_0, ip):
        """Discover a device by checking port and ping response asynchronously."""
        computer = f"{self.system_ip}.{ip_0}.{ip}"
        # First, check if the port is open
        port_open = await asyncio.to_thread(self.is_port_open, computer, self.port)
        if port_open:
            # If port is open, then ping the device
            ping_success = await self.ping_ip(computer)
            if ping_success:
                print(
                    f"Pinged {computer} successfully, and port {self.port} is open.")
            else:
                print(f"Ping to {computer} failed.")
        else:
            print(f"Port {self.port} is closed on {computer}.")

    async def scan_network(self):
        """Scan the network with asyncio for high concurrency."""
        ip = self.get_ip_from_mac()
        if ip:
            print(
                f"MAC address {self.mac_address} is already in the ARP table with IP {ip}")
            return  # Skip scanning if the MAC address is already in the ARP table

        print("MAC address not found in ARP table, proceeding with network scan.")

        # Create a list of tasks for Phase 1 (check open port)
        tasks = []
        open_ips = []
        for ip_0 in range(self.subnet_range[0], self.subnet_range[1]):
            for ip in self.iprange:
                computer = f"{self.system_ip}.{ip_0}.{ip}"
                tasks.append(self.check_and_record_ip(ip_0, ip, open_ips))

        # First Phase: Check which IPs have the port open
        await asyncio.gather(*tasks)
        print(open_ips)

        # Second Phase: Ping only the IPs that have the port open
        ping_tasks = [self.ping_ip(ip) for ip in open_ips]
        await asyncio.gather(*ping_tasks)

    async def check_and_record_ip(self, ip_0, ip, open_ips):
        """Check if the port is open and record the IP if it's open."""
        computer = f"{self.system_ip}.{ip_0}.{ip}"
        port_open = await asyncio.to_thread(self.is_port_open, computer, self.port)
        if port_open:
            open_ips.append(computer)

    def get_ip_from_mac(self):
        """Get the IP address for the given MAC address from the ARP table."""
        arp_output = subprocess.check_output("arp -a", shell=True).decode()
        match = re.search(
            rf"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+.*\s+{self.mac_address}", arp_output)
        if match:
            return match.group(1)
        return None


if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    mac = "34-6f-24-31-17-ef"
    scanner = IPScanner(mac_address=mac)
    print(f"System IP Address: {scanner.system_ip}")

    # Perform the network scan asynchronously
    asyncio.run(scanner.scan_network())

    ip = scanner.get_ip_from_mac()
    if ip:
        print(f"{mac} has an IP of {ip}")
    else:
        print(f"MAC address {mac} not found in ARP table")

    # End the timer and calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print(f"Execution time: {elapsed_time:.4f} seconds")
