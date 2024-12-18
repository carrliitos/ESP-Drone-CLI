import socket
import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG)

class ESPUDPLink:
  def __init__(self, app_port=2399, device_port=2390, udp_host="192.168.43.42"):
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.app_port = app_port
    self.device_port = device_port
    self.udp_host = udp_host
    self.connected = False
    self.state = "idle"

    try:
      self.client_socket.bind(("0.0.0.0", self.app_port))
      logging.info(f"Socket bound to 0.0.0.0:{self.app_port}")
    except OSError as e:
      logging.error(f"Failed to bind socket: {e}")
      exit(1)

  def connect(self):
    """Attempt to connect to the ESP-Drone."""
    self.state = "connecting"
    logging.info("Attempting to connect to ESP-Drone...")
    try:
      # Send an initial packet to establish connection
      self.client_socket.sendto(b'\xFF\x01\x01\x01'.encode(), (self.udp_host, self.device_port))
      logging.info("Connection packet sent.")
      self.state = "connected"
      self.connected = True
      logging.info(f"Connected to {self.udp_host}:{self.device_port}")
    except Exception as e:
      self.state = "idle"
      logging.error(f"Failed to connect: {e}")

  def listen(self):
    """Listen for incoming packets from the ESP-Drone."""
    def _listen():
      while self.connected:
        try:
          data, address = self.client_socket.recvfrom(1024)
          logging.info(f"Received data: {data} from {address}")
        except socket.error as e:
          logging.error(f"Socket error: {e}")
          self.connected = False
          break

    listener_thread = threading.Thread(target=_listen, daemon=True)
    listener_thread.start()

  def disconnect(self):
    """Disconnect from the ESP-Drone."""
    self.connected = False
    self.state = "idle"
    self.client_socket.close()
    logging.info("Disconnected from the ESP-Drone.")

if __name__ == "__main__":
  esp_udp_link = ESPUDPLink()

  try:
    # Attempt to connect to the ESP-Drone
    esp_udp_link.connect()

    if esp_udp_link.connected:
      # Start listening for incoming packets
      esp_udp_link.listen()

      # Keep the script running to listen for packets
      while esp_udp_link.connected:
        time.sleep(1)
  except KeyboardInterrupt:
    esp_udp_link.disconnect()
