#! /bin/bash
#set -x -e

N=$1
shift
: ${N:=1000000}

funnel() {
    export homedir=`echo ~`
    export JVM_ARGS=${JVM_ARGS}"-DspecPath=.;${homedir}/funnel/etc;/opt/funnel/etc "
    export JVM_ARGS=${JVM_ARGS}"-Dlog4j.configuration=/opt/funnel/etc/log4j.xml "
    export JVM_ARGS=${JVM_ARGS}"-Xms48M -Xmx1G -XX:NewRatio=2 "
    export JVM_ARGS=${JVM_ARGS}"-ea:com.obdobion.funnel... "
    export JVM_RUNNABLE_JAR="/opt/funnel/lib/funnel-1.3.18.jar"
    #export FUNNEL_OPTS="--cacheWork--cacheInput--workDirectory=/tmp"
    export FUNNEL_OPTS="--workDirectory=/tmp"
    time java -Dversion=1.3.18 ${JVM_ARGS} -jar ${JVM_RUNNABLE_JAR} ${FUNNEL_OPTS} $@
}

./64/gensort -a ${N} /tmp/unsorted
funnel /tmp/unsorted -o /tmp/sorted
#time sort -S 1G < /tmp/unsorted > /tmp/sorted
./64/valsort /tmp/sorted

rm -f /tmp/unsorted /tmp/sorted
