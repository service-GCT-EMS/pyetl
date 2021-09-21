time /T 
call init_d.bat
set FLASK_APP=%programmes%\mapper_web.py
start python -m flask run
time /T
IF %ERRORLEVEL% NEQ 0 (
  echo sortie en erreur du programme mapper
)

timeout /t 5
start http://127.0.0.1:5000