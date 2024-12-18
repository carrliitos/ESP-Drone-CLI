import socket
import time
import logging

logging.basicConfig(level=logging.DEBUG)

# Define UDP communication parameters
DRONE_IP = "192.168.43.42"
DRONE_PORT = 2390
APP_PORT = 2399

# CRTP Ports
CRTP_PORT_COMMANDER = 3

# CRTP Packet Structure
CRTP_HEADER_PORT_BITS = 4
CRTP_HEADER_CHANNEL_BITS = 2
CRTP_HEADER_RESERVED_BITS = 2

class ESPDroneApp:
  def __init__(self, drone_ip, drone_port, app_port):
    self.drone_ip = drone_ip
    self.drone_port = drone_port
    self.app_port = app_port

    # Create a UDP socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      # Bind the socket to the app's TX/RX port
      self.sock.bind((drone_ip, app_port))
      logging.info(f"Socket bound to {drone_ip}:{app_port}")
    except OSError as e:
      logging.error(f"Failed to bind socket: {e}")
      exit(1)

  def calculate_checksum(self, header, data):
    """Calculate checksum for the CRTP packet."""
    raw = (header,) + data
    cksum = sum(raw) % 256  # Modulo 256 checksum
    return cksum

  def send_crtp_packet(self, port, channel, data):
    """Construct and send a CRTP packet."""
    # Construct the CRTP header
    header = (port << CRTP_HEADER_CHANNEL_BITS) | channel
    logging.debug(f"Header: {header}")

    # Calculate checksum
    cksum = self.calculate_checksum(header, data)
    logging.debug(f"Checksum: {cksum}")

    # Construct the full packet (header + data + checksum)
    packet = bytearray((header,) + data + (cksum,))
    logging.debug(f"Sending packet: {packet.hex()}")

    # Send the packet to the drone
    self.sock.sendto(packet, (self.drone_ip, self.drone_port))

  def _ramp_motors(self):
    """Ramp motors up and down using CRTP commands."""
    thrust_mult = 1
    thrust_step = 500
    thrust = 20000  # Initial thrust value
    pitch = 0
    roll = 0
    yawrate = 0

    # Unlock startup thrust protection (send initial zero setpoint)
    self.send_crtp_packet(CRTP_PORT_COMMANDER, 0, (0, 0, 0, 0))

    # Ramp up and down thrust
    try:
      while thrust >= 20000:
        # Construct the payload for the setpoint command
        payload = (
          int(roll * 100),    # Roll (scaled to int)
          int(pitch * 100),   # Pitch (scaled to int)
          int(yawrate * 100),   # Yawrate (scaled to int)
          thrust        # Thrust (16-bit unsigned)
        )

        # Send the command packet
        self.send_crtp_packet(CRTP_PORT_COMMANDER, 0, payload)

        # Adjust thrust
        time.sleep(0.1)
        if thrust >= 25000:
          thrust_mult = -1
        thrust += thrust_step * thrust_mult

      # Send a final zero setpoint to stop the motors
      self.send_crtp_packet(CRTP_PORT_COMMANDER, 0, (0, 0, 0, 0))
      logging.info("Motor ramping complete.")
    except Exception as e:
      logging.error(f"Error during motor ramping: {e}")
    finally:
      # Ensure the socket is closed
      self.sock.close()

if __name__ == "__main__":
  # Create an instance of the drone app
  app = ESPDroneApp(DRONE_IP, DRONE_PORT, APP_PORT)

  # Ramp the motors
  app._ramp_motors()
