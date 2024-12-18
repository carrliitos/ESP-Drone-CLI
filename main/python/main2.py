import socket
import struct
import time

# Configuration for the ESP-Drone in Access Point (AP) mode
local_ip = "192.168.1.76"  # Replace with your device's IP assigned by the drone
local_port = 2399
drone_ip = "192.168.43.42"
drone_port = 2390

class ESPUDPLink:
  def __init__(self, local_ip, local_port, drone_ip, drone_port):
    self.local_ip = local_ip
    self.local_port = local_port
    self.drone_ip = drone_ip
    self.drone_port = drone_port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind((self.local_ip, self.local_port))
  
  def send_packet(self, data):
    self.socket.sendto(data, (self.drone_ip, self.drone_port))
  
  def close(self):
    self.socket.close()

def create_motor_command(thrust, roll=0.0, pitch=0.0, yaw=0.0):
  """
  Constructs a CRTP-compatible motor command packet.

  Parameters:
  - thrust (int): Thrust value (0-65535).
  - roll (float): Roll value (-1.0 to 1.0).
  - pitch (float): Pitch value (-1.0 to 1.0).
  - yaw (float): Yaw value (-1.0 to 1.0).

  Returns:
  - bytes: The binary CRTP command packet.
  """
  header = 0x30  # CRTP header for motor commands
  packet = struct.pack('<BfffH', header, roll, pitch, yaw, thrust)
  return packet

def main():
  link = ESPUDPLink(local_ip, local_port, drone_ip, drone_port)
  try:
    while True:
      # Send command to spin motors with low thrust for 1 second
      print("Spinning motors...")
      motor_command = create_motor_command(thrust=30000)  # Adjust thrust as needed
      link.send_packet(motor_command)
      time.sleep(1)  # Keep motors running for 1 second

      # Send command to stop motors
      print("Stopping motors...")
      stop_command = create_motor_command(thrust=0)
      link.send_packet(stop_command)
      time.sleep(4)  # Wait 4 seconds before next spin
  except KeyboardInterrupt:
    print("Exiting...")
  finally:
    link.close()

if __name__ == "__main__":
  main()
