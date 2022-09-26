# MicroPython-esp32
Create a custom MicroPython firmware for an ESP32 board with `secp256k1` compiled in.

## Clone this repo and its dependencies
```bash
git clone https://github.com/kdmukai/micropython-esp32.git
cd micropython-esp32

# clone our various submodule dependencies
git submodule update --init

# And within lv_micropython, recursively clone the esixtyone fork of lv_bindings
cd deps/lv_micropython
git submodule update --init --recursive lib/lv_bindings

# Recursively clone secp256k1
cd ../../
git submodule update --init --recursive deps/usermods/secp256k1-embedded

# embit needs some parts trimmed out of it
rm -rf deps/embit/src/embit/liquid
rm -rf deps/embit/src/embit/util

# soft link embit inside lv_micropython
ln -s deps/embit/src/embit deps/lv_micropython/ports/esp32/modules/embit
```

## Create a python3 virtualenv and install dependencies
```
pip install -r requirements.txt
```


## Build and run the Docker container
```bash
docker-compose build
docker-compose up
```

Run the `container_bash.sh` script to get a shell prompt inside the container (you may need to edit the container's name in the script).


## Continue configuration within the container
```bash
# Compile the micropython cross compiler
make -C /code/deps/lv_micropython/mpy-cross

cd /code/deps/lv_micropython/ports/esp32
make submodules
```

### Configure board target for LVGL compatibility
The `boards/GENERIC_S2` sdkconfig has already been updated for LVGL compatibility. Edit the definition of any other S2 board by updating its `sdkconfig.board`:
```
CONFIG_ETH_ENABLED=n
CONFIG_ETH_USE_SPI_ETHERNET=n
```


### Compile the firmware for the target board
Now we can compile the custom firmware:
```bash
# Targeting the SAOLA_1R board
# Note: we build to a dir inside the container (instead of the shared /code dir) because otherwise
#   the compiler runs significantly slower.
make LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=SAOLA_1R BUILD=/root/build-saola_1r USER_C_MODULES=/code/deps/usermods/micropython.cmake
mkdir -p /code/build/saola_1r
cp build-generic_s2/bootloader/bootloader.bin /code/build/generic_s2/.
cp build-generic_s2/partition_table/partition-table.bin /code/build/generic_s2/.
cp build-generic_s2/micropython.bin /code/build/generic_s2/.
```

GENERIC_S3
```
make LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=GENERIC_S3 BUILD=/root/build-generic_s3 USER_C_MODULES=/code/deps/usermods/micropython.cmake
mkdir -p /code/generic_s3
cp /root/build-generic_s3/bootloader/bootloader.bin /code/generic_s3/.
cp /root/build-generic_s3/partition_table/partition-table.bin /code/generic_s3/.
cp /root/build-generic_s3/micropython.bin /code/generic_s3/.
```


S3-DEVKITC-1 (N8R8)
```
make LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=S3_DEVKITC_1_N8R8 BUILD=/root/build-s3_devkitc_1_n8r8 USER_C_MODULES=/code/deps/usermods/micropython.cmake
mkdir -p /code/build/s3_devkitc_1_n8r8
cp /root/build-s3_devkitc_1_n8r8/bootloader/bootloader.bin /code/build/s3_devkitc_1_n8r8/.
cp /root/build-s3_devkitc_1_n8r8/partition_table/partition-table.bin /code/build/s3_devkitc_1_n8r8/.
cp /root/build-s3_devkitc_1_n8r8/micropython.bin /code/build/s3_devkitc_1_n8r8/.
```


Steps for FeatherS3 (esp32-S3)
```bash
cp build-generic_s3_spiram/bootloader/bootloader.bin /code/feather_s3/.
cp build-generic_s3_spiram/partition_table/partition-table.bin /code/feather_s3/.
cp build-generic_s3_spiram/micropython.bin /code/feather_s3/.
```

Steps for Generic esp32 (WROOM, etc)
```bash
cp build-generic/bootloader/bootloader.bin /code/generic_esp32/.
cp build-generic/partition_table/partition-table.bin /code/generic_esp32/.
cp build-generic/micropython.bin /code/generic_esp32/.
```




## Write the firmware to the board
see: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html#esp32-intro

With Python 3.x on your local machine:
```bash
pip install esptool
```

Put the board into bootloader update mode:
* Press and hold BOOT
* Press RST and release
* Release BOOT

The board's port name should either be `tty.usbmodem01` or `cu.usbmodem01` (older(?) macOS). Confirm with:
```
ls /dev
```

Write in the new firmware; the `write_flash` command is copied from the `idf.py` guidance above when compilation is completed.
```bash
esptool.py -p /dev/tty.usbmodem01 erase_flash
esptool.py -p /dev/tty.usbmodem01 -b 460800 --before default_reset --chip esp32s2  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```

### S3-DevKitC-1 (N8R8)
```bash
esptool.py -p /dev/tty.usbmodem1101 erase_flash
esptool.py -p /dev/tty.usbmodem1101 -b 460800 --before default_reset --after no_reset --chip esp32s3  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```


### FeatherS3 (esp32-S3)
```
esptool.py --port /dev/tty.usbmodem1101 erase_flash
esptool.py -p /dev/tty.usbmodem1101 -b 460800 --before default_reset --chip esp32s3  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```

### Generic ESP-32 (WROOM, etc)
* Press and hold 100
* Press EN and release
* Release 100
```
esptool.py --port /dev/tty.usbserial-0001 erase_flash
esptool.py -p /dev/tty.usbserial-0001 -b 460800 --before default_reset --chip esp32s3  write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```

Once it's complete, press RST to reset the board to normal operations. It will remount itself with a different name (e.g. `/dev/tty.usbmodem1234561`).


## Interact with the board

### `ampy`
Install the `ampy` tool:
```bash
pip install adafruit-ampy
```

```bash
# List the files on the board
ampy -p /dev/tty.usbmodem1234561 ls

# Transfer a file
ampy -p /dev/tty.usbmodem1234561 put blah.py

# Transfer a whole directory
ampy -p /dev/tty.usbmodem1234561 put embit

# Run an arbitrary local python file on the ESP32
ampy -p /dev/tty.usbmodem1234561 run test.py
```


### `mpremote`
Offers similar features to `ampy` but also provides an interactive REPL option.

```bash
pip install mpremote
```

```bash
# Run a local file on the device
mpremote connect /dev/tty.usbmodem1234561 run demos/secp256k1_test.py
mpremote connect /dev/tty.usbserial-110 run demos/secp256k1_test.py

# Enter the interactive REPL
mpremote connect /dev/tty.usbserial-110 repl

# List files on the device
mpremote connect /dev/tty.usbserial-110 ls
```



## Misc ESP32 notes

### Expand app partition when necessary
If your compilation fails with something like:
```
Error: app partition is too small for binary micropython.bin size 0x1f28d0:
  - Part 'factory' 0/0 @ 0x10000 size 0x1f0000 (overflow 0x28d0)
```

You'll need to alter the partition sizes for your target board. Here's a baseline partition table:
```bash
# Notes: the offset of the partition table itself is set in
# $IDF_PATH/components/partition_table/Kconfig.projbuild.
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x6000,
phy_init, data, phy,     0xf000,  0x1000,
factory,  app,  factory, 0x10000, 0x1F0000,
vfs,      data, fat,     0x200000, 0xE00000,
```

We can create more room for the `factory` partition that contains the `app`:
* Expand the `factory` partition from `0x1F0000` to `0x2F0000`.
* Shift the next partition's offset (4th col) by the same amount: change `0x200000` to `0x300000`.
* Reduce the size (5th col) of the `vfs` partition by the same amount: change `0xE00000` to `0xD00000`.

```
factory,  app,  factory, 0x10000, 0x2F0000,
vfs,      data, fat,     0x300000, 0xD00000,
```

Then configure the board to use your new partitions:
```
CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions-16MiB-my_version.csv"
```


# Raspi RP2040
In the Docker container:
```bash
cd /root/micropython/ports/rp2
make -j6 submodules

# Compile the custom firmware for RP2040
idf.py -D MICROPY_BOARD=PICO -B build-pico -DUSER_C_MODULES=/code/deps/usermods/micropython.cmake build

# Copy the completed firmware to shared volume
cp build-pico/firmware.uf2 /code/pico/.
```

Hold down the `BOOTSEL` button while restarting the Pico. It will mount itself as USB drive RPI-RP2.

Drag the `.u2f` file to the RPI-RP2 disk. It will copy and then remount itself.

On your local machine:
```bash
ampy -p /dev/tty.usbmodem01 run test.py
```


# Random MicroPython notes
Get the platform:
```python
>>> import usys
>>> usys.platform
'esp32'
```

Get full firmware details:
```python
>>> import os
>>> os.uname()
(sysname='esp32', nodename='esp32', release='1.18.0', version='v1.18-4-g5c8f5b4ce-dirty on 2022-07-05', machine='FeatherS2 with ESP32-S2')
```



## Generate custom font
```bash
# bin format for dynamic includes
lv_font_conv --font OpenSans-Semibold.ttf -r 0x00-0xFF --size 20 --format bin --bpp 4 --no-compress -o opensans_semibold_20.bin 

# lvgl format to compile directly into firmware
lv_font_conv --font OpenSans-Regular.ttf -r 0x20-0x7F --size 17 --format lvgl --bpp 3 -o opensans_regular_17.c  --force-fast-kern-format
```


Convert FontAwesome glyphs
```python
# Extract the list of chars in decimal:
import inspect
from seedsigner.gui.components import FontAwesomeIconConstants
char_list = []
for key, value in inspect.getmembers(FontAwesomeIconConstants):
    if key.startswith("_"):
        continue
    char_list.append(ord(value))
",".join([str(c) for c in char_list])

# Also add the space char (32).
```

```bash
lv_font_conv --font Font_Awesome_6_Free-Solid-900.otf -r 32,61703,61700,61701,61702,61488,61655,61657,61658,61656,61713,61752,62754,62755,62756,62757,62758,62759,62760,61459,61572,61724,61475,62073,61912,62212,43,61457,61481,62201,63449,61528,61640,61776,61841,61778,61777,61770,61553,61596,88  --size 22 --format bin --bpp 4 --no-compress -o fontawesome_22.bin

lv_font_conv --font Font_Awesome_6_Free-Solid-900.otf -r 32,61703,61700,61701,61702,61488,61655,61657,61658,61656,61713,61752,62754,62755,62756,62757,62758,62759,62760,61459,61572,61724,61475,62073,61912,62212,43,61457,61481,62201,63449,61528,61640,61776,61841,61778,61777,61770,61553,61596,88  --size 24 --format bin --bpp 4 --no-compress -o fontawesome_24.bin

lv_font_conv --font seedsigner-glyphs.otf -r 32,0xe900-0xe90d  --size 24 --format bin --bpp 4 --no-compress -o seedsigner_glyphs_24.bin

lv_font_conv --font seedsigner-glyphs.otf -r 32,0xe900-0xe90d  --size 22 --format bin --bpp 4 --no-compress -o seedsigner_glyphs_22.bin

lv_font_conv --font seedsigner-glyphs.otf -r 0xe90d  --size 100 --format bin --bpp 4 --no-compress -o bitcoin_logo_100.bin

lv_font_conv --font seedsigner-glyphs.otf -r 0xe90d  --size 150 --format bin --bpp 4 --no-compress -o bitcoin_logo_150.bin


```


python3 ~/lv_micropython/lib/lv_bindings/lvgl/scripts/built_in_font/built_in_font_gen.py 



Edit nano ~/lv_micropython/lib/lv_bindings/lv_conf.h 

And add custom fonts:
```
/*Optionally declare custom fonts here.
 *You can use these fonts as default font too and they will be available globally.
 *E.g. #define LV_FONT_CUSTOM_DECLARE   LV_FONT_DECLARE(my_font_1) LV_FONT_DECLARE(my_font_2)*/
#define LV_FONT_CUSTOM_DECLARE LV_FONT_DECLARE(opensans_regular_17) LV_FONT_DECLARE(opensans_semibold_20)
```
