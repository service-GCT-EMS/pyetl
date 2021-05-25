Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

#fenêtre
$window = New-Object System.Windows.Forms.Form
$window.Text = 'Bonjour'
$window.AutoSize = $true #wrap to content
$window.Height = 1 #Autosize agrandira la fenêtre
$window.FormBorderStyle = 3 #fenêtre à taille fixe
$window.StartPosition = 'CenterScreen'

#mise en page des champs prénom / nom
$windowLayout = New-Object System.Windows.Forms.TableLayoutPanel
$windowLayout.AutoSize = $true
$windowLayout.ColumnCount = 1
$windowLayout.RowCount = 2

#mise en page des champs prénom / nom
$nameLayout = New-Object System.Windows.Forms.FlowLayoutPanel
$nameLayout.AutoSize = $true

#label prénom
$firstnameLabel = New-Object System.Windows.Forms.Label
$firstnameLabel.Text = 'Prénom :'
$firstnameLabel.TextAlign = 256 #BottomLeft
$firstnameLabel.AutoSize = $true
$nameLayout.Controls.Add($firstnameLabel)

#champ texte prénom
$firstnameTextBox = New-Object System.Windows.Forms.TextBox
$nameLayout.Controls.Add($firstnameTextBox)

#label nom
$lastnameLabel = New-Object System.Windows.Forms.Label
$lastnameLabel.Text = 'Nom :'
$lastnameLabel.TextAlign = 256 #BottomLeft
$lastnameLabel.AutoSize = $true
$lastnameLabel.Margin = New-Object System.Windows.Forms.Padding::new(20,0,0,0) #Margin top 20
$nameLayout.Controls.Add($lastnameLabel)

#champ texte nom
$lastnameTextBox = New-Object System.Windows.Forms.TextBox
$nameLayout.Controls.Add($lastnameTextBox)

#mise en page des boutons ok / annuler
$btnLayout = New-Object System.Windows.Forms.FlowLayoutPanel
$btnLayout.AutoSize = $true
$btnLayout.Anchor = 8 #Right

$sayHelloButton = New-Object System.Windows.Forms.Button
$sayHelloButton.Text = 'Dire bonjour'
#$okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
$btnLayout.Controls.Add($sayHelloButton);

#onclick
$sayHelloButton.Add_Click(
        {    
  [System.Windows.Forms.MessageBox]::Show("Bonjour " + $firstnameTextBox.Text + " " + $lastnameTextBox.Text + " !", "Bonjour")
        }
    )

#bouton quitter
$quitButton = New-Object System.Windows.Forms.Button
$quitButton.Text = 'Quitter'
$quitButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel #Quitte le formulaire
$btnLayout.Controls.Add($quitButton);

#ajoute les groupes
$windowLayout.Controls.Add($nameLayout);
$windowLayout.Controls.Add($btnLayout);
$window.Controls.Add($windowLayout);

#montre la fenêtre
$window.ShowDialog()