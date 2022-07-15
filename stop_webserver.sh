#!/bin/sh
PID=/tmp/pymio.pid
kill -INT $(<"$PID")