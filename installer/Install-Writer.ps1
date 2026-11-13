param([string]$VerifyDestination)
$ErrorActionPreference = 'Stop'
$payload = Join-Path $PSScriptRoot 'payload.zip'

function Install-Writer([string]$parent) {
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'Choose an existing installation folder.' }
    $target = Join-Path ([IO.Path]::GetFullPath($parent)) 'Writer-Translator'
    if (Test-Path -LiteralPath $target) { throw 'Writer-Translator already exists there. Choose another folder to keep existing files safe.' }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($payload)
    try {
        foreach ($entry in $archive.Entries) {
            if ($entry.FullName -notmatch '^Writer-Translator/' -or $entry.FullName -match '(^/|^[A-Za-z]:|(^|/)\.\.(/|$)|[\\:])') { throw 'The installation package contains an unsafe path.' }
        }
        New-Item -ItemType Directory -Path $target -ErrorAction Stop | Out-Null
        foreach ($entry in $archive.Entries) {
            $relative = $entry.FullName.Substring('Writer-Translator/'.Length)
            if (-not $relative) { continue }
            $destination = Join-Path $target $relative
            if ($entry.FullName.EndsWith('/')) { [IO.Directory]::CreateDirectory($destination) | Out-Null; continue }
            [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($destination)) | Out-Null
            $inputStream = $entry.Open()
            try {
                $outputStream = [IO.File]::Open($destination, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
                try { $inputStream.CopyTo($outputStream) } finally { $outputStream.Dispose() }
            } finally { $inputStream.Dispose() }
        }
    } finally { $archive.Dispose() }
    if (-not (Test-Path -LiteralPath (Join-Path $target 'Start Local Writer.bat') -PathType Leaf)) { throw 'Installation is incomplete; the launcher is missing.' }
    return $target
}

if ($VerifyDestination) {
    Install-Writer $VerifyDestination
    exit 0
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object Windows.Forms.Form
$form.Text = 'Writer & Translator Setup'
$form.Size = New-Object Drawing.Size(620, 510)
$form.MinimumSize = $form.Size
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$title = New-Object Windows.Forms.Label
$title.Text = 'Install Writer & Translator'
$title.Font = New-Object Drawing.Font('Segoe UI', 14, [Drawing.FontStyle]::Bold)
$title.SetBounds(24, 20, 550, 35)
$form.Controls.Add($title)
$description = New-Object Windows.Forms.Label
$description.Text = 'Choose where to create the Writer-Translator folder. Existing folders will not be overwritten.'
$description.SetBounds(26, 65, 550, 42)
$form.Controls.Add($description)
$pathBox = New-Object Windows.Forms.TextBox
$pathBox.SetBounds(26, 112, 438, 28)
$pathBox.Text = [Environment]::GetFolderPath('MyDocuments')
$form.Controls.Add($pathBox)
$browse = New-Object Windows.Forms.Button
$browse.Text = 'Browse...'; $browse.SetBounds(475, 110, 100, 30)
$browse.Add_Click({ $dialog = New-Object Windows.Forms.FolderBrowserDialog; $dialog.Description = 'Select the parent folder for Writer & Translator'; if ($dialog.ShowDialog($form) -eq [Windows.Forms.DialogResult]::OK) { $pathBox.Text = $dialog.SelectedPath }; $dialog.Dispose() })
$form.Controls.Add($browse)
$instructions = New-Object Windows.Forms.Label
$instructions.Text = "Requirements (not installed automatically):`r`n- Python 3 is needed to start the application.`r`n- For Gemma, install and start Ollama; use Manage models and confirm the model download.`r`n- For Argos, follow the in-app setup guidance and confirm the language package download.`r`nInternet and disk space are required for these optional downloads."
$instructions.SetBounds(26, 165, 550, 140)
$form.Controls.Add($instructions)
$pythonLink = New-Object Windows.Forms.LinkLabel
$pythonLink.Text = 'Official Python download'; $pythonLink.SetBounds(26, 310, 180, 25)
$pythonLink.Add_LinkClicked({ Start-Process 'https://www.python.org/downloads/' })
$form.Controls.Add($pythonLink)
$ollamaLink = New-Object Windows.Forms.LinkLabel
$ollamaLink.Text = 'Official Ollama download'; $ollamaLink.SetBounds(220, 310, 180, 25)
$ollamaLink.Add_LinkClicked({ Start-Process 'https://ollama.com/download' })
$form.Controls.Add($ollamaLink)
$install = New-Object Windows.Forms.Button
$install.Text = 'Install'; $install.SetBounds(365, 395, 100, 34)
$install.Add_Click({
    try {
        $install.Enabled = $false
        $target = Install-Writer $pathBox.Text
        [Windows.Forms.MessageBox]::Show($form, "Installed in:`r`n$target`r`n`r`nOpen Start Local Writer.bat in that folder to start.", 'Installation complete', 'OK', 'Information') | Out-Null
        & cmd.exe /d /c 'python --version >nul 2>&1'
        $pythonAvailable = $LASTEXITCODE -eq 0
        if (-not $pythonAvailable) {
            $answer = [Windows.Forms.MessageBox]::Show($form, 'Python was not found. It is required to start Writer & Translator. Open the official Python download page?', 'Python required', 'YesNo', 'Question')
            if ($answer -eq [Windows.Forms.DialogResult]::Yes) { Start-Process 'https://www.python.org/downloads/' }
        }
        if (-not (Get-Command 'ollama.exe' -ErrorAction SilentlyContinue)) {
            $answer = [Windows.Forms.MessageBox]::Show($form, 'Ollama was not found on PATH. It is needed to write with Gemma. Open the official Ollama download page?', 'Ollama', 'YesNo', 'Question')
            if ($answer -eq [Windows.Forms.DialogResult]::Yes) { Start-Process 'https://ollama.com/download' }
        }
        if ($pythonAvailable) {
            & cmd.exe /d /c 'python -c "import argostranslate" >nul 2>&1'
            if ($LASTEXITCODE -ne 0) {
                $answer = [Windows.Forms.MessageBox]::Show($form, 'The Argos Python package was not found. Show instructions for installing it yourself?', 'Argos Translate', 'YesNo', 'Question')
                if ($answer -eq [Windows.Forms.DialogResult]::Yes) {
                    [Windows.Forms.MessageBox]::Show($form, "Open Command Prompt in the installation folder and run:`r`npython -m pip install -r requirements-argos.txt`r`n`r`nRestart the app, then confirm installation of the language package when offered. These downloads need internet.", 'Argos setup', 'OK', 'Information') | Out-Null
                }
            }
        }
        $form.Close()
    } catch {
        [Windows.Forms.MessageBox]::Show($form, $_.Exception.Message, 'Installation failed', 'OK', 'Error') | Out-Null
        $install.Enabled = $true
    }
})
$form.Controls.Add($install)
$cancel = New-Object Windows.Forms.Button
$cancel.Text = 'Cancel'; $cancel.SetBounds(475, 395, 100, 34)
$cancel.Add_Click({ $form.Close() })
$form.Controls.Add($cancel)
$form.AcceptButton = $install; $form.CancelButton = $cancel
[void]$form.ShowDialog()
$form.Dispose()
