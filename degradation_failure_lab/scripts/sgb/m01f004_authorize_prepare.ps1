$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'D:\AS\AutoSkill-main\degradation_failure_lab'

python -B .\scripts\sgb\authorize_downstream.py `
    --task monitoring_gap_brief_classifier_001 `
    --generator-run m01g001 `
    --experiment m01f004 `
    --approve
if ($LASTEXITCODE -ne 0) { throw 'Authorization failed; do not prepare.' }

& .\scripts\sgb\Invoke-Pilot.ps1 `
    -Phase prepare `
    -Task monitoring_gap_brief_classifier_001 `
    -GeneratorRun m01g001 `
    -Experiment m01f004
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed; preserve evidence and do not run.' }
