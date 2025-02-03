FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y software-properties-common

# UHD drivers for USRP
RUN add-apt-repository -y ppa:ettusresearch/uhd && \
    add-apt-repository -y ppa:nuandllc/bladerf && \
    add-apt-repository -y ppa:myriadrf/drivers && \
    apt update && \
    apt install -y \
    bladerf libbladerf-dev \
    libuhd-dev libuhd4.8.0 uhd-host \
    # build dependencies
    cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev git \
    libzmq3-dev libboost-system-dev libboost-test-dev libboost-thread-dev libqwt-qt5-dev qtbase5-dev \
    software-properties-common g++ make pkg-config libpython2-dev python-numpy swig libi2c-dev \
    libboost-program-options-dev libconfig++-dev libusb-1.0-0-dev libpython3-dev python3-numpy swig \
    && rm -rf /var/lib/apt/lists/*

ENV UHD_IMAGES_DIR=/usr/share/uhd/images/

# Download UHD images using the built-in uhd_images_downloader
RUN uhd_images_downloader

# Get SoapySDR, compile and install
RUN git clone https://github.com/pothosware/SoapySDR.git && \
    cd SoapySDR && \
    git checkout 637023d5e1b60e117a6533daddc4d991a33375f9 && \
    mkdir build && cd build && \
    cmake ../ && make && make install && \
    ldconfig

# Get Limesuite, compile and install
RUN git clone https://github.com/myriadrf/LimeSuite.git && \
    cd LimeSuite && \
    git checkout tags/v22.09.1 -b v22.09.1 && \
    mkdir builddir && cd builddir && \
    cmake ../ && make && make install && \
    ldconfig

RUN git clone https://github.com/pothosware/SoapyBladeRF.git && \
    cd SoapyBladeRF && \
    mkdir build && cd build && \
    cmake .. && make && make install && \
    ldconfig

# Get srsLTE, compile and install
RUN git clone https://github.com/srsran/srsRAN_4G

#COPY ./srsRAN_4G /srsRAN_4G

COPY sib_logger.patch /srsRAN_4G

WORKDIR /srsRAN_4G/

# origin/master at 2024.12.25
RUN git checkout ec29b0c1ff79cebcbe66caa6d6b90778261c42b8 && git apply sib_logger.patch && \
    mkdir build && cd build && \
    cmake -DUSE_LTE_RATES=ON ../ && make -j`nproc` cell_search srsue && make install && \
    ldconfig

RUN cp /srsRAN_4G/build/lib/examples/cell_search /usr/bin/

RUN mkdir /vol/

WORKDIR /vol

ENTRYPOINT ["bash", "-c", "cp /vol/helpers/uhd_images/*.bin /usr/share/uhd/images/ 2>/dev/null || true && bash"]