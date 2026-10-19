[CmdletBinding(DefaultParameterSetName = 'Check')]
param(
    [Parameter(ParameterSetName = 'Check')][switch]$CheckOnly,
    [Parameter(Mandatory = $true, ParameterSetName = 'Set')][switch]$SetCredential,
    [Parameter(Mandatory = $true, ParameterSetName = 'Connectivity')][switch]$SendOnce,
    [Parameter(ParameterSetName = 'Connectivity')]
    [ValidatePattern('^p1-connectivity-[A-Za-z0-9_-]+$')][string]$RunId = 'p1-connectivity-20261019-001',
    [Parameter(Mandatory = $true, ParameterSetName = 'Trial')][string]$TrialConfig
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ZhizengzengCredential.ps1')
$taskMode = $PSCmdlet.ParameterSetName
$taskContainer = 'harbor-p0-control-20261018'
if ($SetCredential) {
    Set-AutoSkillZhizengzengCredential
    Write-Output 'Credential saved with Windows CurrentUser DPAPI and a user-only ACL. No API request sent.'
    return
}
if ($PSCmdlet.ParameterSetName -eq 'Trial') {
    if ([Environment]::GetEnvironmentVariable('P1_ALLOW_PAID', 'Process') -cne '1') {
        throw 'Paid trials require separate approval and an existing P1_ALLOW_PAID=1. No credential loaded or request sent.'
    }
    if ($TrialConfig -notmatch '^/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-[A-Za-z0-9_-]+/configs/(A0|A1|Gold)\.json$') {
        throw 'Use an existing prepared P1 TrialConfig container path (A0, A1 or Gold).'
    }
}
$taskRunning = & docker inspect $taskContainer --format '{{.State.Running}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker and the existing Harbor control container must be running first.' }
if ($taskRunning -ne 'true') {
    & docker start $taskContainer | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'The existing Harbor control container could not be started.' }
}
if ($SendOnce) {
    # Preflight and the existing durable one-request lock run before any credential is loaded.
    & docker exec $taskContainer python -B -m downstream_eval.integration.model_connectivity --run-id $RunId
    if ($LASTEXITCODE -ne 0) { throw 'No-request preflight failed. No credential loaded or model request sent.' }
}
Invoke-WithAutoSkillCredential {
    if ($SendOnce) {
        & docker exec --env ZHIZENGZENG_API_KEY $taskContainer python -B -m downstream_eval.integration.model_connectivity --run-id $RunId --send-once
    } elseif ($taskMode -eq 'Trial') {
        & docker exec --env ZHIZENGZENG_API_KEY --env P1_ALLOW_PAID $taskContainer harbor trials start --config $TrialConfig
    } else {
        # Real credentials stay on Windows during offline checks; fake-key transfer is covered by the test script.
        $taskCheckCode = 'import json,os; print(json.dumps(dict(controller_persistent_credential_present=bool(os.environ.get(''ZHIZENGZENG_API_KEY'')),new_model_requests=0)))'
        $taskOutput = & docker exec $taskContainer python -B -c $taskCheckCode
        if ($LASTEXITCODE -ne 0) { throw 'The offline control-container check failed.' }
        $taskCheck = $taskOutput | ConvertFrom-Json
        if ($taskCheck.controller_persistent_credential_present) { throw 'The control container unexpectedly has a persistent credential; offline check stopped.' }
        [ordered]@{credential_available=$true; credential_forwarded=$false; new_model_requests=0; P1_ALLOW_PAID_changed=$false} | ConvertTo-Json -Compress
        return
    }
    if ($LASTEXITCODE -ne 0) { throw 'Harbor execution stopped. Inspect the saved result before any separately approved retry.' }
}
