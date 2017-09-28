FROM ubuntu
RUN apt-get update \
&&  apt-get install -y \
    time
#ADD http://www.ordinal.com/try.cgi/gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
COPY gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
RUN tar -xf gensort-linux-1.5.tar.gz || true
COPY prepare /usr/bin/prepare
COPY run /usr/bin/run
COPY status /usr/bin/status
ENTRYPOINT [ "sleep", "inf" ]

