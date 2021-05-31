$installdir=split-path -parent $MyInvocation.MyCommand.Definition
Get-Date
$installdir
if (-not $Env:VIRTUAL_ENV){
    $env:ORACLE_HOME=$installdir+"\autres\instantclient19.9"
    $env:PATH=$env:ORACLE_HOME+";"+$env:PATH
    $env:NLS_LANG="FRENCH_FRANCE.UTF8"
    $activ=$installdir+"\env_mapper\scripts\activate.ps1"
    $env:psql=$installdir+"\autres\psql\psql"
    
    invoke-expression $activ
}
$programmes=$installdir+"\mapper"
$env:PYETL_SITE_PARAMS=".\site_params"
python $programmes\mapper_web.py
Get-Date

