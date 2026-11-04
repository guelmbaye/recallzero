$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Offline Gate7 tests FAILED' }
python .\gate7.py status
if ($LASTEXITCODE -ne 0) { throw 'Status check FAILED' }
Write-Host 'PASS: Gate7 offline runner tests. Real evidence/model gate NOT YET RUN.'
