param(
    [Parameter(Mandatory = $true)][string]$SourceRef,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
foreach ($name in @('Setup.cs', 'Install-Writer.ps1')) {
    $committed = (& git -C $repo rev-parse "${SourceRef}:installer/$name")
    if ($LASTEXITCODE -ne 0) { throw "Installer source not found in $SourceRef." }
    $working = (& git -C $repo hash-object (Join-Path $PSScriptRoot $name))
    if ($LASTEXITCODE -ne 0 -or $committed -ne $working) { throw "Installer source differs from $SourceRef`: $name" }
}
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (-not (Test-Path -LiteralPath $output -PathType Container)) { throw 'Output directory does not exist.' }
$exe = Join-Path $output 'Writer-Translator-Setup.exe'
if (Test-Path -LiteralPath $exe) { throw 'Installer already exists; choose an empty output directory.' }
$stage = Join-Path $output ('writer-setup-build-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stage | Out-Null
$payload = Join-Path $stage 'payload.zip'
& git -C $repo archive --format=zip --prefix=Writer-Translator/ "--output=$payload" $SourceRef -- 'Start Local Writer.bat' app requirements-argos.txt README.md
if ($LASTEXITCODE -ne 0) { throw 'Could not create the application payload from the selected commit.' }
$csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $csc -PathType Leaf)) { throw 'The .NET Framework C# compiler is unavailable.' }
& $csc /nologo /target:winexe "/out:$exe" '/reference:System.Windows.Forms.dll' "/resource:$payload,writer.payload" "/resource:$(Join-Path $PSScriptRoot 'Install-Writer.ps1'),writer.setup" (Join-Path $PSScriptRoot 'Setup.cs')
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Could not build the Windows installer.' }
Get-FileHash -LiteralPath $exe -Algorithm SHA256
