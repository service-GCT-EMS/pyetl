echo off
rem set python=D:\donnees\outils\python3.4\python.exe
rem set PATH=c:\util\ora11g\client\bin;%PATH%
rem set ORACLE_HOME=c:\util\ora11g\client
rem set psql=D:\donnees\programmes\postgres\9.5.1\pgsql\bin\psql
rem set PYETL_SITE_PARAMS=site_params
call site_params\specifique.bat
set programmes=S:\Commun\dev_open_source\pyetl_dev
call env_mapper\scripts\activate
echo 'variables configurees mode dev pyetl '
echo on