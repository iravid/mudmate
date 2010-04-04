import logging

from subscriber import Subscriber
from event_bus import EventBus

class MXPMapper(RegexProcessor, Subscriber):
    """
    An MXP-parsing mapper.

    This class works vaguely like a SAX XML parser, IIRC. 

    The assumption right now is that only <RDesc> and <RExits> need multiline parsing. This can obviously
    break quite easily...
    """
    
    rules = {
        r"<RNum (?P<rnum>\d+)>": "foundRnum",
        r"<RName>(?P<rname>.*)</RName>": "foundRname"
    }

    def __init__(self):
        RegexProcessor.__init__(self)

        self.logger = logging.getLogger("mud_proxy.MXPMapper")

    def foundRnum(self, match):
        self.logger.debug("Found RNum %s" % match.groupdict()["rnum"])

    def foundRname(self, match):
        self.logger.debug("Found RName '%s'" % match.groupdict()["rname"])
