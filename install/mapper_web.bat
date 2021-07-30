@echo off
rem pb de connection postgres12
set PGGSSENCMODE=disable
start python C:\dev\pyetl\mapper_web.py
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5000/
