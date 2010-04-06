import logging
import re

from events.subscriber import Subscriber
from events.event_bus import EventBus
from modules.regex_processor import RegexProcessor

class MXPParser(RegexProcessor):
    """
    An MXP parser.

    This class works vaguely like a SAX XML parser, IIRC. 

    The assumption right now is that only <RDesc> and <RExits> need multiline parsing. This can obviously
    break quite easily...
    """
    
    RDESC_BUFFER_REGEX = r"^(?P<descLine>[^<]*)(?P<closeTag></RDesc>)?"
    REXITS_BUFFER_REGEX = r"^(?P<exitsLine>.*\.)(?P<closeTag></*RExits>)?"
    REXITS_EXIT_REGEX = r'<SEND HREF="(?P<dir>[^"]*)">(?P<dirText>[^<]*)</SEND>(?: \((?P<dirHasDoor>(?:open|closed) door)\))?'
    
    rules = {
        r"<RNum (?P<rnum>\d+)>": "FoundRnum",
        r"<RName>(?P<rname>.*)</RName>": "FoundRname",
        r"<RDesc>(?P<descLine>[^<]*)(?P<closeTag></RDesc>)?": "FoundRdescOpen",
        r"^(.*</RDesc>\s*)?<RExits>(?P<exitsLine>.*\.)(?P<closeTag></*RExits>)?": "FoundRexitsOpen",
    }

    def __init__(self):
        RegexProcessor.__init__(self)

        self.logger = logging.getLogger("mud_proxy.MXPParser")

        # Compile exits regex
        self.exitsPattern = re.compile(self.REXITS_EXIT_REGEX)

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
            self.addRule(self.RDESC_BUFFER_REGEX, self.onRdescBuffer)

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
            self.removeRule(self.RDESC_BUFFER_REGEX)

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
            self.parseExits("".join(self.rexitsBuffer))
            del self.rexitsBuffer
        else:
            self.addRule(self.REXITS_BUFFER_REGEX, self.onRexitsBuffer)

    def onRexitsBuffer(self, match):
        self.logger.info("Buffering into RExits: %s" % match.groupdict()["exitsLine"])
        self.rexitsBuffer.append(match.groupdict()["exitsLine"])

        if match.groupdict().get("closeTag"):
            self.logger.info("Found RExits close, exits was:")
            self.logger.info("".join(self.rexitsBuffer))
            self.parseExits("".join(self.rexitsBuffer))

            del self.rexitsBuffer
            self.removeRule(self.REXITS_BUFFER_REGEX)

    def parseExits(self, exitsLine):
        exits = [match.groupdict() for match in self.exitsPattern.finditer(exitsLine)]

        self.logger.info("Parsed exit info: %s" % exits)
