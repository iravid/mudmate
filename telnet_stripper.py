import logging

import twisted.conch.telnet as tl

from subscriber import Subscriber
from event_bus import EventBus
from event import Event

class TelnetStripper(Subscriber):
    """
    This class strips telnet and ANSI command codes off of incoming RawMUDDataReceived
    events, and sends out clean MUDDataReceived events.
    """

    def __init__(self):
        self.logger = logging.getLogger("mud_proxy.TelnetStripper")
        
        # Initialize state-machine
        self.state = "data"

        # Initialize data buffer
        self.lines = []
        self.currentLine = []

        # Compile ANSI regex
        self.ansiRegex = re.compile(r"""
        \x1b     # literal ESC
        \[       # literal [
        [;\d]*   # zero or more digits or semicolons
        [A-Za-z] # a letter
        """, re.VERBOSE)

        EventBus.instance.subscribe(self)

    def onRawMUDDataReceived(self, event):
        bytes = event.data

        # Main state-machine loop to handle the telnet protocol stripping.
        # Mostly shamelessly stolen from twisted.conch.telnet.Telnet#dataReceived
        for byte in bytes:
            if self.state == "data":
                if byte == tl.IAC:
                    # Server wants something special. Next byte should be a command
                    self.state = "escaped"
                elif byte == '\n':
                    # This is one of the cases where we stop buffering and stuff the line
                    # into self.lines.
                    self.currentLine.append(byte)
                    self.lines.append("".join(self.currentLine))
                    self.currentLine = []
                else:
                    self.currentLine.append(byte)
            elif self.state == "escaped":
                if byte == tl.IAC:
                    # Weird, server sent chr(255) as actual data... switch back to data state
                    self.currentLine.append(byte)
                    self.state = "data"
                elif byte in (tl.NOP, tl.DM, tl.BRK, tl.IP, tl.AO, tl.AYT, tl.EC, tl.EL, tl.GA):
                    # These commands usually mean we can safely stop buffering and stuff the current line
                    # into self.lines
                    self.lines.append("".join(self.currentLine))
                    self.currentLine = []
                    self.state = "data"
                elif byte in (tl.WILL, tl.WONT, tl.DO, tl.DONT):
                    # Next byte will be the subject of the W/D, so we switch to command state.
                    self.state = "command"
                elif byte == tl.SB:
                    # Subnegotiation
                    self.state = "sb"
            elif self.state == "command":
                # Only case we might handle this in the future is for ATCP (200)
                self.state = "data"
                continue
            elif self.state == "sb":
                if byte == tl.IAC:
                    # Switch to sb-escaped, next byte might be SE
                    self.state = "sb-escaped"
                else:
                    continue
            elif self.state == "sb-escaped":
                if byte == tl.SE:
                    # Done negotiating. Twisted stops buffering the appData and sends it over at 
                    # this point for some reason...
                    self.state = "data"
                else:
                    self.state = "sb"
            else:
                raise ValueError("How did I get here...?")

        for line in self.lines:
            # Strip ANSI codes
            strippedLine = self.ansiRegex.sub("", line)

            ev = Event("MUDDataReceived", strippedLine)
            EventBus.instance.publish(ev)

        self.lines = []
