import logging, logging.config
import sys

from twisted.internet import reactor

from control_server import ControlServerFactory
from mud_client import MUDClientFactory
from event_bus import EventBus
from subscriber import Subscriber
from regex_processor import RegexProcessor
from telnet_stripper import TelnetStripper
from mxp_mapper import MXPMapper
from config import MUD_HOSTNAME, MUD_PORT

class MUDProxy(Subscriber):
    def __init__(self):
        self.logger = logging.getLogger("mud_proxy.MUDProxy")
        self.logger.info("Initialising components")

        self.controlServerFactory = ControlServerFactory()
        self.mudClientFactory = MUDClientFactory()
        self.telnetStripper = TelnetStripper()
        self.regexProcessor = RegexProcessor()
        self.mxpMapper = MXPMapper()
        
        EventBus.instance.subscribe(self)
        
        self.logger.info("Reactor listening at localhost:10023")
        reactor.listenTCP(10023, self.controlServerFactory)

    def onControlConnectionReceived(self, event):
        self.logger.info("Reactor connecting at %s:%s" % (MUD_HOSTNAME, MUD_PORT))
        reactor.connectTCP(MUD_HOSTNAME, MUD_PORT, self.mudClientFactory)

    def onControlConnectionLost(self, event):
        reactor.stop()

def initLogging():
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("mud_proxy")
    logger.info("Initialised logging")

if __name__ == "__main__":
    initLogging()
    mudProxy = MUDProxy()
    reactor.run()
