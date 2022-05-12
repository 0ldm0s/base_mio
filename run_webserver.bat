@echo off
SET MIO_CONFIG=production
SET MIO_LIMIT_CPU=1
SET MIO_PORT=5050
SET MIO_HOST=0.0.0.0
python mio\pymio.py
pause