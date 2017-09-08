FROM gcc
RUN git clone https://github.com/torvalds/linux
RUN apt-get update \
&&  apt-get install -y \
    bc \
    time
WORKDIR linux
RUN make allmodconfig
COPY benchmark.sh ./benchmark.sh
ENTRYPOINT [ "./benchmark.sh" ]
