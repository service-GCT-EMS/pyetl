$installdir=split-path -parent $MyInvocation.MyCommand.Definition

$env:PATH=$installdir+";"+$env:PATH
if (-not $Env:VIRTUAL_ENV){
    $env:ORACLE_HOME=$installdir+"\autres\instantclient19.9"
    $env:PATH=$env:ORACLE_HOME+";"+$env:PATH
    $env:NLS_LANG="FRENCH_FRANCE.UTF8"
    $activ=$installdir+"\env_mapper\scripts\activate.ps1"
    $env:psql=$installdir+"\autres\psql\psql"
    $env:prog_export=$installdir+"\autres\fea2orav2\ORA2FEA.exe"
    invoke-expression $activ
}
$programmes=$installdir+"\pyetl_dev_stable"
$env:PYETL_SITE_PARAMS=".\site_params"


