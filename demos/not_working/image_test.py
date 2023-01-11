"""
    see: https://lvgl.github.io/lv_img_conv/

    DOES NOT WORK YET!!
"""
import lvgl as lv
import ili9XXX
from ili9XXX import st7789
import machine
import os
import time


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

# scr = lv.scr_act()
# scr.clean()

# scr.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
# scr.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)



img1 = lv.img(lv.scr_act())
img1.set_size(240, 51)
img1.align(lv.ALIGN.CENTER, 0, 0)


# Create an image from the rgb565 bin file
with open('bitcoin_magazine_logo_240.bin','rb') as f:
    img_data = f.read()

print(f"read the logo data: {len(img_data)}")

logo = lv.img_dsc_t({
    'header': {
        'always_zero': 0,
        'w': 240,
        'h': 51,
    },
    'data_size': len(img_data),
    'data': img_data
})
img1.set_src(logo)

print("created img obj")

time.sleep(10)
