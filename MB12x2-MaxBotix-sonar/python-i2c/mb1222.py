
import time
import Jetson.GPIO as GPIO
import smbus2


class MB1222:
    def __init__(self, busnum, addr, irqpin):
        self._bus = smbus2.SMBus(busnum)
        self._chipAddr = addr
        self._irqpin = irqpin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(irqpin, GPIO.IN)

    def get_distance(self):
        if GPIO.input(self._irqpin) == 1:  # sensor is busy
            return  # try again later
        try:
            self._bus.write_byte(self._chipAddr, 81)  # command a range reading
        except OSError as oee:  # (electrical glitch on the i2c bus?)
            print('OSError:', oee)
            return  # try again later

        # Pin goes hi when busy, goes low when ready
        GPIO.wait_for_edge(self._irqpin, GPIO.FALLING, timeout=500)

        pkt = self._bus.read_i2c_block_data(self._chipAddr, 0, 2)
        dist = pkt[0] << 8 | pkt[1]

        return dist


if __name__ == '__main__':
    sonar = MB1222(1, 0x71, 26)
    #sonar = MB1222(1, 0x72, 19)

    while True:
        dst = sonar.get_distance()
        print(dst)
        time.sleep(0.01)


