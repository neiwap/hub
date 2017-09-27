FROM ubuntu
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
&&  apt-get install -y \
    build-essential \
    automake \
    libtool \
    mysql-server \
    mysql-client \
    libmysqlclient-dev
WORKDIR /sysbench
COPY sysbench .
RUN ./autogen.sh \
&&  ./configure  \
&&  make         \
&&  make install
