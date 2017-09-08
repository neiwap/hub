#!/bin/bash

: ${CORE:=$(grep -c processor /proc/cpuinfo)}
# EXTRA (--dry-run)

report() {
cat <<EOF
[{
"measurement": "kernelcompile",
"time": "${time}",
"fields": {
"real" : %e,
"user" : %U,
"sys" : %S
}
}]
EOF
}

time=$(date --rfc-3339=seconds)
format=$(report)

/usr/bin/time --format "${format}" bash -c "make ${EXTRA} -j ${CORE} >/dev/null 2>&1"
