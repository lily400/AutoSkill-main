[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Task,
    [Parameter(Mandatory=$true)][ValidateSet('generate','evaluate','analyze','status')][string]$Phase,
    [switch]$Approve
)
$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$queue = Get-Content -LiteralPath (Join-Path $labRoot 'configs/sgb/clean10.json') -Raw | ConvertFrom-Json
$selected = @($queue.tasks | Where-Object { $_.task_id -eq $Task })
if ($selected.Count -ne 1 -or $selected[0].status -ne 'READY') { throw 'One READY task in clean10.json is required.' }
$entry = $selected[0]
$binding = Get-Content -LiteralPath (Join-Path $labRoot "configs/tasks/sgb/$Task.json") -Raw | ConvertFrom-Json
if ($binding.adapter -notin @('downstream_eval.sgb.task_adapters.audited.json_task','downstream_eval.sgb.task_adapters.audited.code_task')) { throw 'Use the existing pilot command for this legacy adapter.' }
function Invoke-LabPython {
    param([string[]]$Arguments)
    & python -B @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'Command stopped. Inspect retained evidence; no automatic retry or resume.' }
}
$generation = Join-Path $labRoot "runs/gen/sgb/$($entry.case_id)/clean/$($entry.generator_run_id)"
$experiment = Join-Path $labRoot "runs/eval/sgb/$Task/$($entry.planned_experiment_id)"
if ($Phase -eq 'generate') {
    if (Test-Path -LiteralPath $generation) { throw 'Generation identity already exists; inspect it instead of regenerating.' }
    $arguments = @((Join-Path $PSScriptRoot 'authorize_generation.py'),'--case',$entry.case_id,'--run-id',$entry.generator_run_id)
    if ($Approve) { $arguments += '--approve' }
    Invoke-LabPython -Arguments $arguments
    if (-not $Approve) { return }
    if ([string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) { $env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User') }
    if ([string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) { throw 'DEEPSEEK_API_KEY is unavailable; no model request started.' }
    Invoke-LabPython -Arguments @((Join-Path $labRoot 'scripts/lab.py'),'run','--case',$entry.case_id,'--condition','clean','--repeat','1','--run-id',$entry.generator_run_id)
    Write-Output "Generation finished. Next: -Task $Task -Phase evaluate -Approve"
    return
}
if ($Phase -eq 'evaluate') {
    if (Test-Path -LiteralPath $experiment) { throw 'Experiment identity already exists; use status/analyze and preserve its ledger.' }
    $arguments = @((Join-Path $PSScriptRoot 'authorize_downstream.py'),'--task',$Task,'--generator-run',$entry.generator_run_id,'--experiment',$entry.planned_experiment_id)
    if ($Approve) { $arguments += '--approve' }
    Invoke-LabPython -Arguments $arguments
    if (-not $Approve) { return }
    & (Join-Path $PSScriptRoot 'Invoke-Pilot.ps1') -Phase prepare -Task $Task -GeneratorRun $entry.generator_run_id -Experiment $entry.planned_experiment_id
    & (Join-Path $PSScriptRoot 'Invoke-Pilot.ps1') -Phase run -Task $Task -Experiment $entry.planned_experiment_id
}
if ($Phase -eq 'status') {
    & (Join-Path $PSScriptRoot 'Invoke-Pilot.ps1') -Phase status -Task $Task -Experiment $entry.planned_experiment_id
    return
}
$analysis = "results/sgb/analyses/$($entry.planned_experiment_id)"
& (Join-Path $PSScriptRoot 'Invoke-Pilot.ps1') -Phase analyze -Task $Task -Experiment $entry.planned_experiment_id -Output $analysis
$stamp = Get-Date -Format 'yyyyMMdd-HHmmssfff'
Invoke-LabPython -Arguments @((Join-Path $labRoot 'scripts/lab.py'),'sgb','cohort','--config','configs/sgb/clean10.json','--output',"results/sgb/analyses/clean10-$($entry.planned_experiment_id)-$stamp")
