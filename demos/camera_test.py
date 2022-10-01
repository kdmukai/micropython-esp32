
import lvgl as lv
import camera
import ili9XXX
from ili9XXX import st7789
import fs_driver

import time

lv.init()

time.sleep(0.1)

# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
opensans_semibold_20 = lv.font_load("S:/opensans_semibold_20.bin")

disp = st7789(
    mosi=11, clk=12, cs=10, dc=1, rst=2,
    width=240, height=240, rot=ili9XXX.LANDSCAPE
)

time.sleep(0.1)

scr = lv.scr_act()
scr.clean()

scr.set_style_bg_color(lv.color_hex(0x000000), 0)
scr.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

### Top Nav ###
top_nav = lv.obj(scr)
top_nav.set_size(240, 48)
top_nav.align(lv.ALIGN.TOP_LEFT, 0, 0)
top_nav.set_style_bg_color(lv.color_hex(0x000000), 0)

style = lv.style_t()
style.init()
style.set_pad_all(0)
style.set_border_width(0)
style.set_radius(0)
top_nav.add_style(style, 0)

label = lv.label(top_nav)
label.center()
label.set_style_text_font(opensans_semibold_20, 0)
label.set_style_text_color(lv.color_hex(0xf8f8f8), 0)
label.set_text("Camera Test")


img1 = lv.img(scr)
img1.set_size(240, 192)
img1.align(lv.ALIGN.CENTER, 0, 24)

img_label_shadow = lv.label(scr)
img_label_shadow.center()
img_label_shadow.set_style_text_font(opensans_semibold_20, 0)
img_label_shadow.align(lv.ALIGN.BOTTOM_MID, 2, 2)
img_label_shadow.set_style_text_color(lv.color_hex(0x333333), 0)
img_label_shadow.set_text("< cancel  |  proceed >")

img_label = lv.label(scr)
img_label.center()
img_label.set_style_text_font(opensans_semibold_20, 0)
img_label.align(lv.ALIGN.BOTTOM_MID, 0, 0)
img_label.set_style_text_color(lv.color_hex(0xffa500), 0)
img_label.set_text("< cancel  |  proceed >")

# Let LVGL finish updating before starting the camera(?)
time.sleep(0.1)

# Saola-1R wiring
# sioc = SCL; siod = SDA
camera.init(
    0,
    format=camera.JPEG,
    framesize=camera.FRAME_240X240,
    fb_location=camera.PSRAM,
    xclk_freq=camera.XCLK_20MHz,
    sioc=9,  # SCL
    siod=8,  # SDA
    vsync=7, href=6,
    pclk=5, xclk=4,
    d6=41, d7=42,
    d4=39, d5=40,
    d2=37, d3=38,
    d0=35, d1=36,
    reset=-1, pwdn=-1,  # not connected
)

camera.brightness(1)
camera.mirror(1)
camera.flip(1)
camera.saturation(2)
camera.contrast(2)


try:
    i = 0
    while True:
        start = time.ticks_ms()
        buf = camera.capture()
        # print(f"{i}: {len(buf)}")
        if buf:
            image_data = lv.img_dsc_t({
                'header': {
                    'always_zero': 0,
                    'w': 240,
                    'h': 240,
                },
                'data_size': len(buf),
                'data': buf
            })
            img1.set_src(image_data)
            i += 1
            print(f"{time.ticks_ms() - start:3} ms")
        else:
            print("NO DATA")
finally:
    camera.deinit()

