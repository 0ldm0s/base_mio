#!/usr/bin/env bash
PID=/tmp/pymio.pid
kill -INT $(<"$PID")