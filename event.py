class ControlConnectionReceived(object):
    def __init__(self, connectionInput):
        self.connectionInput = connectionInput

class ControlConnectionLost(object):
    pass

class ControlDataReceived(object):
    def __init__(self, data):
        self.data = data

class MUDDataReceived(object):
    def __init__(self, data):
        self.data = data
