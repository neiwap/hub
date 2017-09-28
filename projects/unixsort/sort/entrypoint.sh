#! /bin/bash
#set -x -e
until [ -f /tmp/unsorted ]; do sleep 1; done
time sort $@ < /tmp/unsorted > /tmp/sorted.tmp
mv /tmp/sorted.tmp /tmp/sorted
