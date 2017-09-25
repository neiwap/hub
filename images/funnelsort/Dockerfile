FROM centos
RUN yum install -y java
WORKDIR sort
#ADD https://sourceforge.net/projects/funnelsort/files/centos/funnel-1.3.18-1.x86_64.rpm/download funnel-1.3.18-1.x86_64.rpm
COPY funnel-1.3.18-1.x86_64.rpm funnel-1.3.18-1.x86_64.rpm
RUN rpm -i funnel-1.3.18-1.x86_64.rpm
#ADD http://www.ordinal.com/try.cgi/gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
COPY gensort-linux-1.5.tar.gz gensort-linux-1.5.tar.gz
RUN tar -xf gensort-linux-1.5.tar.gz || true
