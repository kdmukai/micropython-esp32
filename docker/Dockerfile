# Pull base image: Ubuntu v20.x (aka "focal")
FROM ubuntu:focal

RUN apt update
RUN apt install -y software-properties-common curl nano
RUN add-apt-repository ppa:pybricks/ppa

# Need Automake
RUN apt install -y autoconf libtool

# Setup steps from Espressif for ESP32: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/linux-macos-setup.html
RUN apt install -y git wget flex bison gperf python3 python3-venv python3-dev cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0

# pip setup
WORKDIR /root
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py
RUN pip3 install esptool

# Get ESP-IDF compiler for esp32
WORKDIR /root/home
RUN mkdir -p esp
WORKDIR /root/home/esp
RUN git clone -b v4.4.1 --recursive https://github.com/espressif/esp-idf.git
WORKDIR /root/home/esp/esp-idf
RUN ./install.sh esp32,esp32s2,esp32s3

# Add the esp32-camera driver
WORKDIR /root/home/esp/esp-idf/components
RUN git clone -b v2.0.2 https://github.com/espressif/esp32-camera.git

WORKDIR /root
# Build MicroPython firmware from esixtyone's fork of lv_micropython w/his tweaks for esp32-S2
# RUN git clone -b fix/esp32s2-build https://github.com/esixtyone/lv_micropython.git
# WORKDIR /root/lv_micropython

# RUN git submodule update --init --recursive lib/lv_bindings

# Freeze embit into the ESP32 firmware; remove unnecessary dirs, soft link from modules
# WORKDIR /root
# RUN git clone -b v0.5.0 https://github.com/diybitcoinhardware/embit.git
# WORKDIR /code/deps/embit
# RUN rm -rf src/embit/liquid
# RUN rm -rf src/embit/util
# RUN ln -s /code/deps/embit/src/embit /code/deps/lv_micropython/ports/esp32/modules/embit

# Build mpy-cross
# RUN make -C deps/lv_micropython/mpy-cross

# # Setup MicroPython ESP32 support
# WORKDIR /code/deps/lv_micropython/ports/esp32
# RUN make submodules

# Get additional resources as usermods:
# WORKDIR /root
# RUN mkdir usermods
# WORKDIR /root/usermods
# RUN git clone --recursive -b esp32_support https://github.com/kdmukai/secp256k1-embedded.git
# RUN git clone -b esp32s2-s3-compatibility https://github.com/diybitcoinhardware/uhashlib.git

# # Add cmake file for compiling usermods
# COPY docker/micropython.cmake /root/usermods/micropython.cmake

# # Add modified partitions to make more room for larger firmware
# COPY docker/partitions-16MiB-lvgl.csv /root/lv_micropython/ports/esp32/partitions-16MiB-lvgl.csv

# # Raspi RP2040 support
# RUN apt install -y gcc-arm-none-eabi build-essential
# WORKDIR /root/lv_micropython/ports/rp2
# RUN make submodules

# # LVGL font converter
# WORKDIR /root
# RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
# RUN apt install -y nodejs
# RUN npm i lv_font_conv -g

# Set up the interactive bash shell to our liking
COPY docker/bashrc /root/.bashrc

