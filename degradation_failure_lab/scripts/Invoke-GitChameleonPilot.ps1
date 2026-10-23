[CmdletBinding()]
param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Invoke-ProjectCredential.ps1') -CheckOnly:$CheckOnly -Action {
    & python -B (Join-Path $PSScriptRoot 'run_gitchameleon_pilot.py')
    if ($LASTEXITCODE -ne 0) { throw 'Pilot stopped; inspect the preserved pilot_batch.json before any retry.' }
}
