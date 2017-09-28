FROM ubuntu
WORKDIR sort
#ADD http://www.ordinal.com/try.cgi/gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
COPY gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
RUN tar -xf gensort-linux-1.5.tar.gz || true
COPY entrypoint.sh entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
