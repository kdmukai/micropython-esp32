# MicroPython-esp32
Create a custom MicroPython firmware for an ESP32 board with `secp256k1` compiled in.

## Clone this repo and its dependencies
```bash
git clone https://github.com/kdmukai/micropython-esp32.git

# clone the esixtyone fork of lv_micropython
cd micropython-esp32
git submodule update --init deps/lv_micropython

# And within lv_micropython, clone the esixtyone fork of lv_bindings
cd deps/lv_micropython
git submodule update --init --recursive lib/lv_bindings

git submodule update --init deps/embit
git submodule update --init --recursive deps/usermods/secp256k1-embedded
git submodule update --init deps/usermods/uhashlib

```


## Build the custom MicroPython firmware
Build and run the Docker container that will be configured to build the firmware
```bash
docker-compose build
docker-compose up
```

Run the `container_bash.sh` script to get a shell prompt inside the container (you may need to edit the container's name in the script).

### Configure board target for LVGL compatibility
The `boards/GENERIC_S2` sdkconfig has already been updated for LVGL compatibility. Edit the definition of any other S2 board by updating its sdkconfig.board:
```
CONFIG_ETH_ENABLED=n
CONFIG_ETH_USE_SPI_ETHERNET=n
```

### Expand app partition when necessary
If your compilation fails with something like:
```
Error: app partition is too small for binary micropython.bin size 0x1f28d0:
  - Part 'factory' 0/0 @ 0x10000 size 0x1f0000 (overflow 0x28d0)
```

You'll need to alter the partition sizes for your target board.

Copy of `partitions-16MiB.csv` to `partitions-16MiB-lvgl.csv` and make the following changes:

* Expand the `factory` partition from `0x1F0000` to `0x2F0000`.
* Shift the next partition's Offset by the same amount: from `0x200000` to `0x300000`.
* Reduce the size of the "vfs" partition by the same amount: from `0xE00000` to `0xD00000`.

```
factory,  app,  factory, 0x10000, 0x2F0000,
vfs,      data, fat,     0x300000, 0xD00000,
```

Then configure the board to use your new partitions:
```
CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions-16MiB-lvgl.csv"
```

### Compile the firmware for the target board
Now we can compile the custom firmware:
```bash
# This example targets the UM FeatherS2 board
make LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=UM_FEATHERS2 USER_C_MODULES=/root/usermods/micropython.cmake

# Copy the compiled artifacts over to the shared /code volume so you can access them outside the container
cp build-UM_FEATHERS2/bootloader/bootloader.bin /code/build/feather_s2/.
cp build-UM_FEATHERS2/partition_table/partition-table.bin /code/build/feather_s2/.
cp build-UM_FEATHERS2/micropython.bin /code/build/feather_s2/.

# Targeting the GENERIC_S2 board
make LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=GENERIC_S2 USER_C_MODULES=/root/usermods/micropython.cmake
cp build-GENERIC_S2/bootloader/bootloader.bin /code/build/generic_s2/.
cp build-GENERIC_S2/partition_table/partition-table.bin /code/build/generic_s2/.
cp build-GENERIC_S2/micropython.bin /code/build/generic_s2/.
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
esptool.py --port /dev/tty.usbmodem01 erase_flash
esptool.py -p /dev/tty.usbmodem01 -b 460800 --before default_reset --chip esp32s2  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
```


### FeatherS3 (esp32-S3)
```
esptool.py --port /dev/tty.usbmodem101 erase_flash
esptool.py -p /dev/tty.usbmodem101 -b 460800 --before default_reset --chip esp32s3  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
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



# Raspi RP2040
In the Docker container:
```bash
cd /root/micropython/ports/rp2
make -j6 submodules

# Compile the custom firmware for RP2040
idf.py -D MICROPY_BOARD=PICO -B build-pico -DUSER_C_MODULES=/root/usermods/micropython.cmake build

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
