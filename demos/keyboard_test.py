"""
    From: https://forum.lvgl.io/t/buttons-not-working-as-encoder/8692/3
"""
import lvgl as lv
import ili9XXX
from ili9XXX import st7789
from utils import Button
import fs_driver
import hashlib
from machine import Pin
import os
import time


encoder_state = {'left': 0, 'right': 0, 'pressed': False}

def on_press_left(btn):
    if btn.pressed:
        encoder_state['left'] += 1
        print('on_press_left')


def on_press_center_click(btn):
    encoder_state['pressed'] = btn.pressed
    print('on_press_center_click')


def on_press_right(btn):
    if btn.pressed:
        encoder_state['right'] += 1
        print('on_press_right')

def button_read_constr():
    def button_read(drv, data):
        data.enc_diff = encoder_state['right'] - encoder_state['left']
        encoder_state['right'] = 0
        encoder_state['left'] = 0
        if encoder_state['pressed']:
            data.state = lv.INDEV_STATE.PRESSED
            encoder_state['pressed'] = False
        else:
            data.state = lv.INDEV_STATE.RELEASED
        # gc.collect()
        return False
    return button_read


lv.init()

"""
    Pinouts for different boards:

    ESP32-S3-DevKitC-1:
        FSPID (11) = MOSI
        mosi=11, clk=12, cs=10, dc=4, rst=5,

    Unexpected Maker FeatherS3:
        mosi=12, clk=6, cs=17, dc=14, rst=18,

    Saola-1R:
        mosi=11, clk=12, cs=10, dc=1, rst=2,
"""
disp = st7789(
    mosi=11, clk=12, cs=10, dc=1, rst=2,
    width=240, height=240, rot=ili9XXX.LANDSCAPE
)

scr = lv.scr_act()
scr.clean()


joy_right = Button(Pin(15), id=1, key=lv.KEY.UP, user_callback=on_press_right)
joy_press = Button(Pin(17), id=2, key=lv.KEY.ENTER, user_callback=on_press_center_click)
joy_left = Button(Pin(16), id=3, key=lv.KEY.DOWN, user_callback=on_press_left)

read_button = button_read_constr(joy_right, joy_press, joy_left)

indev_drv = lv.indev_drv_t()
indev_drv.type = lv.INDEV_TYPE.ENCODER
indev_drv.read_cb = read_button

win_drv = indev_drv.register()

# Create a keyboard to use it with one of the text areas
kb = lv.keyboard(lv.scr_act())

# Create a text area. The keyboard will write here
ta = lv.textarea(lv.scr_act())
ta.set_width(220)
ta.align(lv.ALIGN.TOP_LEFT, 10, 10)
ta.add_event_cb(lambda e: ta_event_cb(e,kb), lv.EVENT.ALL, None)
# ta.set_placeholder_text("Hello")


# ta = lv.textarea(lv.scr_act())
# ta.set_width(200)
# ta.align(lv.ALIGN.TOP_RIGHT, -10, 10)
# ta.add_event_cb(lambda e: ta_event_cb(e,kb), lv.EVENT.ALL, None)

kb.set_textarea(ta)


group = lv.group_create()
group.add_obj(kb)

win_drv.set_group(group)

