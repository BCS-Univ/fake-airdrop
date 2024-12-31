import socket
import threading
import os
import time

BROADCAST_PORT = 37020
BUFFER_SIZE = 10240

def broadcast_presence():
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.2)
    message = b"Device available"
    #while True:
    sock.sendto(message, ('<broadcast>', BROADCAST_PORT))
      # print("Broadcasting presence...")
    time.sleep(10)
    

def listen_for_devices():
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    # while True:
    #   data, addr = sock.recvfrom(BUFFER_SIZE)
      #print(f"Detected device: {addr} - {data.decode()}")
"""
def send_file(target_ip, file_path):
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    with open(file_path, 'rb') as f:
      while True:
        chunk = f.read(BUFFER_SIZE)
        if not chunk:
          sock.sendto(b"EOF", (target_ip, BROADCAST_PORT))
          break
        sock.sendto(chunk, (target_ip, BROADCAST_PORT))
      print(f"File {file_path} sent to {target_ip}")

def receive_file(save_path):
  os.makedirs(os.path.dirname(save_path), exist_ok=True)

  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    with open(save_path, 'wb') as f:
      while True:
        chunk, addr = sock.recvfrom(BUFFER_SIZE)
        if chunk == b"EOF":
          print("End of file received")
          break
        f.write(chunk)
        print(f"Received chunk from {addr}: {chunk}")
      print(f"File received and saved to {save_path}")
"""
import hashlib
import struct
import os

def send_file(target_ip, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Send file size first
        file_size = os.path.getsize(file_path)
        sock.sendto(struct.pack("!Q", file_size), (target_ip, BROADCAST_PORT))
        
        # Send file content with sequence numbers
        with open(file_path, 'rb') as f:
            sequence = 0
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    # Send EOF with checksum
                    checksum = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                    sock.sendto(f"EOF:{checksum}".encode(), (target_ip, BROADCAST_PORT))
                    break
                
                # Send sequence number and chunk
                header = struct.pack("!I", sequence)
                sock.sendto(header + chunk, (target_ip, BROADCAST_PORT))
                sequence += 1
                
            print(f"File {file_path} sent to {target_ip}")
            print(f"Original file size: {file_size} bytes")

def receive_file(save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    received_chunks = {}
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", BROADCAST_PORT))
        
        # Receive file size first
        size_data, _ = sock.recvfrom(8)
        expected_size = struct.unpack("!Q", size_data)[0]
        print(f"Expected file size: {expected_size} bytes")
        
        with open(save_path, 'wb') as f:
            while True:
                chunk, addr = sock.recvfrom(BUFFER_SIZE + 4)  # 4 bytes for sequence number
                
                if chunk.startswith(b"EOF:"):
                    expected_checksum = chunk[4:].decode()
                    break
                
                # Extract sequence number and data
                sequence = struct.unpack("!I", chunk[:4])[0]
                data = chunk[4:]
                received_chunks[sequence] = data
            
            # Write chunks in order
            for i in sorted(received_chunks.keys()):
                f.write(received_chunks[i])
            
            # Verify file
            received_size = os.path.getsize(save_path)
            received_checksum = hashlib.md5(open(save_path, 'rb').read()).hexdigest()
            
            print(f"Received file size: {received_size} bytes")
            print(f"Checksum match: {received_checksum == expected_checksum}")
            
            if received_size != expected_size or received_checksum != expected_checksum:
                print("Error: File corruption detected!")
                os.remove(save_path)
            else:
                print(f"File successfully received and saved to {save_path}")
def main():
  threading.Thread(target=broadcast_presence, daemon=True).start()
  threading.Thread(target=listen_for_devices, daemon=True).start()
  save_path = './storage/test.png'
  receive_file(save_path)
  """
  command = input("Enter 'send' to send a file, 'receive' to receive a file, or 'exit' to quit: ")
  if command == 'send':
    target_ip = input("Enter the target device IP: ")
    file_path = input("Enter the file path: ")
    if os.path.exists(file_path):
      send_file(target_ip, file_path)
    else:
      print("File does not exist.")
  elif command == 'receive':
    
  elif command == 'exit':
    return
"""
if __name__ == "__main__":
  main()