"""
    From: https://forum.lvgl.io/t/buttons-not-working-as-encoder/8692/3
"""
from input import DigitalInput


class Button:
    def __init__(self, pin, id, key, user_callback=None):
        self._press = False
        self._changed = False
        self._id = id
        self._key = key
        self._user_callback = user_callback
        self.setPin(pin)

    def _cb(self, pin, press):
        if self._press != press:
            print("State change [{}] {}->{} [{}]".format(pin, self._press, press, self._key))
            self._changed = True
            self._press = press
            return self._user_callback(self)

    @property
    def pressed(self):
        return self._press

    @property
    def changed(self):
        ch = self._changed
        self._changed = False
        return ch

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return self._key

    def setPin(self, pin):
        # DigitalIput : the class that monitors/debounces pin. Uses an irq internally
        # see : https://github.com/tuupola/micropython-m5stack/blob/master/firmware/lib/input.py
        # Can be replaced with an explicit irq on the pin object.
        self._input = DigitalInput(pin, self._cb)