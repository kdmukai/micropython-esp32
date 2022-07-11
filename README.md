# MicroPython-esp32
Create a custom MicroPython firmware for an ESP32 board with `secp256k1` compiled in.


## Build the custom MicroPython firmware
Build and run the Docker container that will be configured to build the firmware
```bash
docker-compose build
docker-compose up
```

Run the `container_bash.sh` script to get a shell prompt inside the container (you may need to edit the container's name in the script).

Once you're inside the container, you can compile the custom firmware:
```bash
# This example targets the UM FeatherS2 board
idf.py -D MICROPY_BOARD=UM_FEATHERS2 -B build-um_feathers2 -DUSER_C_MODULES=/root/usermods/micropython.cmake build

# Copy the compiled artifacts over to the shared /code volume so you can access them outside the container
cp build-um_feathers2/bootloader/bootloader.bin /code/feather_s2/.
cp build-um_feathers2/partition_table/partition-table.bin /code/feather_s2/.
cp build-um_feathers2/micropython.bin /code/feather_s2/.
```

Steps for FeatherS3 (esp32-S3)
```bash
idf.py -D MICROPY_BOARD=GENERIC_S3_SPIRAM -B build-generic_s3_spiram -DUSER_C_MODULES=/root/usermods/micropython.cmake build
cp build-generic_s3_spiram/bootloader/bootloader.bin /code/feather_s3/.
cp build-generic_s3_spiram/partition_table/partition-table.bin /code/feather_s3/.
cp build-generic_s3_spiram/micropython.bin /code/feather_s3/.
```

Steps for Generic esp32 (WROOM, etc)
```bash
idf.py -D MICROPY_BOARD=GENERIC -B build-generic -DUSER_C_MODULES=/root/usermods/micropython.cmake build
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
