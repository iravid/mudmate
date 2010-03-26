from twisted.internet.protocol import Protocol, ClientFactory
from twisted.conch.telnet import StatefulTelnetProtocol

from event_bus import EventBus
from event import MUDDataReceived, ControlDataReceived
from subscriber import Subscriber

class MUDClient(StatefulTelnetProtocol):
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
        ev = MUDDataReceived(data)

        EventBus.instance.publish(ev)

    def onControlDataReceived(self, event):
        self.mainConnection.transport.write(event.data)
