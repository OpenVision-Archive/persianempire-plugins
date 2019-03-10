#!/bin/sh

top -n1 > /tmp/cpuinfo.tmp &
TOP_PID=$!
sleep 1
kill $TOP_PID

