<# This form was created using POSHGUI.com  a free online gui designer for PowerShell
.NAME
    Untitled
#>

Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::EnableVisualStyles()
$font = New-Object System.Drawing.Font('Microsoft Sans Serif', 10)
$startx = 40

$Form = New-Object system.Windows.Forms.Form
$Form.ClientSize = New-Object System.Drawing.Point(400, 400)
$Form.text = "export prod vers dev"
$Form.TopMost = $false

$Label1 = New-Object system.Windows.Forms.Label
$Label1.text = "fichier de definition de couches"
$Label1.AutoSize = $true
$Label1.location = New-Object System.Drawing.Point($startx, 50)
$Label1.Font = $font


$TextBox1 = New-Object system.Windows.Forms.TextBox
$TextBox1.multiline = $false
$TextBox1.width = 300
$TextBox1.height = 20
$TextBox1.location = New-Object System.Drawing.Point($startx, 90)
$TextBox1.Font = $font
$textbox1.AllowDrop = $true

$FileBrowser1 = New-Object System.Windows.Forms.OpenFileDialog
$FileBrowser1.Title = 'fichier de definition de couches'
$FileBrowser1.Filter = 'fichiers csv|*.csv|Projets QGIS|*.qgs'

$FileButton1 = New-Object system.Windows.Forms.Button
$FileButton1.text = "f"
$FileButton1.width = 24
$FileButton1.height = 24
$FileButton1.location = New-Object System.Drawing.Point(350, 90)
$FileButton1.Font = $font


#onclick
$FileButton1.Add_Click(
    {
        $startdir = "."
        if ($TextBox1.Text -ne '') { $startdir = Split-Path -Path $TextBox1.Text }
        $FileBrowser1.InitialDirectory = $startdir
        $null = $FileBrowser1.ShowDialog()
        $TextBox1.Text = $FileBrowser1.FileName
        $TextBox1.Update()

    }
)


$LabelS1 = New-Object system.Windows.Forms.Label
$LabelS1.text = "origine"
$LabelS1.AutoSize = $true
$LabelS1.location = New-Object System.Drawing.Point($startx, 130)
$LabelS1.Font = $font


$Select1 = New-Object system.Windows.Forms.ComboBox
$t = $select1.Items.Add("sigli_prod")
$t = $select1.Items.Add("siglc_prod")
$t = $select1.Items.Add("sigli_dageo")
$t = $select1.Items.Add("sigli_ddref")
$t = $select1.Items.Add("sigli_devco")
$t = $select1.Items.Add("sigli_prod")
$t = $select1.Items.Add("sigli_sesvn")
$t = $select1.Items.Add("sigli_sig3d")
$t = $select1.Items.Add("sigli_sprop")
$t = $select1.Items.Add("sigli_stag1")
$t = $select1.Items.Add("sigli_stag2")
$t = $select1.Items.Add("sigli_svoip")
$t = $select1.Items.Add("sigli_test")
$t = $select1.Items.Add("sigli_usag1")
$t = $select1.Items.Add("sigli_usag2")
$t = $select1.Items.Add("sigli_usag3")
$t = $select1.Items.Add("sigli_usag4")
$t = $select1.Items.Add("sigli_usag5")
$t = $select1.Items.Add("sigli_usag6")
$t = $select1.Items.Add("sigli_usag7")


$select1.location = New-Object System.Drawing.Point($startx, 150)
$select1.width = 100
$select1.height = 40
$select1.Font = $font

$LabelS2 = New-Object system.Windows.Forms.Label
$LabelS2.text = "destination"
$LabelS2.AutoSize = $true
$LabelS2.location = New-Object System.Drawing.Point(150, 130)
$LabelS2.Font = $font


$Select2 = New-Object system.Windows.Forms.ComboBox

