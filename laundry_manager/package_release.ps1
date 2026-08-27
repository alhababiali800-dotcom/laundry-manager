$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$zip = Join-Path $root 'InternationalLaundries-Windows-corrected.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $root 'dist\InternationalLaundries') -DestinationPath $zip -Force
Write-Output $zip
