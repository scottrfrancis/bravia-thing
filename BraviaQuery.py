from braviarc import BraviaRC


class BraviaQuery:
    def __init__(self, ip, psk):
        self.ip = ip
        self.psk = psk
        self.mac = 'AA:BB:CC:DD:EE:FF'

        self.bravia = BraviaRC(self.ip, self.psk, self.mac)
    
    def poll(self):
        power_status = self.bravia.get_power_status()
        led_status = 'off' if (self.bravia.get_led_status() == 'SimpleResponse') else 'on'

        return {    'Power': power_status(),
                    'LED': led_status }

    def setMute(self, isOn):
        mode = "Demo" if str(isOn).lower() == "on" else "SimpleResponse"
        print("setting LED to " + str(str(isOn).lower() == "on").lower() + " with mode " + mode)
        self.bravia.set_led_status(mode, str(str(isOn).lower() == "on").lower())

        print("setting AudioMute OSD with " + str(str(isOn).lower() == "on"))
        self.bravia.set_audio_mute(str(isOn).lower() == "on")

    def setVolume(self, level):
        print("setting volume to " + str(level))
        self.bravia.set_volume_level(level/100)
        
