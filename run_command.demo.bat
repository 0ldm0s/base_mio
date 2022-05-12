@echo off
SET COMMAND=cli.WorkMan.Daemon.hello
SET MIO_CONFIG=production
SET FLASK_APP=mio.shell
flask cli exe -cls=%COMMAND%
pause