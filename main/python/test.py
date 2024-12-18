# -*- coding: utf-8 -*-
# File Name:          test.py
#
# Created on:         2024-12-08 22:50:47
#     Author:         carrliitos
#
# Last Modified by:   carrliitos
# Last Modified time: 2024-12-08 22:53:41

import socket

def get_local_ip(target_ip):
  """Determine the local IP address used to reach a target IP."""
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    try:
      # Connect to the target IP on a dummy port
      s.connect((target_ip, 1))
      print(f"Found: {s}")
      print(f"Binding to IP: {s.getsockname()[0]}")
      return s.getsockname()[0]
    except Exception as e:
      print(f"Error determining local IP: {e}")
      return "127.0.0.1"  # Fallback to localhost

def main():
  DRONE_IP = "192.168.43.42"  # Replace with the ESP-Drone's static IP
  print(get_local_ip(DRONE_IP))

if __name__ == '__main__':
  main()
