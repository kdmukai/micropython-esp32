
"""
"""
import lvgl as lv
import ili9XXX
from ili9XXX import st7789
import machine
import time

# see pin_defs.py and import the pin defs that match your build
from pin_defs import dev_board as pins
# from pin_defs import manual_wiring as pins
import fs_driver

lv.init()

# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

# Load the font
opensans_regular_17 = lv.font_load("S:/opensans_regular_17.bin")

disp = st7789(
    **pins["st7789"],
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

key1 = machine.Pin(pins["buttons"]["key1"], machine.Pin.IN, machine.Pin.PULL_UP)
key2 = machine.Pin(pins["buttons"]["key2"], machine.Pin.IN, machine.Pin.PULL_UP)
key3 = machine.Pin(pins["buttons"]["key3"], machine.Pin.IN, machine.Pin.PULL_UP)

joy_up = machine.Pin(pins["buttons"]["joy_up"], machine.Pin.IN, machine.Pin.PULL_UP)
joy_down = machine.Pin(pins["buttons"]["joy_down"], machine.Pin.IN, machine.Pin.PULL_UP)
joy_left = machine.Pin(pins["buttons"]["joy_left"], machine.Pin.IN, machine.Pin.PULL_UP)
joy_right = machine.Pin(pins["buttons"]["joy_right"], machine.Pin.IN, machine.Pin.PULL_UP)
joy_press = machine.Pin(pins["buttons"]["joy_press"], machine.Pin.IN, machine.Pin.PULL_UP)

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

