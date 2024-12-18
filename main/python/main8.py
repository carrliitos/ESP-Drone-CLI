import logging
import socket
import sys
import threading
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crtp.crtpstack import CRTPPacket
from cflib.utils import uri_helper

class ESPDroneUDP:
  def __init__(self, link_uri):
    cflib.crtp.init_drivers()

    # UDP socket for interfacing with GCS
    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock.bind(("192.168.43.42", 2399))

    # Create a Crazyflie object without specifying any cache dirs
    self._cf = Crazyflie()

    # Connect some callbacks from the Crazyflie API
    self._cf.link_established.add_callback(self._connected)
    self._cf.disconnected.add_callback(self._disconnected)
    self._cf.connection_failed.add_callback(self._connection_failed)
    self._cf.connection_lost.add_callback(self._connection_lost)

    print('Connecting to %s' % link_uri)

    # Try to connect to the Crazyflie
    self._cf.open_link(link_uri)

    # Variable used to keep main loop occupied until disconnect
    self.is_connected = True

    threading.Thread(target=self._server).start()

  def _connected(self, link_uri):
    """ This callback is called form the Crazyflie API when a Crazyflie
    has been connected and the TOCs have been downloaded."""
    print('Connected to %s' % link_uri)

    self._cf.packet_received.add_callback(self._got_packet)

  def _got_packet(self, pk):
    if pk.port == CRTP_PORT_MAVLINK:
      self._sock.sendto(pk.data, ("192.168.43.42", 2390))

  def _disconnected(self, link_uri):
    """Callback when the Crazyflie is disconnected (called in all cases)"""
    print('Disconnected from %s' % link_uri)
    self.is_connected = False

if __name__ == "__main__":
  DRONE_URI = uri_helper.uri_from_env(default="udp://192.168.43.42:2390")
  drone = ESPDroneUDP(DRONE_URI)
