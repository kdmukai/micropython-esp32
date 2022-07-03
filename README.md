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
idf.py -D MICROPY_BOARD=UM_FEATHERS2 -B build-um_feathers2 -DUSER_C_MODULES=/root/usermods/secp256k1-embedded/micropython.cmake build

# Copy the compiled artifacts over to the shared /code volume so you can access them outside the container
cp build-um_feathers2/bootloader/bootloader.bin /code/.
cp build-um_feathers2/partition_table/partition-table.bin /code/.
cp build-um_feathers2/micropython.bin /code/.
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

Write in the new firmware
```bash
esptool.py --port /dev/tty.usbmodem01 erase_flash
esptool.py -p /dev/tty.usbmodem01 -b 460800 --before default_reset --chip esp32s2  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 micropython.bin
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

