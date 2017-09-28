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
RUN apt-get install -y \
    python-pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY benchmark.py .
COPY prepare /usr/bin/prepare
COPY run /usr/bin/run
ENTRYPOINT [ "sleep", "inf" ]
