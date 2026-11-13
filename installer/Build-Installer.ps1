param(
    [Parameter(Mandatory = $true)][string]$SourceRef,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
foreach ($name in @('Setup.cmd', 'Install-Writer.ps1')) {
    $committed = (& git -C $repo rev-parse "${SourceRef}:installer/$name")
    if ($LASTEXITCODE -ne 0) { throw "Installer source not found in $SourceRef." }
    $working = (& git -C $repo hash-object (Join-Path $PSScriptRoot $name))
    if ($LASTEXITCODE -ne 0 -or $committed -ne $working) { throw "Installer source differs from $SourceRef`: $name" }
}
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (-not (Test-Path -LiteralPath $output -PathType Container)) { throw 'Output directory does not exist.' }
$stage = Join-Path $output ('writer-setup-build-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stage | Out-Null
$payload = Join-Path $stage 'payload.zip'
& git -C $repo archive --format=zip --prefix=Writer-Translator/ "--output=$payload" $SourceRef -- 'Start Local Writer.bat' app requirements-argos.txt README.md
if ($LASTEXITCODE -ne 0) { throw 'Could not create the application payload from the selected commit.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Setup.cmd'), (Join-Path $PSScriptRoot 'Install-Writer.ps1') -Destination $stage
$exe = Join-Path $output 'Writer-Translator-Setup.exe'
if (Test-Path -LiteralPath $exe) { throw 'Installer already exists; choose an empty output directory.' }
$sed = Join-Path $stage 'setup.sed'
$config = @"
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles
[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=$exe
FriendlyName=Writer and Translator Setup
AppLaunched=cmd /c Setup.cmd
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
FILE0="Setup.cmd"
FILE1="Install-Writer.ps1"
FILE2="payload.zip"
[SourceFiles]
SourceFiles0=$stage\
[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=
"@
if ($config -cmatch '[^\x00-\x7f]') { throw 'IExpress requires an ASCII-only build path; choose another output directory.' }
Set-Content -LiteralPath $sed -Value $config -Encoding Ascii
$result = Start-Process -FilePath (Join-Path $env:SystemRoot 'System32\iexpress.exe') -ArgumentList @('/N', ('"' + $sed + '"')) -WindowStyle Hidden -Wait -PassThru
if ($result.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "IExpress failed (exit $($result.ExitCode))." }
Get-FileHash -LiteralPath $exe -Algorithm SHA256
