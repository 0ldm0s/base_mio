#!/bin/bash
PID=/tmp/pymio.pid
kill -INT $(<"$PID")