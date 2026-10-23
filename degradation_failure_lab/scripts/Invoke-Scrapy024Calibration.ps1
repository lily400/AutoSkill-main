[CmdletBinding()]
param([string]$Experiment = 's24d001')
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Invoke-ProjectCredential.ps1') -Action {
    & python -B (Join-Path $PSScriptRoot 'scrapy024.py') run --experiment $Experiment
    if ($LASTEXITCODE -ne 0) { throw 'Calibration stopped. Preserve its ledger and results; do not resend or restart.' }
}
