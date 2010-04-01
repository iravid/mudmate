import logging
import sys

from twisted.internet import reactor

from control_server import ControlServerFactory
from mud_client import MUDClientFactory
from event_bus import EventBus
from subscriber import Subscriber
from regex_processor import RegexProcessor
from telnet_stripper import TelnetStripper
from config import MUD_HOSTNAME, MUD_PORT

class MUDProxy(Subscriber):
    def __init__(self):
        self.logger = logging.getLogger("mud_proxy.MUDProxy")
        self.logger.debug("Initialising components")

        self.controlServerFactory = ControlServerFactory()
        self.mudClientFactory = MUDClientFactory()
        self.telnetStripper = TelnetStripper()
        self.regexProcessor = RegexProcessor()
        
        EventBus.instance.subscribe(self)
        
        self.logger.info("Reactor listening at localhost:10023")
        reactor.listenTCP(10023, self.controlServerFactory)

    def onControlConnectionReceived(self, event):
        self.logger.info("Reactor connecting at %s:%s" % (MUD_HOSTNAME, MUD_PORT))
        reactor.connectTCP(MUD_HOSTNAME, MUD_PORT, self.mudClientFactory)

    def onControlConnectionLost(self, event):
        reactor.stop()

def initLogging():
    logger = logging.getLogger("mud_proxy")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.debug("Initialised logging")

if __name__ == "__main__":
    initLogging()
    mudProxy = MUDProxy()
    reactor.run()
