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
    
    RDESC_BUFFER_REGEX = r"^(?P<descLine>[^<]*)(?P<closeTag></RDesc>)?"
    
    rules = {
        r"<RNum (?P<rnum>\d+)>": "FoundRnum",
        r"<RName>(?P<rname>.*)</RName>": "FoundRname",
        r"<RDesc>(?P<descLine>[^<]*)": "FoundRdescOpen",
    }

    def __init__(self):
        RegexProcessor.__init__(self)

        self.logger = logging.getLogger("mud_proxy.MXPMapper")
        
        # See matchData for explanation
        self.installLater = []
        self.removeLater = []

    def matchData(self, data):
        responses = RegexProcessor.matchData(self, data)

        # Since we don't want the rules list to mutate during a parsing pass, we schedule
        # the addition of new rules in self.installLater and install them after we finish parsing.
        # The RDesc and RExits bufferings use this.
        for regex, handler in self.installLater:
            if self.rules.get(regex):
                self.logger.warning("Yikes! The regex I'm installing already exists...")

            self.rules[regex] = handler

        self.installLater = []

        # Same idea, but for removing rules:
        for regex in self.removeLater:
            if not self.rules.get(regex):
                self.logger.warning("Yikes! The regex I'm removing doesn't exist...")

            self.rules.pop(regex, None)

        self.removeLater = []

        return responses

    def onFoundRnum(self, match):
        self.logger.info("Found RNum %s" % match.groupdict()["rnum"])

    def onFoundRname(self, match):
        self.logger.info("Found RName '%s'" % match.groupdict()["rname"])

    def onFoundRdescOpen(self, match):
        self.logger.info("Found RDesc opening tag, first line is: %s" % match.groupdict()["descLine"])
        self.activateRdescBuffering(match.groupdict()["descLine"])

    def activateRdescBuffering(self, firstLine):
        self.logger.info("Activating RDesc buffering")
        self.rdescBuffer = [firstLine,]
        self.installLater.append((self.RDESC_BUFFER_REGEX, self.onRdescBuffer))

    def onRdescBuffer(self, match):
        self.logger.info("Buffering into RDesc: %s" % match.groupdict()["descLine"])
        self.rdescBuffer.append(match.groupdict()["descLine"])

        if match.groupdict().get("closeTag"):
            self.logger.info("Found RDesc close, desc was:")
            self.logger.info("".join(self.rdescBuffer))

            # Check for errors: MXP tags showing up in the desc is definitely not right
            if re.search("<.*>", "".join(self.rdescBuffer)):
                self.logger.error("Ugh, MXP tags showed up in the RDesc text")

            # Cleanup
            del self.rdescBuffer
            self.removeLater.append(self.RDESC_BUFFER_REGEX)
