import time
import lvgl as lv
import ili9XXX
from ili9XXX import st7789

# see pin_defs.py and import the pin defs that match your build
from pin_defs import dev_board as pins
# from pin_defs import manual_wiring as pins



import fs_driver
# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

FONT__OPEN_SANS__REGULAR__17 = lv.font_load("S:/opensans_regular_17.bin")
FONT__OPEN_SANS__SEMIBOLD__20 = lv.font_load("S:/opensans_semibold_20.bin")


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
    
# Black out the background
# TODO: set the bg color on the scr obj?
"""
bg = lv.obj(lv.scr_act())
bg.set_size(240, 240)
bg.align(lv.ALIGN.TOP_LEFT, 0, 0)
style = lv.style_t()
style.set_bg_color(lv.color_hex(0x000))
style.set_border_width(0)
style.set_radius(0)
bg.add_style(style, 0)
"""

### Top Nav ###
top_nav = lv.obj(scr)
top_nav.set_size(240, 48)
top_nav.align(lv.ALIGN.TOP_LEFT, 0, 0)

style = lv.style_t()
style.init()
style.set_pad_all(0)
style.set_border_width(0)
style.set_radius(0)
style.set_bg_color(lv.color_hex(0x000000))
top_nav.add_style(style, 0)

label = lv.label(top_nav)
label.set_text("Settings")
label.center()
label_style = lv.style_t()
label_style.set_text_font(FONT__OPEN_SANS__SEMIBOLD__20)
label_style.set_text_color(lv.color_hex(0xffffff))
label.add_style(label_style, 0)


### Button List ###
cont_col = lv.obj(scr)
cont_col.set_size(240, 240 - top_nav.get_height() - 48)
cont_col.align_to(top_nav, lv.ALIGN.OUT_BOTTOM_MID, 0, 0)
cont_col.set_flex_flow(lv.FLEX_FLOW.COLUMN)

# Set the scroll snap point to land scroll target at center
cont_col.set_scroll_snap_y(lv.SCROLL_SNAP.CENTER)
cont_col.add_flag(lv.obj.FLAG.SCROLL_ONE)
cont_col.set_scroll_dir(lv.DIR.VER)
cont_col.update_snap(lv.ANIM.ON)

style = lv.style_t()
style.set_bg_color(lv.color_hex(0x000))
style.set_border_width(1)
style.set_border_color(lv.color_hex(0xff0000))
style.set_radius(0)
style.set_pad_column(0)
cont_col.add_style(style, 0)

buttons = []
for i in range(10):
    # Add items to the column
    obj = lv.btn(cont_col)
    obj.set_size(240 - 2*EDGE_PADDING, 32)
    obj.add_flag(lv.obj.FLAG.SNAPPABLE)
    obj.center()
    buttons.append(obj)

    style = lv.style_t()
    style.set_bg_color(lv.color_hex(0x2c2c2c))
    style.set_pad_all(0)
    style.set_text_font(FONT__OPEN_SANS__REGULAR__17)
    obj.add_style(style, 0)

    label = lv.label(obj)
    label.set_text("Item: {:d}".format(i))
    label.center()
    
    if i == 0:
        style = lv.style_t()
        style.set_text_color(lv.color_hex(0x0))
        label.add_style(style, 0)


for button in buttons:
    button.set_style_bg_color(lv.color_hex(0xffa500), 0)
    button.get_child(0).set_style_text_color(lv.color_hex(0x0), 0)
    cont_col.scroll_to_y(button.get_y(), lv.ANIM.ON)
    time.sleep_ms(1000)
    button.set_style_bg_color(lv.color_hex(0x2c2c2c), 0)
    button.get_child(0).set_style_text_color(lv.color_hex(0xffffff), 0)

