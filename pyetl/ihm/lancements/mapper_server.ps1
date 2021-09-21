
Get-Date
if (-not $Env:VIRTUAL_ENV){
    env_mapper\scripts\activate
}
$programmes="S:\Commun\outils_publics\pyetl_dev"
$env:PYETL_SITE_PARAMS="site_params"
$env:FLASK_APP=$programmes+"\mapper_web.py"
python -m flask run

