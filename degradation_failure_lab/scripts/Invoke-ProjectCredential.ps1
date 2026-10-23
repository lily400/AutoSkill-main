[CmdletBinding()]
param([switch]$CheckOnly, [Alias('Action')][scriptblock]$Command)
$ErrorActionPreference = 'Stop'
$gchLab = Split-Path -Parent $PSScriptRoot
$gchConfig = Get-Content -LiteralPath (Join-Path $gchLab 'configs/credentials.json') -Raw | ConvertFrom-Json
$gchProvider = $gchConfig.providers.zhizengzeng
if ($gchProvider.loader.type -ne 'windows_currentuser_dpapi' -or $gchProvider.environment_variable -ne 'ZHIZENGZENG_API_KEY') { throw 'Unexpected credential configuration.' }
. (Join-Path $gchLab $gchProvider.loader.script)
if ([string]::IsNullOrWhiteSpace($env:ZHIZENGZENG_API_KEY) -and -not (Test-Path -LiteralPath (Get-AutoSkillCredentialPath))) {
    throw 'Saved credential is absent. Use the documented one-time SetCredential command; no prompt or model request was opened.'
}
Invoke-WithAutoSkillCredential {
    if ($CheckOnly) {
        [ordered]@{ credential_available = -not [string]::IsNullOrWhiteSpace($env:ZHIZENGZENG_API_KEY); configured_provider = 'zhizengzeng'; persistent_storage = 'Windows CurrentUser DPAPI'; new_model_requests = 0 } | ConvertTo-Json -Compress
    } elseif ($null -ne $Command) {
        & $Command
    } else { throw 'Specify -CheckOnly or -Action.' }
}
