FROM gcc
RUN git clone https://github.com/torvalds/linux
RUN apt-get update \
&&  apt-get install -y \
    bc \
    time
WORKDIR linux
RUN make allmodconfig
CMD time bash -c "make -j $(grep -c processor /proc/cpuinfo) > /dev/null"