[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('plan','freeze','prepare','run','status','analyze')][string]$Phase,
    [Parameter(Mandatory = $true)][string]$Task,
    [string]$GeneratorRun,
    [string]$Experiment,
    [string]$Output,
    [switch]$Watch
)
$ErrorActionPreference = 'Stop'
$pilotArguments = @('-B', (Join-Path $PSScriptRoot 'pilot.py'), $Phase, '--task', $Task)
if ($GeneratorRun) { $pilotArguments += @('--generator-run', $GeneratorRun) }
if ($Experiment) { $pilotArguments += @('--experiment', $Experiment) }
if ($Output) { $pilotArguments += @('--output', $Output) }
if ($Watch) { $pilotArguments += '--watch' }
if ($Phase -eq 'run') {
    & (Join-Path (Split-Path $PSScriptRoot -Parent) 'Invoke-ProjectCredential.ps1') -Action {
        & python @pilotArguments
        if ($LASTEXITCODE -ne 0) { throw 'Pilot stopped. Preserve its ledger; do not restart.' }
    }
} else {
    & python @pilotArguments
    if ($LASTEXITCODE -ne 0) { throw 'Pilot command failed; inspect its output.' }
}
