#!/bin/bash
rsync -a /code/deps/ /root/internal/
make -C /root/internal/lv_micropython/ports/esp32 LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=SAOLA_1R BUILD=/root/build-saola_1r USER_C_MODULES=/root/internal/usermods/micropython.cmake clean
make -C /root/internal/lv_micropython/ports/esp32 LV_CFLAGS="-DLV_MEM_SIZE=32768 -DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1" BOARD=SAOLA_1R BUILD=/root/build-saola_1r USER_C_MODULES=/root/internal/usermods/micropython.cmake
mkdir -p /code/build/saola_1r
cp /root/build-saola_1r/bootloader/bootloader.bin /code/build/saola_1r/.
cp /root/build-saola_1r/partition_table/partition-table.bin /code/build/saola_1r/.
cp /root/build-saola_1r/micropython.bin /code/build/saola_1r/.