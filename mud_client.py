from twisted.internet.protocol import Protocol, ClientFactory

from event_bus import EventBus
from event import Event
from subscriber import Subscriber

class MUDClient(Protocol):
    def dataReceived(self, data):
        self.factory._dataReceived(data)

class MUDClientFactory(ClientFactory, Subscriber):
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

    def _dataReceived(self, data):
        ev = Event("RawMUDDataReceived", data)
        EventBus.instance.publish(ev)

    def onControlDataReceived(self, event):
        self.mainConnection.transport.write(event.data)

    def onTriggerDataGenerated(self, event):
        for line in event.data:
            self.mainConnection.transport.write(line)
