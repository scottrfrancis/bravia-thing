from braviarc import BraviaRC


class BraviaQuery:
    def __init__(self, ip, psk):
        self.ip = ip
        self.psk = psk
        self.mac = 'AA:BB:CC:DD:EE:FF'

        self.bravia = BraviaRC(self.ip, self.psk, self.mac)
    
    def poll(self):
        return { 'Power': self.bravia.get_power_status() }
        
