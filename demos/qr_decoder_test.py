"""
Test the QR decoder on its own.

Hardware requirements: 
"""

import machine
import time
import quirc

machine.freq(240000000)

with open("qr_test_image_2.bin", 'rb') as f:
    img_bytes = f.read()

print(f"img_bytes: {len(img_bytes)} bytes")

# # Try swapping the row and cols in the byte array
# gray_width = 120
# gray_height = 120
# src_row_span = gray_height
# swapped_bytes = bytearray([0]*120*120)
# print(len(swapped_bytes))
# for y in range(0, gray_width):
#     for x in range(0, gray_height):
#         pixel = img_bytes[(y * src_row_span) + x]
#         dest_y = gray_height - x
#         dest_x = y
#         # print(f"x: {x} | y: {y} | dest_x: {dest_x} | dest_y: {dest_y} | {dest_y * gray_width + dest_x}")
#         swapped_bytes[dest_y * gray_width + dest_x] = pixel 

# def ascii_print(img):
#     buf = ""
#     for x in range(0, 120):
#         for y in range(0, 120):
#             pixel = img[y*120 + x]
#             if pixel == 0:
#                 buf += "  "
#             else:
#                 buf += "X "
#         buf += "\n"
#     print(buf)

# ascii_print(img_bytes)

# gray_width = 120
# gray_height = 120
# swapped_bytes = bytearray([0]*120*120)
# for x in range(0, gray_width):
#     for y in range(0, gray_height):
#         pixel = img_bytes[y*gray_width + x]
#         swapped_bytes[x*gray_height + y] = pixel

# ascii_print(swapped_bytes)

# with open("qr_test_image_transformed.bin", 'wb') as f:
#     f.write(swapped_bytes)

quirc.init(120, 120)
print("init complete")

start = time.ticks_ms()
quirc.load_framebuffer(img_bytes)
print(f"{time.ticks_ms() - start}ms")

# result = quirc.scan()
# print(f"quirc result: {result}")
