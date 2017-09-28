FROM ubuntu
#ADD http://www.ordinal.com/try.cgi/gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
COPY gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
RUN tar -xf gensort-linux-1.5.tar.gz || true
COPY prepare /usr/bin/prepare
COPY run /usr/bin/run
COPY terminated /usr/bin/terminated
ENTRYPOINT [ "sleep", "inf" ]

