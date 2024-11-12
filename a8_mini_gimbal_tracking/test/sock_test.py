import socket 
import struct
center = "55 66 01 01 00 00 00 08 01 d1 12"
versionFirmware = "55 66 01 00 00 00 00 01 64 c4"
gimbalInfo = "55 66 01 00 00 00 00 0a 0f 75"
test = "55 66 01 02 00 10 00 0f 04 05 6b 15"
ip_address = '192.168.6.121'
zoom = "55 66 01 01 00 00 00 06 01 de 31"
zoom_out="55 66 01 01 00 00 00 05 FF 5c 6a"
Auto_Focu ="55 66 01 01 00 00 00 04 01 bc 57"
Manual_Zoom  ="55 66 01 01 00 00 00 06 ff 0f 3f"
Zoom ="55 66 01 01 00 00 00 05 01 8d 64"
port = 37260
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # For TCP, use SOCK_DGRAM for UDP
sock.connect((ip_address, port))

packets =bytes.fromhex(center)
sock.sendall(packets)

data = sock.recv(1024)  # Read data from socket


print(data)

def decode_firmware_response(data):
    try:
        # Example unpacking based on an assumed structure
        # '2s' for the header, 'B' for unsigned byte, and 'H' for short integers
        header, major, minor, patch = struct.unpack('>2sBBB', data[:5])
        
        print(f"Header: {header}")
        print(f"Firmware Version: {major}.{minor}.{patch}")
        
        # Remaining data (if any) can be further decoded as required by protocol
        additional_data = data[5:]
        print(f"Additional Data: {additional_data.hex()}")
        
    except struct.error as e:
        print(f"Error unpacking data: {e}")

#decode_firmware_response(data)