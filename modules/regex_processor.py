import logging
import re

from events.subscriber import Subscriber
from events.event import Event
from events.event_bus import EventBus

class RegexProcessor(Subscriber):
    rules = {
    }

    def __init__(self):
        self.logger = logging.getLogger("mud_proxy.RegexProcessor")

        # Replace string function names with actual function objects
        for pattern, handlerName in self.rules.items():
            self.rules[pattern] = getattr(self, "on%s" % handlerName)

        # Rule removal/addition queues
        self.installLater = []
        self.removeLater = []

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

        # Since we don't want the rules list to mutate during a parsing pass, we schedule
        # the addition/removal of new rules in self.installLater and self.removeLater and
        # perform the appropriate action after we finish parsing.
        for regex, handler in self.installLater:
            if self.rules.get(regex):
                self.logger.warning("Yikes! The regex I'm installing already exists...")

            self.rules[regex] = handler

        self.installLater = []

        for regex in self.removeLater:
            if not self.rules.get(regex):
                self.logger.warning("Yikes! The regex I'm removing doesn't exist...")

            self.rules.pop(regex, None)

        self.removeLater = []

        return responses

    def addRule(self, regex, handler):
        """
        Add a rule to the processor, to be matched by regex and handled by handler.

        Rules will be added once the current parsing run finishes.
        """
        self.installLater.append((regex, handler))

    def removeRule(self, regex):
        """
        Remove a rule matched by regex.

        Rules will be removed once the current parsing run finishes.
        """
        self.removeLater.append(regex)
