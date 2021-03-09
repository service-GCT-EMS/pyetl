@echo off
rem pb de connection postgres12
set PGGSSENCMODE=disable
set PYETL_SITE_PARAMS=site_params
python C:\dev\pyetl\mapper.py %*