import socket
import threading
import logging

class ESPUDPLink:
  def __init__(self, udp_host="192.168.43.42", app_port=2399, device_port=2390):
    self.udp_host = udp_host
    self.app_port = app_port
    self.device_port = device_port
    self.client_socket = None
    self.state = "idle"
    self.state_callback = None
    self.connect_callback = None
    self.listener_thread = None
    logging.basicConfig(level=logging.INFO)

  def set_state(self, new_state):
    self.state = new_state
    if self.state_callback:
      self.state_callback(self.state)
    logging.info(f"State updated to: {self.state}")

  def connect(self, callback=None):
    try:
      self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      self.client_socket.bind(("", self.app_port))
      self.connect_callback = callback
      self.set_state("connected")
      if self.connect_callback:
        self.connect_callback(True)

      # Start listener thread for incoming data
      self.listener_thread = threading.Thread(target=self.listen_for_data, daemon=True)
      self.listener_thread.start()

    except Exception as e:
      logging.error(f"Failed to connect: {e}")
      if self.connect_callback:
        self.connect_callback(False)

  def listen_for_data(self):
    logging.info("Listening for incoming data...")
    while self.state == "connected":
      try:
        data, addr = self.client_socket.recvfrom(1024)  # Adjust buffer size as needed
        self.handle_received_data(data, addr)
      except Exception as e:
        logging.error(f"Error receiving data: {e}")
        break

  def handle_received_data(self, data, addr):
    try:
      message = data.decode("utf-8")
      logging.info(f"Received from {addr}: {message}")
    except UnicodeDecodeError:
      logging.warning("Received non-UTF-8 data")

  def send_packet(self, packet, callback=None):
    try:
      self.client_socket.sendto(packet, (self.udp_host, self.device_port))
      if callback:
        callback(True)
      logging.info("Packet sent successfully")
    except Exception as e:
      logging.error(f"Failed to send packet: {e}")
      if callback:
        callback(False)

  def disconnect(self):
    if self.client_socket:
      self.client_socket.close()
    self.set_state("idle")
    logging.info("Disconnected")

  def on_state_updated(self, callback):
    self.state_callback = callback

# Example usage
if __name__ == "__main__":
  def state_update_callback(state):
    print(f"State updated: {state}")

  def connection_callback(success):
    if success:
      print("Connected successfully")
    else:
      print("Failed to connect")

  esp_link = ESPUDPLink()
  esp_link.on_state_updated(state_update_callback)
  esp_link.connect(connection_callback)

  try:
    while esp_link.state == "connected":
      # Example of sending a packet
      esp_link.send_packet(b"Hello, Drone!")
  except KeyboardInterrupt:
    esp_link.disconnect()
