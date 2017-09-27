#! /bin/bash
#set -x -e

N=$1
shift
: ${N:=1000000}

if ! [ -f /tmp/unsorted ]
then
    ./64/gensort -a ${N} /tmp/unsorted.tmp
    mv /tmp/unsorted.tmp /tmp/unsorted
fi
