
# fileselector pour le repertoire de sortie
Add-Type -AssemblyName System.Windows.Forms
$FileBrowser = New-Object System.Windows.Forms.OpenFileDialog -Property @{ InitialDirectory = [Environment]::GetFolderPath('Desktop') }
$FileBrowser.Title = 'projet qgis a traiter'
$FileBrowser.Filter = 'Projets QGIS|*.qgs'
$null = $FileBrowser.ShowDialog()
$projetqgis=$FileBrowser.FileName

$FileBrowser2 = New-Object System.Windows.Forms.OpenFileDialog 
$FileBrowser2.InitialDirectory = Split-Path -Path $projetqgis
$FileBrowser2.Title = 'repertoire de sortie'
$FileBrowser2.ValidateNames = 0
$FileBrowser2.CheckFileExists = 0
$FileBrowser2.CheckPathExists = 1
$FileBrowser2.FileName = "Folder Selection.";
$null = $FileBrowser2.ShowDialog()
$sortie_res=Split-Path -Path $FileBrowser2.FileName

mapper.ps1 -#dbschema niveau=in:$projetqgis sortie_schema=$sortie_res/parametres


python autres/project_converter.py $projetqgis limit $sortie_res/standalone