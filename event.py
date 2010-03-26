class Event(object):
    def __init__(self, data=None):
        self.data = data

class ControlConnectionReceived(Event):
    pass

class ControlConnectionLost(Event):
    pass

class ControlDataReceived(Event):
    pass

class MUDDataReceived(Event):
    pass

class TriggerDataGenerated(Event):
    pass
