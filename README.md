# MicroPython-esp32
Create a custom MicroPython firmware that is Bitcoin-enabled (`secp256k1` compiled in, `embit` onboard) that initially targets the esp32-S2.

Choose:
* Begin testing things out immediately by downloading the [pre-compiled firmware](demos/precompiled) for the esp32-S2 Saola-1R dev board.
* OR compile the firmware yourself following the steps below.

For now we assume you're working with the Saola-1R build described here:
* [Instructions for assembling the Saola-1R kit](docs/saola_1r_build/README.md)


---

# Building the firmware

## Clone this repo and its dependencies
```bash
git clone https://github.com/kdmukai/micropython-esp32.git
cd micropython-esp32

# clone our various submodule dependencies
git submodule update --init

# And within lv_micropython, recursively clone the esixtyone fork of lv_bindings
cd deps/lv_micropython
git checkout fix/esp32s2-build
git submodule update --init --recursive lib/lv_bindings

# Recursively clone secp256k1
cd ../../
git submodule update --init --recursive deps/usermods/secp256k1-embedded

# embit needs some parts trimmed out of it
rm -rf deps/embit/src/embit/liquid
rm -rf deps/embit/src/embit/util
```

## Create a python3 virtualenv and install dependencies
```
pip install virtualenv
virtualenv .env
source .env/bin/activate
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

# soft link embit inside lv_micropython
ln -s /code/deps/embit/src/embit /code/deps/lv_micropython/ports/esp32/modules/embit
```

### Configure board target for LVGL compatibility
_Note: The Saola-1R and any "GENERIC_S2" board can skip this step since their sdkconfigs have already been updated for LVGL compatibility._

Edit the definition of your S2 board in `lv_micropython/ports/esp32/boards` by updating its `sdkconfig.board`:
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
make LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=SAOLA_1R BUILD=/root/build-saola_1r USER_C_MODULES=/root/internal/usermods/micropython.cmake
mkdir -p /code/build/saola_1r
cp /root/build-saola_1r/bootloader/bootloader.bin /code/build/saola_1r/.
cp /root/build-saola_1r/partition_table/partition-table.bin /code/build/saola_1r/.
cp /root/build-saola_1r/micropython.bin /code/build/saola_1r/.
```


## Write the firmware to the board
see: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html#esp32-intro

With Python 3.x on your local machine:
```bash
pip install esptool
```

Put the board into bootloader update mode:
* Press and hold BOOT
* Click RST and release
* Release BOOT

The board's port name should be something like `/dev/tty.usbserial-1110`. Confirm with:
```
ls /dev
```

Write the new firmware; the `write_flash` command is copied from the `idf.py` guidance above when compilation is completed.

### Saola-1R (S2 dev kit)
```bash
esptool.py -p /dev/tty.usbserial-1110 erase_flash
esptool.py -p /dev/tty.usbserial-1110 -b 460800 --before default_reset --chip esp32s2  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```

Once it's complete, power cycle or press RST to reset the board to normal operations. It will/may remount itself with a different name.


## Interact with the board

### `ampy`
Install the `ampy` tool:
```bash
pip install adafruit-ampy
```

```bash
# List the files on the board
ampy -p /dev/tty.usbserial-1110 ls

# Transfer files. Most of the demos require:
ampy -p /dev/tty.usbserial-1110 put demos/pin_defs.py
ampy -p /dev/tty.usbserial-1110 put demos/fonts/opensans_regular_17.bin
ampy -p /dev/tty.usbserial-1110 put demos/fonts/opensans_semibold_20.bin

# Transfer a whole directory
ampy -p /dev/tty.usbserial-1110 put mydir

# Run an arbitrary local python file on the ESP32 (not recommended; use mpremote -- see below)
ampy -p /dev/tty.usbserial-1110 run test.py
```


### `mpremote`
Offers similar features to `ampy` but also provides an interactive REPL option. Runs local scripts more reliably.

```bash
pip install mpremote
```

```bash
# Run a local file on the device
mpremote connect /dev/tty.usbserial-1110 run demos/secp256k1_test.py

# Enter the interactive REPL
mpremote connect /dev/tty.usbserial-1110 repl

# List files on the device
mpremote connect /dev/tty.usbserial-1110 ls

# Mount the current dir to make its files available as if it was onboard, then run
#   a test file that depends on those imports.
mpremote connect /dev/tty.usbserial-1110 mount . run blah/some_test_file.py

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
(Have not seriously pursued RP2040 support; notes here are to return to later)

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


# Generic Linux
(Have not seriously pursued Linux support; notes here are to return to later)

Follow the instructions for the [Unix (Linux) port](https://github.com/esixtyone/lv_micropython/tree/ad12fa45de530db806d8193d887ccf1e75f81d9f#unix-linux-port).

```bash
make -C ports/unix USER_C_MODULES=/code/deps/usermods/micropython.cmake
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
see: https://github.com/lvgl/lv_font_conv

```bash
# bin format for dynamic includes
lv_font_conv --font OpenSans-Semibold.ttf -r 0x00-0xFF --size 20 --format bin --bpp 4 --no-compress -o opensans_semibold_20.bin 

# lvgl format to compile directly into firmware
lv_font_conv --font OpenSans-Regular.ttf -r 0x20-0x7F --size 17 --format lvgl --bpp 3 -o opensans_regular_17.c  --force-fast-kern-format
```

### Convert FontAwesome glyphs
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

