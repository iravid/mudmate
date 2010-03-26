class EventBus(object):
    class _EventBusImpl(object):
        def __init__(self):
            self.subscribers = []

        def subscribe(self, subscriber):
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)

        def publish(self, event):
            for subscriber in self.subscribers:
                subscriber.handle(event)

    instance = _EventBusImpl()

    def __init__(self):
        raise NotImplementedError()
