from twisted.internet import reactor

from control_server import ControlServerFactory
from mud_client import MUDClientFactory
from event_bus import EventBus
from subscriber import Subscriber
from regex_processor import RegexProcessor
from config import MUD_HOSTNAME, MUD_PORT

class MUDProxy(Subscriber):
    def __init__(self):
        self.controlServerFactory = ControlServerFactory()
        self.mudClientFactory = MUDClientFactory()
        self.regexProcessor = RegexProcessor()
        
        EventBus.instance.subscribe(self)
        
        reactor.listenTCP(10023, self.controlServerFactory)

    def onControlConnectionReceived(self, event):
        reactor.connectTCP(MUD_HOSTNAME, MUD_PORT, self.mudClientFactory)

    def onControlConnectionLost(self, event):
        reactor.stop()

if __name__ == "__main__":
    mudProxy = MUDProxy()
    reactor.run()
