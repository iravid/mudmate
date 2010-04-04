import logging
import re

from subscriber import Subscriber
from event import Event
from event_bus import EventBus

class RegexProcessor(Subscriber):
    rules = {
    }

    def __init__(self):
        self.logger = logging.getLogger("mud_proxy.RegexProcessor")

        for pattern, handlerName in self.rules.items():
            self.rules[pattern] = getattr(self, "on%s" % handlerName)

        EventBus.instance.subscribe(self)

    def onMUDDataReceived(self, event):
        responses = self.matchData(event.data)

        event = Event("TriggerDataGenerated", responses)

        EventBus.instance.publish(event)

    def matchData(self, data):
        responses = []

        for pattern, handler in self.rules.items():
            self.logger.debug("Trying to match %s against %s" % (data, pattern))
            match = re.search(pattern, data, re.MULTILINE)

            if match:
                response = handler(match)

                if response:
                    responses.append(response)

        return responses
