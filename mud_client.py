from twisted.internet.protocol import Protocol, ClientFactory

from event_bus import EventBus
from event import MUDDataReceived, ControlDataReceived

class MUDClient(Protocol):
    def dataReceived(self, data):
        self.factory.onDataReceived(data)

class MUDClientFactory(ClientFactory):
    def __init__(self):
        self.mainConnection = None

        EventBus.instance.subscribe(self)

    def buildProtocol(self, addr):
        if self.mainConnection is None:
            protocol = MUDClient()

            protocol.factory = self
            self.mainConnection = protocol

            return protocol
        else:
            return None

    def onDataReceived(self, data):
        ev = MUDDataReceived(data)

        EventBus.instance.publish(ev)

    def handle(self, event):
        if isinstance(event, ControlDataReceived):
            self.mainConnection.transport.write(event.data)
