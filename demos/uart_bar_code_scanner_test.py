import time
from machine import UART

"""
Lightly adapted from:
https://github.com/cryptoadvance/specter-diy/blob/1790c2cad3ecda3dbc3921fe574346591b85701b/src/hosts/qr.py

Tests just the bar code reader module UART connection to the mcu.
"""

# OK response from scanner
SUCCESS = b"\x02\x00\x00\x01\x00\x33\x31"

# serial port mode
SERIAL_ADDR = b"\x00\x0D"

""" We switch the scanner to continuous mode to initiate scanning and
to command mode to stop scanning. No external trigger is necessary """
SETTINGS_ADDR = b"\x00\x00"

""" After basic scanner configuration (9600 bps) uart is set to 115200 bps
to support fast scanning of animated qrs """
BAUD_RATE_ADDR = b"\x00\x2A"
BAUD_RATE = b"\x1A\x00"  # 115200

# commands
SCAN_ADDR = b"\x00\x02"
# timeout
TIMOUT_ADDR = b"\x00\x06"

""" After the scanner obtains a scan it waits 100ms and starts a new scan."""
INTERVAL_OF_SCANNING_ADDR = b"\x00\x05"
INTERVAL_OF_SCANNING = 0x01  # 100ms

""" DELAY_OF_SAME_BARCODES of 5 seconds means scanning the same barcode again
(and sending it over uart) can happen only when the interval times out or resets
which happens if we scan a different qr code. """
DELAY_OF_SAME_BARCODES_ADDR = b"\x00\x13"
DELAY_OF_SAME_BARCODES = 0x85  # 5 seconds


class QRHost:
    def __init__(self):
        print("__init__")
        self.uart = UART(1)
        print("Instantiated UART")

        self.init_uart()

    def init_uart(self, baudrate=9600):
        print("starting init_uart")
        # self.uart.init(baudrate=baudrate, bits=8, parity=None, stop=1, rx=35, tx=36)
        self.uart.init(baudrate=baudrate, bits=8, parity=None, stop=1, rx=18, tx=17)
        print(f"init_uart({baudrate}) complete")

    @property
    def MASK(self):
        b = (1<<7)
        # if self.settings.get("sound", True):
        #     b |= (1<<6)
        # if self.settings.get("aim", True):
        #     b |= (1<<4)
        # if self.settings.get("light", False):
        #     b |= (1<<2)

        # if self.settings.get("sound", True):
        b |= (1<<6)
        # if self.settings.get("aim", True):
        b |= (1<<4)
        # if self.settings.get("light", False):
        # b |= (1<<2)
        return b

    @property
    def CMD_MODE(self):
        return self.MASK | 1

    @property
    def CONT_MODE(self):
        return self.MASK | 2

    def query(self, data, timeout=100):
        """Blocking query"""
        self.uart.write(data)
        t0 = time.time()
        while self.uart.any() < 7:
            time.sleep_ms(10)
            t = time.time()
            if t > t0 + timeout / 1000:
                return None
        res = self.uart.read(7)
        return res

    def get_setting(self, addr):
        # only for 1 byte settings
        res = self.query(b"\x7E\x00\x07\x01" + addr + b"\x01\xAB\xCD")
        if res is None or len(res) != 7:
            return None
        return res[-3]

    def set_setting(self, addr, value):
        # only for 1 byte settings
        res = self.query(b"\x7E\x00\x08\x01" + addr + bytes([value]) + b"\xAB\xCD")
        if res is None:
            return False
        return res == SUCCESS

    def save_settings_on_scanner(self):
        res = self.query(b"\x7E\x00\x09\x01\x00\x00\x00\xDE\xC8")
        if res is None:
            return False
        return res == SUCCESS

    def configure(self):
        """Tries to configure scanner, returns True on success"""

        self.uart.read()

        save_required = False
        val = self.get_setting(SERIAL_ADDR)
        if val is None:
            print(f"get_setting(SERIAL_ADDR) is None")
            return False
        if val & 0x3 != 0:
            self.set_setting(SERIAL_ADDR, val & 0xFC)
            save_required = True

        val = self.get_setting(SETTINGS_ADDR)
        if val is None:
            print(f"get_setting(SETTINGS_ADDR) is None")
            return False
        if val != self.CMD_MODE:
            self.set_setting(SETTINGS_ADDR, self.CONT_MODE)
            save_required = True

        val = self.get_setting(TIMOUT_ADDR)
        if val is None:
            print(f"get_setting(TIMOUT_ADDR) is None")
            return False
        if val != 0:
            self.set_setting(TIMOUT_ADDR, 0)
            save_required = True

        val = self.get_setting(INTERVAL_OF_SCANNING_ADDR)
        if val is None:
            print(f"get_setting(INTERVAL_OF_SCANNING_ADDR) is None")
            return False
        if val != INTERVAL_OF_SCANNING:
            self.set_setting(INTERVAL_OF_SCANNING_ADDR, INTERVAL_OF_SCANNING)
            save_required = True

        val = self.get_setting(DELAY_OF_SAME_BARCODES_ADDR)
        if val is None:
            print(f"get_setting(DELAY_OF_SAME_BARCODES_ADDR) is None")
            return False
        if val != DELAY_OF_SAME_BARCODES:
            self.set_setting(DELAY_OF_SAME_BARCODES_ADDR, DELAY_OF_SAME_BARCODES)
            save_required = True

        # if save_required:
        #     val = self.save_settings_on_scanner()
        #     if not val:
        #         print("save_settings_on_scanner FAILED!")
        #         return False

        # # Set 115200 bps: this query is special - it has a payload of 2 bytes
        # ret = self.query(b"\x7E\x00\x08\x02" + BAUD_RATE_ADDR + BAUD_RATE + b"\xAB\xCD")
        # if ret != SUCCESS:
        #     print("setting BAUD_RATE FAILED!")
        #     return False
        # self.uart.deinit()
        # self.init_uart(baudrate=115200)
        # return True


scanner = QRHost()
print("Instantiated QRHost")

scanner.configure()
print("finished configure()")

while True:
    if scanner.uart.any() > 0:
        data = scanner.uart.read()
        if data:
            try:
                print(data.decode())
            except:
                print(data)
