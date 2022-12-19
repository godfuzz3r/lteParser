FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

# Install updates and dependencies
RUN apt-get update && \
    apt-get -y install cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev git \
    libzmq3-dev libboost-system-dev libboost-test-dev libboost-thread-dev libqwt-qt5-dev qtbase5-dev \
    software-properties-common g++ make pkg-config libpython2-dev python-numpy swig libi2c-dev \
    libboost-program-options-dev libconfig++-dev net-tools iputils-ping libusb-1.0-0-dev libpython3-dev python3-numpy swig \
    python3-distutils jq curl extrace

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

# UHD drivers for USRP
RUN add-apt-repository ppa:ettusresearch/uhd && \
    apt update && apt -y install libuhd-dev libuhd4.3.0 uhd-host && \
    uhd_images_downloader


# Get srsLTE, compile and install
RUN git clone https://github.com/srsran/srsRAN.git

COPY cellscan.patch /srsRAN

WORKDIR /srsRAN

RUN git checkout tags/release_22_04_1 && git apply cellscan.patch

RUN mkdir build && cd build && \
    cmake ../ && make -j`nproc` cell_search srsue && make install && \
    ldconfig

WORKDIR /

ENV UHD_IMAGES_DIR=/usr/share/uhd/images/

RUN apt install -y python3-pip

RUN pip3 install tailer

COPY worker.sh parse_sib.py ./

ENTRYPOINT ["./worker.sh"]
