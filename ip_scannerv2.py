import socket
import struct


def get_broadcast_address(ip, subnet_mask):
    """
    Calculate the broadcast address based on the IP and subnet mask.
    :param ip: The client's IP address as a string.
    :param subnet_mask: The subnet mask as a string.
    :return: The broadcast address as a string.
    """
    ip_bytes = struct.unpack('!I', socket.inet_aton(ip))[0]
    mask_bytes = struct.unpack('!I', socket.inet_aton(subnet_mask))[0]
    broadcast_bytes = ip_bytes | ~mask_bytes
    broadcast_address = socket.inet_ntoa(struct.pack('!I', broadcast_bytes))
    return broadcast_address


def broadcast_mac_address(server_mac, port=12345):
    """
    Broadcasts the server's MAC address to the calculated broadcast address.

    :param server_mac: The server's MAC address to be broadcast.
    :param port: The port number to use for broadcasting (default is 12345).
    """
    # Get the client's IP and subnet mask
    hostname = socket.gethostname()
    client_ip = socket.gethostbyname(hostname)
    # Replace with actual subnet mask if dynamic retrieval is needed
    subnet_mask = '255.255.0.0'

    broadcast_ip = get_broadcast_address(client_ip, subnet_mask)
    print(f"Broadcasting to {broadcast_ip}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        message = f"MAC:{server_mac}"
        client_socket.sendto(message.encode(), (broadcast_ip, port))
        print(f"Broadcasted MAC address: {server_mac}")

        # Wait for the server's response
        client_socket.settimeout(5)  # Timeout for server's response
        while True:
            try:
                data, server = client_socket.recvfrom(1024)
                print(
                    f"Received response from server {server}: {data.decode()}")
                break
            except socket.timeout:
                print("No response received. Retrying...")
                client_socket.sendto(message.encode(), (broadcast_ip, port))
    finally:
        client_socket.close()


if __name__ == "__main__":
    # Replace this with the actual MAC address of the server you want to contact
    server_mac = "00:11:22:33:44:55"
    broadcast_mac_address(server_mac)