$t = $Select2.Items.Add("sigli_dageo")
$t = $Select2.Items.Add("sigli_ddref")
$t = $Select2.Items.Add("sigli_devco")
$t = $Select2.Items.Add("sigli_prod")
$t = $Select2.Items.Add("sigli_sesvn")
$t = $Select2.Items.Add("sigli_sig3d")
$t = $Select2.Items.Add("sigli_sprop")
$t = $Select2.Items.Add("sigli_stag1")
$t = $Select2.Items.Add("sigli_stag2")
$t = $Select2.Items.Add("sigli_svoip")
$t = $Select2.Items.Add("sigli_test")
$t = $Select2.Items.Add("sigli_usag1")
$t = $Select2.Items.Add("sigli_usag2")
$t = $Select2.Items.Add("sigli_usag3")
$t = $Select2.Items.Add("sigli_usag4")
$t = $Select2.Items.Add("sigli_usag5")
$t = $Select2.Items.Add("sigli_usag6")
$t = $Select2.Items.Add("sigli_usag7")

$Select2.location = New-Object System.Drawing.Point(150, 150)
$Select2.width = 100
$Select2.height = 40
$Select2.Font = $font

$Label3 = New-Object system.Windows.Forms.Label
$Label3.text = " "
$Label3.AutoSize = $true
$Label3.location = New-Object System.Drawing.Point($startx, 270)
$Label3.Font = $font


$Button1 = New-Object system.Windows.Forms.Button
$Button1.text = "extraire les données"
$Button1.width = 100
$Button1.height = 40
$Button1.location = New-Object System.Drawing.Point($startx, 200)
$Button1.Font = $font
$Button1.UseWaitCursor = $true
#onclick
$Button1.Add_Click(
    {
        #$Button1.UseWaitCursor           = $true
        #$Button1.Refresh()
        $listeclasse = $TextBox1.Text
        $sortie_res = Split-Path -Path $listeclasse
        $orig = $select1.SelectedItem
        $label3.Text = 'export'
        $label3.Refresh()
        mapper.ps1 -#dbextract acces=$orig niveau=in:$listeclasse $sortie_res/export format=sql:sigli format_schema=sql
        $label3.Text = 'fin export'
        $label3.Refresh()
        #$Button1.UseWaitCursor           = $false
        #$Button1.Refresh()
    }
)


$Button2 = New-Object system.Windows.Forms.Button
$Button2.text = "creer le schema"
$Button2.width = 100
$Button2.height = 40
$Button2.location = New-Object System.Drawing.Point(150, 200)
$Button2.Font = $font
$Button2.UseWaitCursor = $true
#onclick
$Button2.Add_Click(
    {
        $label3.Text = 'creation structure'
        $label3.Refresh()
        $dest = $select2.SelectedItem
        mapper.ps1 -#runsql dest=$dest nom=$sortie_res/export/schemas/0*
        $label3.Text = 'fin creation'
        $label3.Refresh()
    }
)


$Button3 = New-Object system.Windows.Forms.Button
$Button3.text = "importer les donnees"
$Button3.width = 100
$Button3.height = 40
$Button3.location = New-Object System.Drawing.Point(260, 200)
$Button3.Font = $font
$Button3.UseWaitCursor = $true
#onclick
$Button3.Add_Click(
    {
        $label3.Text = 'chargement'
        $label3.Refresh()
        $dest = $select2.SelectedItem
        mapper.ps1 -#runsql dest=$dest nom=$sortie_res/export/all.sql
        $label3.Text = 'fin chargement'
        $label3.Refresh()
    }
)






$ButtonX = New-Object system.Windows.Forms.Button
$ButtonX.text = "quitter"
$ButtonX.width = 100
$ButtonX.height = 30
$ButtonX.location = New-Object System.Drawing.Point(260, 300)
$ButtonX.Font = $font
$ButtonX.DialogResult = [System.Windows.Forms.DialogResult]::Cancel #Quitte le formulaire



$Form.controls.AddRange(@($TextBox1, $Label1, $FileButton1, $CheckBox1, $select1, $LabelS1, $select2, $LabelS2,
        $Button1, $Button2, $Button3, $ButtonX, $label3))
$form.ShowDialog()
