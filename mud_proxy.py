from twisted.internet import reactor

from control_server import ControlServerFactory
from mud_client import MUDClientFactory
from event_bus import EventBus
from event import ControlConnectionReceived, ControlConnectionLost
from config import MUD_HOSTNAME, MUD_PORT

class MUDProxy(object):
    def __init__(self):
        self.controlServerFactory = ControlServerFactory()
        self.mudClientFactory = MUDClientFactory()
        
        EventBus.instance.subscribe(self)
        
        reactor.listenTCP(10023, self.controlServerFactory)

    def publish(self, event):
        if isinstance(event, ControlConnectionReceived):
            reactor.connectTCP(MUD_HOSTNAME, MUD_PORT, self.mudClientFactory)

        if isinstance(event, ControlConnectionLost):
            reactor.stop()


mudProxy = MUDProxy()

reactor.run()
