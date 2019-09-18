from braviarc import BraviaRC


class BraviaQuery:
    def __init__(self, ip, psk):
        self.ip = ip
        self.psk = psk
        self.mac = 'AA:BB:CC:DD:EE:FF'

        self.bravia = BraviaRC(self.ip, self.psk, self.mac)
    
    def poll(self):
        led_status = 'off' if (self.bravia.get_led_status() == 'SimpleResponse') else 'on'

        return { 'Power': self.bravia.get_power_status(),
                  'LED': led_status }
        
