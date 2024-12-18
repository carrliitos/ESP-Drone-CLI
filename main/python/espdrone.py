import datetime
import logging
import time
from collections import namedtuple
from threading import Lock
from threading import Thread
from threading import Timer

import cflib

from cflib.utils import uri_helper
from cflib.utils.callbacks import Caller

from cflib.crazyflie.high_level_commander import HighLevelCommander
from cflib.crazyflie.toccache import TocCache
from cflib.crazyflie.platformservice import PlatformService
from cflib.crazyflie.param import Param
from cflib.crazyflie.mem import Memory
from cflib.crazyflie.log import Log
from cflib.crazyflie.localization import Localization
from cflib.crazyflie.extpos import Extpos
from cflib.crazyflie.console import Console
from cflib.crazyflie.commander import Commander

logging.basicConfig(level = logging.ERROR,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DRONE_URI = uri_helper.uri_from_env(default="udp://192.168.43.42:2390")

class State:
  """Stat of the connection procedure"""
  DISCONNECTED = 0
  INITIALIZED = 1
  CONNECTED = 2
  SETUP_FINISHED = 3


class Espdrone():
  """The Espdrone class"""

  def __init__(self, name=None, link=None, ro_cache=None, rw_cache=None):
    """
    Create the objects from this module and register callbacks.

    ro_cache -- Path to read-only cache (string)
    rw_cache -- Path to read-write cache (string)
    """

    # Called on disconnect, no matter the reason
    self.disconnected = Caller()
    # Called on unintentional disconnect only
    self.connection_lost = Caller()
    # Called when the first packet in a new link is received
    self.link_established = Caller()
    # Called when the user requests a connection
    self.connection_requested = Caller()
    # Called when the link is established and the TOCs (that are not
    # cached) have been downloaded
    self.connected = Caller()
    # Called if establishing of the link fails (i.e times out)
    self.connection_failed = Caller()
    # Called for every packet received
    self.packet_received = Caller()
    # Called for every packet sent
    self.packet_sent = Caller()
    # Called when the link driver updates the link quality measurement
    self.link_quality_updated = Caller()

    self.state = State.DISCONNECTED
    
    self.link = link
    self.name = name
    self._toc_cache = TocCache(ro_cache=ro_cache, rw_cache=rw_cache)

    self.incoming = _IncomingPacketHandler(self)
    self.incoming.setDaemon(True)
    self.incoming.start()

    self.commander = Commander(self)
    self.high_level_commander = HighLevelCommander(self)
    self.loc = Localization(self)
    self.extpos = Extpos(self)
    self.log = Log(self)
    self.console = Console(self)
    self.param = Param(self)
    self.mem = Memory(self)
    self.platform = PlatformService(self)

    self.link_uri = DRONE_URI

    # Used for retry when no reply was sent back
    self.packet_received.add_callback(self._check_for_initial_packet_cb)
    self.packet_received.add_callback(self._check_for_answers)

    self._answer_patterns = {}

    self._send_lock = Lock()

    self.connected_ts = None

    # Connect callbacks to logger
    self.disconnected.add_callback(lambda uri: logger.info(f'Callback->Disconnected from [{uri}]'))
    self.disconnected.add_callback(self._disconnected)
    self.link_established.add_callback(lambda uri: logger.info(f'Callback->Connected to [{uri}]'))
    self.connection_lost.add_callback(lambda uri, errmsg: logger.info(f'Callback->Connection lost to [{uri}]: {errmsg}'))
    self.connection_failed.add_callback(lambda uri, errmsg: logger.info(f'Callback->Connected failed to [{uri}]: {errmsg}'))
    self.connection_requested.add_callback(lambda uri: logger.info(f'Callback->Connection initialized [{uri}]'))
    self.connected.add_callback(lambda uri: logger.info(f'Callback->Connection setup finished [{uri}]'))

  def _disconnected(self, link_uri):
    """ Callback when disconnected."""
    self.connected_ts = None

  def _start_connection_setup(self):
    """Start the connection setup by refreshing the TOCs"""
    logger.info(f'We are connected [{self.link_uri}], request connection setup')
    self.platform.fetch_platform_informations(self._platform_info_fetched)

  def _platform_info_fetched(self):
    self.log.refresh_toc(self._log_toc_updated_cb, self._toc_cache)

  def _param_toc_updated_cb(self):
    """Called when the param TOC has been fully updated"""
    logger.info('Param TOC finished updating')
    self.connected_ts = datetime.datetime.now()
    self.connected.call(self.link_uri)
    # Trigger the update for all the parameters
    self.param.request_update_of_all_params()

  def _mems_updated_cb(self):
    """Called when the memories have been identified"""
    logger.info('Memories finished updating')
    self.param.refresh_toc(self._param_toc_updated_cb, self._toc_cache)

  def _log_toc_updated_cb(self):
    """Called when the log TOC has been fully updated"""
    logger.info('Log TOC finished updating')
    self.mem.refresh(self._mems_updated_cb)

  def _link_error_cb(self, errmsg):
    """Called from the link driver when there's an error"""
    logger.warning(f'Got link error callback [{errmsg}] in state [{self.state}]')
    if (self.link is not None):
      self.link.close()
    self.link = None
    if (self.state == State.INITIALIZED):
      self.connection_failed.call(self.link_uri, errmsg)
    if (self.state == State.CONNECTED or self.state == State.SETUP_FINISHED):
      self.disconnected.call(self.link_uri)
      self.connection_lost.call(self.link_uri, errmsg)
    self.state = State.DISCONNECTED

  def _link_quality_cb(self, percentage):
    """Called from link driver to report link quality"""
    self.link_quality_updated.call(percentage)

  def _check_for_initial_packet_cb(self, data):
    """
    Called when first packet arrives from Espdrone.

    This is used to determine if we are connected to something that is
    answering.
    """
    self.state = State.CONNECTED
    self.link_established.call(self.link_uri)
    self.packet_received.remove_callback(self._check_for_initial_packet_cb)

  def open_link(self, link_uri):
    """
    Open the communication link to a copter at the given URI and setup the
    connection (download log/parameter TOC).
    """
    self.connection_requested.call(link_uri)
    self.state = State.INITIALIZED
    self.link_uri = link_uri
    try:
      self.link = cflib.crtp.get_link_driver(link_uri, self._link_quality_cb, self._link_error_cb)

      if not self.link:
        message = f'No driver found or malformed URI: {link_uri}'
        logger.warning(message)
        print(f"connection_failed. {message}")
        self.connection_failed.call(link_uri, message)
      else:
        # Add a callback so we can check that any data is coming
        # back from the copter
        self.packet_received.add_callback(self._check_for_initial_packet_cb)

        self._start_connection_setup()
    except Exception as ex:  # pylint: disable=W0703
      # We want to catch every possible exception here and show
      # it in the user interface
      import traceback

      logger.error(f"Couldn't load link driver: {ex}\n\n{traceback.format_exc()}")
      exception_text = f"Couldn't load link driver: {ex}\n\n{traceback.format_exc()}"
      if self.link:
        self.link.close()
        self.link = None
      self.connection_failed.call(link_uri, exception_text)
      raise ConnectionError()

  def close_link(self):
    """Close the communication link."""
    logger.info('Closing link')
    if (self.link is not None):
      self.commander.send_setpoint(0, 0, 0, 0)
    if (self.link is not None):
      self.link.close()
      self.link = None
    self._answer_patterns = {}
    self.disconnected.call(self.link_uri)

  """Check if the communication link is open or not."""

  def is_connected(self):
    return self.connected_ts is not None

  def add_port_callback(self, port, cb):
    """Add a callback to cb on port"""
    self.incoming.add_port_callback(port, cb)

  def remove_port_callback(self, port, cb):
    """Remove the callback cb on port"""
    self.incoming.remove_port_callback(port, cb)

  def _no_answer_do_retry(self, pk, pattern):
    """Resend packets that we have not gotten answers to"""
    logger.info(f'Resending for pattern {pattern}')
    # Set the timer to None before trying to send again
    self.send_packet(pk, expected_reply=pattern, resend=True)

  def _check_for_answers(self, pk):
    """
    Callback called for every packet received to check if we are
    waiting for an answer on this port. If so, then cancel the retry
    timer.
    """
    longest_match = ()
    if len(self._answer_patterns) > 0:
      data = (pk.header,) + tuple(pk.data)
      for p in list(self._answer_patterns.keys()):
        logger.debug(f'Looking for pattern match on {p} vs {data}')
        if len(p) <= len(data):
          if p == data[0:len(p)]:
            match = data[0:len(p)]
            if len(match) >= len(longest_match):
              logger.debug(f'Found new longest match {match}')
              longest_match = match
    if len(longest_match) > 0:
      self._answer_patterns[longest_match].cancel()
      del self._answer_patterns[longest_match]

  def send_packet(self, pk, expected_reply=(), resend=False, timeout=0.1):
    """
    Send a packet through the link interface.

    pk -- Packet to send
    expect_answer -- True if a packet from the Espdrone is expected to
             be sent back, otherwise false

    """
    self._send_lock.acquire()
    if self.link is not None:
      if len(expected_reply) > 0 and not resend and self.link.needs_resending:
        pattern = (pk.header,) + expected_reply
        logger.debug(f'Sending packet and expecting the {pattern} pattern back')
        new_timer = Timer(timeout, lambda: self._no_answer_do_retry(pk, pattern))
        self._answer_patterns[pattern] = new_timer
        new_timer.start()
      elif resend:
        # Check if we have gotten an answer, if not try again
        pattern = expected_reply
        if pattern in self._answer_patterns:
          logger.debug('We want to resend and the pattern is there')
          if self._answer_patterns[pattern]:
            new_timer = Timer(timeout, lambda: self._no_answer_do_retry(pk, pattern))
            self._answer_patterns[pattern] = new_timer
            new_timer.start()
        else:
          logger.debug(f'Resend requested, but no pattern found: {self._answer_patterns}')
      self.link.send_packet(pk)
      self.packet_sent.call(pk)
    self._send_lock.release()


_CallbackContainer = namedtuple('CallbackConstainer', 'port port_mask channel channel_mask callback')


class _IncomingPacketHandler(Thread):
  """Handles incoming packets and sends the data to the correct receivers"""

  def __init__(self, ed):
    Thread.__init__(self)
    self.ed = ed
    self.cb = []

  def add_port_callback(self, port, cb):
    """Add a callback for data that comes on a specific port"""
    logger.debug(f'Adding callback on port [{port}] to [{cb}]')
    self.add_header_callback(cb, port, 0, 0xff, 0x0)

  def remove_port_callback(self, port, cb):
    """Remove a callback for data that comes on a specific port"""
    logger.debug(f'Removing callback on port [{port}] to [{cb}]')
    for port_callback in self.cb:
      if port_callback.port == port and port_callback.callback == cb:
        self.cb.remove(port_callback)

  def add_header_callback(self, cb, port, channel, port_mask=0xFF, channel_mask=0xFF):
    """
    Add a callback for a specific port/header callback with the
    possibility to add a mask for channel and port for multiple
    hits for same callback.
    """
    self.cb.append(_CallbackContainer(port, port_mask, channel, channel_mask, cb))

  def run(self):
    while True:
      if self.ed.link is None:
        time.sleep(1)
        continue
      pk = self.ed.link.receive_packet(1)

      if pk is None:
        continue

      # All-packet callbacks
      self.ed.packet_received.call(pk)

      found = False
      for cb in (cb for cb in self.cb
                 if cb.port == (pk.port & cb.port_mask) and
                 cb.channel == (pk.channel & cb.channel_mask)):
        try:
          cb.callback(pk)
        except Exception:  # pylint: disable=W0703
          # Disregard pylint warning since we want to catch all
          # exceptions and we can't know what will happen in
          # the callbacks.
          import traceback

          logger.error('Exception while doing callback on port {pk.port}\n\n{traceback.format_exc()}')
        if cb.port != 0xFF:
          found = True

      if not found:
        pass

