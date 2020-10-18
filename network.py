class Network:
    '''
    Initializes Network according the the info we get from running discovery
    '''

    def __init__(self, info):
        self.ip = info[0]
        self.mac = info[1]
        self.broadcastIP = info[2]

    def toString(self):
        return "Router IP: " + self.ip + "; MAC: " + self.mac + "; BroadcastIP: " + self.broadcastIP