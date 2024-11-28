import socket
import threading
import os
import time

BROADCAST_PORT = 37020
BUFFER_SIZE = 1024

def broadcast_presence():
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.2)
    """
    message = b"Device available"
    while True:
      sock.sendto(message, ('<broadcast>', BROADCAST_PORT))
      # print("Broadcasting presence...")
      time.sleep(5)
    """

def listen_for_devices():
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    while True:
      data, addr = sock.recvfrom(BUFFER_SIZE)
      print(f"Detected device: {addr} - {data.decode()}")

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

def main():
  threading.Thread(target=broadcast_presence, daemon=True).start()
  threading.Thread(target=listen_for_devices, daemon=True).start()
  command = input("Enter 'send' to send a file, 'receive' to receive a file, or 'exit' to quit: ")
  if command == 'send':
    target_ip = input("Enter the target device IP: ")
    file_path = input("Enter the file path: ")
    if os.path.exists(file_path):
      send_file(target_ip, file_path)
    else:
      print("File does not exist.")
  elif command == 'receive':
    save_path = input("Enter the path to save the received file: ")
    receive_file(save_path)
  elif command == 'exit':
    return

if __name__ == "__main__":
  main()