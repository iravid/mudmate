import logging

class EventBus(object):
    class _EventBusImpl(object):
        def __init__(self):
            self.subscribers = []
            self.logger = logging.getLogger("mud_proxy.EventBus")

        def subscribe(self, subscriber):
            self.logger.debug("%s subscribing" % subscriber.__class__.__name__)
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)

        def publish(self, event):
            self.logger.debug("%s being published with data:\n%s" % (event.name, event.data))

            for subscriber in self.subscribers:
                self.logger.debug("Asking %s to handle %s" % (subscriber.__class__.__name__, event.name))
                subscriber.handle(event)

    instance = _EventBusImpl()

    def __init__(self):
        raise NotImplementedError()
