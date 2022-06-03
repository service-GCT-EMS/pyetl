rem installation d un environnement virtuel

python -m venv ..\env_mapper
call ..\env_mapper\scripts\activate
python -m pip install --upgrade pip
pip install wheel
pip install -r install\requirement.txt 
call unzip.bat
