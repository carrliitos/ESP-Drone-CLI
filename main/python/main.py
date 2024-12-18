# -*- coding: utf-8 -*-
# File Name:          main.py
#
# Created on:         2024-12-08 22:21:42
#     Author:         carlitos
#
# Last Modified by:   carrliitos
# Last Modified time: 2024-12-08 22:40:35

from flask import Flask, request, jsonify
import socket
import threading
import time

app = Flask(__name__)

# Configuration
LOCAL_IP = "192.168.43.43"  # Replace with your device's IP
LOCAL_PORT = 2399           # Local port to bind to
DRONE_IP = "192.168.43.42"  # Replace with the ESP-Drone's static IP
DRONE_PORT = 2390           # Drone's listening port

# UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((LOCAL_IP, LOCAL_PORT))

# State and Callbacks
state = "idle"
state_callback = None
received_data_callback = None

def update_state(new_state):
  """Update the connection state and trigger the callback."""
  global state, state_callback
  state = new_state
  if state_callback:
    state_callback(state)

def udp_listener():
  """Background thread to listen for UDP packets."""
  while True:
    try:
      data, addr = udp_socket.recvfrom(1024)
      print(f"Received from {addr}: {data}")
      if received_data_callback:
        received_data_callback(data, addr)
    except Exception as e:
      print(f"Error in UDP listener: {e}")

# Start the UDP listener thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

@app.route('/connect', methods=['POST'])
def connect():
  """Simulate connection to the drone."""
  global state
  try:
    # Simulate a connection process
    update_state("connecting")
    time.sleep(1)  # Simulate delay
    update_state("connected")
    return jsonify({"message": "Connected to ESP-Drone"}), 200
  except Exception as e:
    update_state("idle")
    return jsonify({"error": f"Connection failed: {e}"}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect():
  """Simulate disconnection from the drone."""
  global state
  try:
    update_state("idle")
    return jsonify({"message": "Disconnected from ESP-Drone"}), 200
  except Exception as e:
    return jsonify({"error": f"Disconnection failed: {e}"}), 500

@app.route('/send', methods=['POST'])
def send_packet():
  """Send a UDP packet to the drone."""
  data = request.json.get("data")
  if not data:
    return jsonify({"error": "No data provided"}), 400

  try:
    packet = bytes(data)
    udp_socket.sendto(packet, (DRONE_IP, DRONE_PORT))
    return jsonify({"message": "Packet sent"}), 200
  except Exception as e:
    return jsonify({"error": f"Failed to send packet: {e}"}), 500

@app.route('/register_state_callback', methods=['POST'])
def register_state_callback():
  """Register a callback for state changes."""
  global state_callback
  state_callback = lambda new_state: print(f"State updated: {new_state}")
  return jsonify({"message": "State callback registered"}), 200

@app.route('/register_data_callback', methods=['POST'])
def register_data_callback():
  """Register a callback for received data."""
  global received_data_callback
  received_data_callback = lambda data, addr: print(f"Received from {addr}: {data}")
  return jsonify({"message": "Data callback registered"}), 200

@app.route('/state', methods=['GET'])
def get_state():
  """Get the current state."""
  return jsonify({"state": state}), 200

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080)

