#! /bin/bash
#set -x -e

N=$1
shift
: ${N:=1000000}

./64/gensort -a ${N} /tmp/unsorted
time sort $@ < /tmp/unsorted > /tmp/sorted
./64/valsort /tmp/sorted

rm -f /tmp/unsorted /tmp/sorted
