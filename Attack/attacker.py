class Attacker:
    '''
    Initializes Attacker according the the info we get from running discovery
    '''
    def __init__(self, info):
        self.ip = info[0]
        self.mac = info[1]

        
    def toString(self):
        return "{P}Attacker IP: {W}" + self.ip + "{P}; MAC: {W}" + self.mac
