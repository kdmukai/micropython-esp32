# Pull base image: Ubuntu v20.x (aka "focal")
FROM arm64v8/ubuntu:focal

RUN apt update
RUN apt install -y software-properties-common curl nano
RUN add-apt-repository ppa:pybricks/ppa

# Setup steps from Espressif for ESP32: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/linux-macos-setup.html
RUN apt install -y git wget flex bison gperf python3 python3-venv python3-dev cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0

# Python3 and pip setup
WORKDIR /root
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py
RUN pip3 install esptool

# Get ESP-IDF
WORKDIR /root/home
RUN mkdir -p esp
WORKDIR /root/home/esp
RUN git clone -b v4.4.1 --recursive https://github.com/espressif/esp-idf.git
WORKDIR /root/home/esp/esp-idf
RUN ./install.sh esp32,esp32s2,esp32s3

WORKDIR /root
RUN git clone -b v1.18 https://github.com/micropython/micropython.git

# Build mpy-cross
WORKDIR /root/micropython
RUN make -j6 -C mpy-cross

# Setup MicroPython ESP32 support
WORKDIR /root/micropython/ports/esp32
RUN make -j6 submodules

# Get secp256k1-embedded
WORKDIR /root
RUN mkdir usermods
WORKDIR /root/usermods
RUN git clone --recursive https://github.com/diybitcoinhardware/secp256k1-embedded.git

# Add CMake support to secp256k1-embedded
COPY docker/secp256k1-embedded-micropython.cmake /root/usermods/secp256k1-embedded/micropython.cmake

# Set up the interactive bash shell to our liking
COPY docker/bashrc /root/.bashrc

WORKDIR /root/micropython
