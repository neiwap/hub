#!/bin/bash
set -x -e
inotifywait -m -e close . --format %f | while read job
do
    bash ${job}
    rm -f ${job}
done
