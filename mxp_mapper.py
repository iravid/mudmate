import logging

from subscriber import Subscriber
from event_bus import EventBus
from regex_processor import RegexProcessor

class MXPMapper(RegexProcessor):
    """
    An MXP-parsing mapper.

    This class works vaguely like a SAX XML parser, IIRC. 

    The assumption right now is that only <RDesc> and <RExits> need multiline parsing. This can obviously
    break quite easily...
    """
    
    rules = {
        r"<RNum (?P<rnum>\d+)>": "FoundRnum",
        r"<RName>(?P<rname>.*)</RName>": "FoundRname"
    }

    def __init__(self):
        RegexProcessor.__init__(self)

        self.logger = logging.getLogger("mud_proxy.MXPMapper")

    def onFoundRnum(self, match):
        self.logger.info("Found RNum %s" % match.groupdict()["rnum"])

    def onFoundRname(self, match):
        self.logger.info("Found RName '%s'" % match.groupdict()["rname"])
