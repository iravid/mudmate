import logging

from twisted.internet.protocol import ClientFactory
from twisted.conch.telnet import Telnet

from events.event_bus import EventBus
from events.event import Event
from events.subscriber import Subscriber

from twisted.conch.telnet import IAC, SB, SE
ATCP = chr(200)

class MUDClient(Telnet):
    def __init__(self):
        Telnet.__init__(self)

        self.swallowedCommands = [ATCP,]
        self.negotiationMap[ATCP] = self.handleAtcp
        self.logger = logging.getLogger("mud_proxy.MUDClient")

    def applicationDataReceived(self, bytes):
        self.factory._dataReceived(bytes)

    def commandReceived(self, command, argument):
        if argument in self.swallowedCommands:
            Telnet.commandReceived(self, command, argument)
        else:
            self.factory._telnetDataReceived(IAC + command + (argument or ""))

    def unhandledCommand(self, command, argument):
        self.logger.warning("Ouch! This shouldn't happen! (%s, %s)" % (ord(command), ord(argument or chr(0))))

    def negotiate(self, bytes):
        command = bytes[0]
        if command in self.swallowedCommands:
            Telnet.negotiate(self, bytes)
        else:
            self.factory._telnetDataReceived(IAC + SB + bytes + IAC + SE)

    def handleAtcp(self, bytes):
        self.factory._atcpReceived(bytes)

    def enableLocal(self, option):
        return option == ATCP

    def enableRemote(self, option):
        return option == ATCP

class MUDClientFactory(ClientFactory, Subscriber):
    def __init__(self):
        self.mainConnection = None

        EventBus.instance.subscribe(self)

        self.logger = logging.getLogger("mud_proxy.MUDClientFactory")

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

    def _telnetDataReceived(self, data):
        ev = Event("TelnetDataReceived", data)
        EventBus.instance.publish(ev)

    def _atcpReceived(self, data):
        self.logger.info("Publish ATCP: %s" % "".join(data))

        ev = Event("ATCPDataReceived", data)
        EventBus.instance.publish(ev)

    def onControlDataReceived(self, event):
        self.mainConnection.transport.write(event.data)

    def onTriggerDataGenerated(self, event):
        for line in event.data:
            self.mainConnection.transport.write(line)
