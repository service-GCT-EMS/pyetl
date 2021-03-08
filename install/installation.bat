rem installation d un environnement virtuel

python -m venv ..\env_mapper
call ..\env_mapper\scripts\activate
python -m pip install --upgrade pip
pip install wheel
pip install ./wheels/numpy-1.19.4+mkl-cp38-cp38-win_amd64.whl
pip install ./wheels/GDAL-3.1.4-cp38-cp38-win_amd64.whl
pip install ./wheels/Shapely-1.7.1-cp38-cp38-win_amd64.whl
pip install ./wheels/Fiona-1.8.18-cp38-cp38-win_amd64.whl
pip install ./wheels/cx_Oracle-8.0.1-cp38-cp38-win_amd64.whl
pip install ./wheels/psycopg2-2.8.6-cp38-cp38-win_amd64.whl
pip install ./wheels/psutil-5.7.3-cp38-cp38-win_amd64.whl
pip install -r install\requirement.txt 
call unzip.bat
