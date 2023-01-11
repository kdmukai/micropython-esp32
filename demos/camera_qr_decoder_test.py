
import lvgl as lv
import camera
import ili9XXX
from ili9XXX import st7789
import fs_driver
import time
import quirc


lv.init()

# see pin_defs.py and import the pin defs that match your build
from pin_defs import dev_board as pins
# from pin_defs import manual_wiring as pins


# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
opensans_semibold_20 = lv.font_load("S:/opensans_semibold_20.bin")

disp = st7789(
    **pins["st7789"],
    width=240, height=240, rot=ili9XXX.LANDSCAPE
)

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
img1.set_size(240, 240)
img1.align(lv.ALIGN.CENTER, 0, 0)


# Saola-1R wiring
# sioc = SCL; siod = SDA
"""
framesizes:
    FRAME_240X240
    FRAME_96X96
    FRAME_CIF
    FRAME_FHD
    FRAME_HD
    FRAME_HQVGA
    FRAME_HVGA
    FRAME_P_3MP
    FRAME_P_FHD
    FRAME_P_HD
    FRAME_QCIF
    FRAME_QHD
    FRAME_QQVGA
    FRAME_QSXGA
    FRAME_QVGA
    FRAME_QXGA
    FRAME_SVGA
    FRAME_SXGA
    FRAME_UXGA
    FRAME_VGA
    FRAME_WQXGA
    FRAME_XGA

formats:
    GRAYSCALE
    JPEG
    RGB565
    YUV422
"""
camera.init(
    0,
    **pins["camera"],
    # format=camera.JPEG,
    # format=camera.RGB565,
    format=camera.GRAYSCALE,
    framesize=camera.FRAME_240X240,
    fb_location=camera.PSRAM,
    xclk_freq=camera.XCLK_10MHz,
)

camera.brightness(1)
camera.mirror(1)
camera.flip(1)
camera.saturation(2)
camera.contrast(2)

quirc.init(240, 240)

i = 0
while True:
    # start = time.ticks_ms()
    # result = camera.scan_qr()
    # print(result)
    # print(f"{time.ticks_ms() - start:3} ms")


    buf = camera.capture()
    if buf:

        # resized = bytearray()
        # for y in range(0, 240, 2):
        #     for x in range(0, 240, 2):
        #         pixel = (int)((buf[y*240 + x] + buf[y*240 + x+1] + buf[(y+1)*240 + x] + buf[(y+1)*240 + x+1])/4)
        #         resized.append(pixel)
        # print(len(resized))

        # print(f"{i}: {len(buf)} bytes")
        start = time.ticks_ms()
        quirc.load_framebuffer(buf)
        print(f"{i:4}: {time.ticks_ms() - start:3} ms")

        # if i == 50:
        #     with open("image_dump.bin", 'wb') as f:
        #         f.write(buf)
        #     print(len(quirc.framebuffer))
        #     break

        image_data = lv.img_dsc_t({
            'header': {
                'always_zero': 0,
                # 'w': 240,
                # 'h': 240,
            },
            'data_size': len(buf),
            'data': buf
        })
        img1.set_src(image_data)

        i += 1
    else:
        print("NO DATA")

# while True:
#     # result = camera.scan_qr()
#     result = camera.capture()
#     if type(result) == str or type(result) == bool:
#         print(result)
    
#     else:
#         buf = result
#         # buf = camera.capture()
#         print(f"{i:5}: {len(buf)} bytes")
#         if buf:
#             image_data = lv.img_dsc_t({
#                 'header': {
#                     'always_zero': 0,
#                     'w': 240,
#                     'h': 240,
#                     'cf': lv.img.CF.RGB565,
#                 },
#                 'data_size': len(buf),
#                 'data': buf,
#             })
#             img1.set_src(image_data)
#             i += 1

#             # if i == 50:
#             #     print(buf)
#             #     break
#         else:
#             print("NO DATA")




"""
camera RGB565 + CF.RGB565 == "No data" on display
camera RGB565 + CF.TRUE_COLOR (DLV_COLOR_16_SWAP=1) == image w/mis-coded color
camera RGB565 + CF.TRUE_COLOR (DLV_COLOR_16_SWAP=0) == better, but still lots of mis-coding and tearing

camera JPEG + (none) == success
camera JPEG + CF.TRUE_COLOR == success
camera JPEG + CF.RGB565 == success

camera GRAYSCALE + CF.INDEXED_8BIT == garbled

lv.img.CF:
    ALPHA_1BIT
    ALPHA_2BIT
    ALPHA_4BIT
    ALPHA_8BIT
    INDEXED_1BIT
    INDEXED_2BIT
    INDEXED_4BIT
    INDEXED_8BIT
    RAW
    RAW_ALPHA
    RAW_CHROMA_KEYED
    RESERVED_15
    RESERVED_16
    RESERVED_17
    RESERVED_18
    RESERVED_19
    RESERVED_20
    RESERVED_21
    RESERVED_22
    RESERVED_23
    RGB565
    RGB565A8
    RGB888
    RGBA5658
    RGBA8888
    RGBX8888
    TRUE_COLOR
    TRUE_COLOR_ALPHA
    TRUE_COLOR_CHROMA_KEYED
    UNKNOWN
    USER_ENCODED_0
    USER_ENCODED_1
    USER_ENCODED_2
    USER_ENCODED_3
    USER_ENCODED_4
    USER_ENCODED_5
    USER_ENCODED_6
    USER_ENCODED_7
"""