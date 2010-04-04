import logging
import re

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
    REXITS_BUFFER_REGEX = r"^(?P<exitsLine>.*\.)(?P<closeTag><RExits>)?"
    
    rules = {
        r"<RNum (?P<rnum>\d+)>": "FoundRnum",
        r"<RName>(?P<rname>.*)</RName>": "FoundRname",
        r"<RDesc>(?P<descLine>[^<]*)(?P<closeTag></RDesc>)?": "FoundRdescOpen",
        r"^(.*</RDesc>\s*)?<RExits>(?P<exitsLine>.*\.)(?P<closeTag><RExits>)?": "FoundRexitsOpen",
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
        self.activateRdescBuffering(match)

    def activateRdescBuffering(self, match):
        self.logger.info("Activating RDesc buffering")
        self.rdescBuffer = [match.groupdict()["descLine"],]

        # Handle one-line descriptions: don't add the RDESC_BUFFER_REGEX in case this is one
        # of those.
        if match.groupdict().get("closeTag"):
            self.logger.info("One-line RDesc, stopping now")
            del self.rdescBuffer
        else:
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

    # TODO: refactor all this and the RDesc buffering to derive from a common something
    def onFoundRexitsOpen(self, match):
        self.logger.info("Found RExits opening tag, first line is: %s" % match.groupdict()["exitsLine"])
        self.activateRexitsBuffering(match)

    def activateRexitsBuffering(self, match):
        self.logger.info("Activating RExits buffering")
        self.rexitsBuffer = [match.groupdict()["exitsLine"],]

        # Handle one-line exit descriptions
        if match.groupdict().get("closeTag"):
            self.logger.info("One-line RExits, stopping now")
            del self.rexitsBuffer
        else:
            self.installLater.append((self.REXITS_BUFFER_REGEX, self.onRexitsBuffer))

    def onRexitsBuffer(self, match):
        self.logger.info("Buffering into RExits: %s" % match.groupdict()["exitsLine"])
        self.rexitsBuffer.append(match.groupdict()["exitsLine"])

        if match.groupdict().get("closeTag"):
            self.logger.info("Found RExits close, exits was:")
            self.logger.info("".join(self.rexitsBuffer))

            del self.rexitsBuffer
            self.removeLater.append(self.REXITS_BUFFER_REGEX)
