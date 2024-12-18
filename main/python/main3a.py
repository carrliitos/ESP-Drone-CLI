import logging
import sys

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.utils import uri_helper
import cflib.crtp

from PyQt5 import QtCore, QtWidgets, QtGui

logging.basicConfig(level=logging.INFO)

class ESPDrone:
  """Class to handle ESPDrone using Crazyflie API."""
  def __init__(self, URI):
    self.URI = URI
    self.cf = Crazyflie(ro_cache=None, rw_cache="cache")

    # Initialize drivers before connecting
    cflib.crtp.init_drivers()

    # Connect callbacks
    self.cf.connected.add_callback(self.connected)
    self.cf.disconnected.add_callback(self.disconnected)

    # Connect to the Crazyflie
    logging.info(f"Attempting to connect to {URI}")
    self.cf.open_link(URI)

    if not self.cf.link:
      logging.error("Could not connect to Crazyflie")
      sys.exit(1)

    if not hasattr(self.cf.link, "cpx"):
      logging.info("Not connecting with WiFi")
      self.cf.close_link()
    else:
      self.hover = {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0, "height": 0.3}
      self.hoverTimer = QtCore.QTimer()
      self.hoverTimer.timeout.connect(self.sendHoverCommand)
      self.hoverTimer.setInterval(100)
      self.hoverTimer.start()

  def disconnected(self, URI):
    logging.info(f"Disconnected from {URI}")
    sys.exit(1)

  def connected(self, URI):
    logging.info(f"Connected to {URI}")

    # Configure logging
    lp = LogConfig(name="Position", period_in_ms=100)
    try:
      lp.add_variable("stateEstimate.x", "float")
      lp.add_variable("stateEstimate.y", "float")
      lp.add_variable("stateEstimate.z", "float")
      lp.add_variable("stabilizer.roll", "float")
      lp.add_variable("stabilizer.pitch", "float")
      lp.add_variable("stabilizer.yaw", "float")

      self.cf.log.add_config(lp)
      lp.data_received_cb.add_callback(self.pos_data)
      lp.start()
    except KeyError as e:
      logging.error(f"Could not start log configuration, {e} not found in TOC.")
    except AttributeError:
      logging.error("Could not add log config, bad configuration.")

  def pos_data(self, timestamp, data, logconf):
    """Callback function for log data."""
    logging.info(f"Log Data @ {timestamp}: {data}")

if __name__ == "__main__":
  URI = uri_helper.uri_from_env(default="udp://192.168.43.42:2390")
  drone = ESPDrone(URI)
  # Main thread should wait for user interaction or run indefinitely
  try:
    while True:
      pass
  except KeyboardInterrupt:
    logging.info("Interrupted by user, closing connection.")
    drone.cf.close_link()
