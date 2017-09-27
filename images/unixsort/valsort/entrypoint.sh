#! /bin/bash
#set -x -e

until [ -f /tmp/sorted ]; do sleep 1; done
./64/valsort /tmp/sorted
rm -f /tmp/sorted
