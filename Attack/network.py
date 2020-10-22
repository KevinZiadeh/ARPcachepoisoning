class Network:
    '''
    Initializes Network according the the info we get from running discovery
    '''

    def __init__(self, info):
        self.ip = info[0]
        self.mac = info[1]
        self.broadcastIP = info[2]

    def toString(self):
        return " {P}Router IP: {W}" + self.ip + "{P}; MAC: {W}" + self.mac + "{P}; BroadcastIP: {W}" + self.broadcastIP