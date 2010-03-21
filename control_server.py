from twisted.internet.protocol import Protocol, Factory

from event_bus import EventBus
from event import ControlConnectionReceived, ControlConnectionLost, ControlDataReceived, MUDDataReceived

class ControlServer(Protocol):
    def connectionMade(self):
        print "Control connection received. Starting client connection..."
        self.factory.onConnectionMade(self.transport)

    def connectionLost(self, reason):
        print "Control connection died. Dying along..."
        self.factory.onConnectionLost()

    def dataReceived(self, data):
        print "Got some data: %s" % data
        self.factory.onDataReceived(data)

class ControlServerFactory(Factory):
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

    def onConnectionMade(self, connectionInput):
        ev = ControlConnectionReceived(connectionInput)
        
        EventBus.instance.publish(ev)

    def onConnectionLost(self):
        ev = ControlConnectionLost()

        EventBus.instance.publish(ev)

    def onDataReceived(self, data):
        ev = ControlDataReceived(data)

        EventBus.instance.publish(ev)

    def publish(self, event):
        if isinstance(event, MUDDataReceived):
            self.mainConnection.transport.write(event.data)
