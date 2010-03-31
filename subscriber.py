class Subscriber(object):
    def handle(self, event):
        event_name = event.name
        event_handler_name = "on%s" % event_name

        event_handler = getattr(self, event_handler_name, None)

        if event_handler:
            event_handler(event)
