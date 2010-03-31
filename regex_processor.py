import re

from subscriber import Subscriber
from event import Event
from event_bus import EventBus

class RegexProcessor(Subscriber):
    rules = {
        "Enter an option or your character\'s name\.": "Username"
    }

    def __init__(self):
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
            match = re.match(pattern, data)

            if match:
                response = handler(match)

                if response:
                    responses.append(response)

        return responses

    def onUsername(self, match):
        print "Matched! Sending Riaan"

        return "Riaan\n"
