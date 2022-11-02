
"""
"""
import lvgl as lv
import ili9XXX
from ili9XXX import st7789
import machine
import time

import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

try:
    script_path = __file__[:__file__.rfind('/')] if __file__.find('/') >= 0 else '.'
except NameError:
    script_path = ''

import fs_driver

lv.init()

# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

# Load the font
opensans_regular_17 = lv.font_load("S:%s/opensans_regular_17.bin" % script_path)

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
    # mosi=11, clk=12, cs=10, dc=1, rst=2,  # kit build
    mosi=11, clk=12, cs=10, dc=13, rst=14,    # custom dev pcb
    width=240, height=240, rot=ili9XXX.LANDSCAPE
)

scr = lv.scr_act()
scr.clean()

scr.set_style_bg_color(lv.color_hex(0x000000), 0)
scr.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

EDGE_PADDING = 8
COMPONENT_PADDING = 8

### Top Nav ###
top_nav = lv.obj(scr)
top_nav.set_size(240, 48)
top_nav.align(lv.ALIGN.TOP_LEFT, 0, 0)

style = lv.style_t()
style.init()
style.set_pad_all(0)
style.set_border_width(0)
style.set_radius(0)
style.set_bg_color(lv.color_hex(0x0000ff))
top_nav.add_style(style, 0)

label = lv.label(top_nav)
label.set_text("Settings")
label.center()
label_style = lv.style_t()
label_style.set_text_font(opensans_regular_17)
label_style.set_text_color(lv.color_hex(0xffffff))
label.add_style(label_style, 0)

obj = lv.btn(scr)
obj.set_size(240 - 2*EDGE_PADDING, 32)
obj.add_flag(lv.obj.FLAG.SNAPPABLE)
obj.center()

style = lv.style_t()
style.set_bg_color(lv.color_hex(0xffa500))
style.set_text_color(lv.color_hex(0x000000))
style.set_pad_all(0)
obj.add_style(style, 0)

label = lv.label(obj)
label.set_text("")
label.center()

# kit build
# key1 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
# key2 = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP)
# key3 = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)
# joy_up = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
# joy_down = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
# joy_left = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
# joy_right = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
# joy_press = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)

# custom dev pcb
key1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
key2 = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
key3 = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
joy_up = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)
joy_down = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
joy_left = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP)
joy_right = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
joy_press = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

buttons = [
    (key1, "KEY1"),
    (key2, "KEY2"),
    (key3, "KEY3"),
    (joy_up, "UP"),
    (joy_down, "DOWN"),
    (joy_left, "LEFT"),
    (joy_right, "RIGHT"),
    (joy_press, "PRESS"),
]

cur_button = None

while True:
    for button, btn_name in buttons:
        if cur_button != button:
            if button.value() == 0:
                cur_button = button
                label.set_text(btn_name)
                break
        if cur_button == button and button.value() == 1:
            cur_button = None
    time.sleep(0.01)

