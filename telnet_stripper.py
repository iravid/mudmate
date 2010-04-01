import logging

import twisted.conch.telnet as tl

from subscriber import Subscriber
from event_bus import EventBus
from event import Event

class TelnetStripper(Subscriber):
    state = "data"

    def __init__(self):
        self.logger = logging.getLogger("mud_proxy.TelnetStripper")

        EventBus.instance.subscribe(self)

    def onRawMUDDataReceived(self, event):
        bytes = event.data
        appData = []

        for byte in bytes:
            if self.state == "data":
                if byte == tl.IAC:
                    # Server wants something special. Next byte should be a command
                    self.state = "escaped"
                else:
                    appData.append(byte)
            elif self.state == "escaped":
                if byte == tl.IAC:
                    # Weird, server sent chr(255) as actual data... switch back to data state
                    appData.append(byte)
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

        ev = Event("MUDDataReceived", "".join(appData))
        EventBus.instance.publish(ev)
