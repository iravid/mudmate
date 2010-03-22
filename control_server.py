from twisted.internet.protocol import Protocol, Factory

from event_bus import EventBus
from event import ControlConnectionReceived, ControlConnectionLost, ControlDataReceived, MUDDataReceived

class ControlServer(Protocol):
    def connectionMade(self):
        print "Control connection received. Starting client connection..."
        self.factory._connectionMade(self.transport)

    def connectionLost(self, reason):
        print "Control connection died. Dying along..."
        self.factory._connectionLost()

    def dataReceived(self, data):
        print "Got some data: %s" % data
        self.factory._dataReceived(data)

class ControlServerFactory(Factory, Subscriber):
    def __init__(self):
        self.mainConnection = None

        EventBus.instance.subscribe(self)

    def buildProtocol(self, addr):
        if self.mainConnection is None:
            # First connection, proceed normally
            protocol = ControlServer()

            protocol.factory = self
            self.mainConnection = protocol

            return protocol
        else:
            # Another connection, just drop it
            return None

    def _connectionMade(self, connectionInput):
        ev = ControlConnectionReceived(connectionInput)
        
        EventBus.instance.publish(ev)

    def _connectionLost(self):
        ev = ControlConnectionLost()

        EventBus.instance.publish(ev)

    def _dataReceived(self, data):
        ev = ControlDataReceived(data)

        EventBus.instance.publish(ev)

    def onMUDDataReceived(self, event):
        self.mainConnection.transport.write(event.data)
