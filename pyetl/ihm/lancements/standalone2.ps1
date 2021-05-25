<# This form was created using POSHGUI.com  a free online gui designer for PowerShell
.NAME
    Untitled
#>

Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::EnableVisualStyles()
$font=New-Object System.Drawing.Font('Microsoft Sans Serif',10)
$startx=40

$Form                            = New-Object system.Windows.Forms.Form
$Form.ClientSize                 = New-Object System.Drawing.Point(400,400)
$Form.text                       = "creation standalone"
$Form.TopMost                    = $false

$Label1                          = New-Object system.Windows.Forms.Label
$Label1.text                     = "fichier projet"
$Label1.AutoSize                 = $true
$Label1.location                 = New-Object System.Drawing.Point($startx,50)
$Label1.Font                     = $font


$TextBox1                        = New-Object system.Windows.Forms.TextBox
$TextBox1.multiline              = $false
$TextBox1.width                  = 300
$TextBox1.height                 = 20
$TextBox1.location               = New-Object System.Drawing.Point($startx,90)
$TextBox1.Font                   = $font
$textbox1.AllowDrop              = $true

$FileBrowser1 = New-Object System.Windows.Forms.OpenFileDialog 
$FileBrowser1.Title = 'projet qgis a traiter'
$FileBrowser1.Filter = 'Projets QGIS|*.qgs'

$FileButton1                         = New-Object system.Windows.Forms.Button
$FileButton1.text                    = "f"
$FileButton1.width                   = 20
$FileButton1.height                  = 20
$FileButton1.location                = New-Object System.Drawing.Point(350,90)
$FileButton1.Font                    = $font

#onclick
$FileButton1.Add_Click(
    {
        $startdir="."
        if ($TextBox1.Text -ne '') { $startdir=Split-Path -Path $TextBox1.Text }
        $FileBrowser1.InitialDirectory=$startdir
        $null = $FileBrowser1.ShowDialog()
        $TextBox1.Text = $FileBrowser1.FileName
        $TextBox1.Update()
        
    }
    )





$CheckBox1                       = New-Object system.Windows.Forms.CheckBox
$CheckBox1.text                  = "emprise limitee"
$CheckBox1.AutoSize              = $true
$CheckBox1.Checked               = $true
$CheckBox1.location              = New-Object System.Drawing.Point($startx,150)
$CheckBox1.Font                  = $font

$Label2                          = New-Object system.Windows.Forms.Label
$Label2.text                     = "repertoire destination"
$Label2.AutoSize                 = $true
$Label2.location                 = New-Object System.Drawing.Point($startx,200)
$Label2.Font                     = $font


$TextBox2                        = New-Object system.Windows.Forms.TextBox
$TextBox2.multiline              = $false
$TextBox2.width                  = 300
$TextBox2.height                 = 20
$TextBox2.location               = New-Object System.Drawing.Point($startx,240)
$TextBox2.Font                   = $font


$FileBrowser2 = New-Object System.Windows.Forms.OpenFileDialog 
$FileBrowser2.Title = 'Repertoire destination'
$FileBrowser2.ValidateNames = $false
$FileBrowser2.CheckFileExists = $false
$FileBrowser2.CheckPathExists = $true
$FileBrowser2.FileName = "répertoire"

$FileButton2                         = New-Object system.Windows.Forms.Button
$FileButton2.text                    = "f"
$FileButton2.width                   = 20
$FileButton2.height                  = 20
$FileButton2.location                = New-Object System.Drawing.Point(350,240)
$FileButton2.Font                    = $font

#onclick
$FileButton2.Add_Click(
    {
        $startdir="."
        if ($TextBox1.Text -ne '') { $startdir=Split-Path -Path $TextBox1.Text }
        $FileBrowser2.InitialDirectory=$startdir
        $null = $FileBrowser2.ShowDialog()
        $TextBox2.Text = Split-Path -Path $FileBrowser2.FileName
        $TextBox2.Update()
        
    }
    )



$Label3                          = New-Object system.Windows.Forms.Label
$Label3.text                     = " "
$Label3.AutoSize                 = $true
$Label3.location                 = New-Object System.Drawing.Point($startx,270)
$Label3.Font                     = $font






$Button1                         = New-Object system.Windows.Forms.Button
$Button1.text                    = "demarrer"
$Button1.width                   = 100
$Button1.height                  = 30
$Button1.location                = New-Object System.Drawing.Point($startx,300)
$Button1.Font                    = $font
#onclick
$Button1.Add_Click(
        {
        $projetqgis=$TextBox1.Text
        $sortie_res=$TextBox2.Text
        $limite=$CheckBox1.Checked
        $label3.Text='analyse fichiers'
        $label3.Refresh()
        mapper.ps1 -#dbschema niveau=in:$projetqgis sortie_schema=$sortie_res/parametres
        $label3.Text='creation standalone'
        $label3.Refresh()
        if ($limite) { python autres/project_converter.py $projetqgis limit $sortie_res/standalone }
        else { python autres/project_converter.py $projetqgis nolimit $sortie_res/standalone }
        $label3.Text='fin de traitement'
        $label3.Refresh()
        }
    )

$Button2                         = New-Object system.Windows.Forms.Button
$Button2.text                    = "quitter"
$Button2.width                   = 100
$Button2.height                  = 30
$Button2.location                = New-Object System.Drawing.Point(250,300)
$Button2.Font                    = $font
$Button2.DialogResult = [System.Windows.Forms.DialogResult]::Cancel #Quitte le formulaire



$Form.controls.AddRange(@($TextBox1,$Label1,$FileButton1,$CheckBox1,$Label2,$TextBox2,
                            $FileButton2,$Button1,$Button2, $label3))
$form.ShowDialog()

