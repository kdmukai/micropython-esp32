# MicroPython-esp32
The [Unexpected Maker FeatherS2](https://feathers2.io/) (ESP32-S2) comes pre-loaded with the CircuitPython UF2 bootloader. The following steps will replace the UF2 bootloader with MicroPython.


## Build the custom MicroPython firmware
Build and run the Docker container that will be configured to build the firmware
```bash
docker-compose build
docker-compose up
```

Inside the container:
```bash
cd ports/esp32
make BOARD=UM_FEATHERS2 USER_C_MODULES=/root/usermods/secp256k1-embedded/micropython.cmake CFLAGS_EXTRA=-DMODULE_SECP256K1_ENABLED=1
```


## Install MicroPython
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

Clear the existing bootloader:
```bash
esptool.py --port /dev/tty.usbmodem01 erase_flash
```

You should see:
```
    esptool.py v4.1
    Serial port /dev/tty.usbmodem01
    Connecting...
    Detecting chip type... Unsupported detection protocol, switching and trying again...
    Detecting chip type... ESP32-S2
    Chip is ESP32-S2
    Features: WiFi, No Embedded Flash, No Embedded PSRAM, ADC and temperature sensor calibration in BLK2 of efuse V1
    Crystal is 40MHz
    MAC: 84:f7:03:73:9f:78
    Uploading stub...
    Running stub...
    Stub running...
    Erasing flash (this may take a while)...
    Chip erase completed successfully in 34.9s
    WARNING: ESP32-S2 chip was placed into download mode using GPIO0.
    esptool.py can not exit the download mode over USB. To run the app, reset the chip manually.
    To suppress this note, set --after option to 'no_reset'.
```

Download the latest Release firmware at: https://micropython.org/download/featherS2/

Flash the MicroPython firmware to the FeatherS2:
```bash
esptool.py --chip esp32s2 --port /dev/tty.usbmodem01 write_flash -z 0x1000 featherS2-20220618-v1.19.1.bin
```


## Interact with the board
Install the `ampy` tool:
```bash
pip install adafruit-ampy
```

