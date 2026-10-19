param([string]$IntegrationDirectory = (Join-Path $PSScriptRoot '..\downstream_eval\integration'))
# All credentials in this test are disposable fakes. Docker only executes a Python environment comparison.
$ErrorActionPreference = 'Stop'
$testDirectory = Join-Path ([IO.Path]::GetTempPath()) ('autoskill-credential-test-' + [Guid]::NewGuid().ToString('N'))
$testCredentialPath = Join-Path $testDirectory 'private\zhizengzeng.dpapi'
$testPreviousKey = [Environment]::GetEnvironmentVariable('ZHIZENGZENG_API_KEY', 'Process')
$testPreviousGate = [Environment]::GetEnvironmentVariable('P1_ALLOW_PAID', 'Process')
$testFakeKey = 'FAKE_ONLY_NO_API_' + [Guid]::NewGuid().ToString('N')
$testState = @{assertions=0; prompts=0}
$testDockerExecutable = (Get-Command docker.exe -ErrorAction Stop).Source
function Assert-CredentialTest([bool]$Condition, [string]$Name) {
    if (-not $Condition) { throw ('Credential test failed: ' + $Name) }
    $testState.assertions++
}
function Assert-CredentialThrows([scriptblock]$Action, [string]$Name) {
    $testFailed = $false
    try { & $Action | Out-Null } catch { $testFailed = $true }
    Assert-CredentialTest $testFailed $Name
}
try {
    New-Item -ItemType Directory -Path $testDirectory | Out-Null
    $testHelper = Join-Path $IntegrationDirectory 'ZhizengzengCredential.ps1'
    $testLauncher = Join-Path $IntegrationDirectory 'Test-P1Connectivity.ps1'
    # Exercise the actual launcher/helper with only the credential location redirected to an isolated test directory.
    $testPathOverride = "`nfunction Get-AutoSkillCredentialPath { '$($testCredentialPath.Replace("'", "''"))' }`n"
    [IO.File]::WriteAllText((Join-Path $testDirectory 'ZhizengzengCredential.ps1'), ([IO.File]::ReadAllText($testHelper) + $testPathOverride))
    Copy-Item -LiteralPath $testLauncher -Destination $testDirectory
    . (Join-Path $testDirectory 'ZhizengzengCredential.ps1')
    $testSecure = ConvertTo-SecureString $testFakeKey -AsPlainText -Force
    try { Set-AutoSkillZhizengzengCredential $testSecure } finally { $testSecure.Dispose() }
    Assert-CredentialTest (Test-Path -LiteralPath $testCredentialPath) 'encrypted store exists'
    Assert-CredentialTest (-not [IO.File]::ReadAllText($testCredentialPath).Contains($testFakeKey)) 'store excludes plaintext'
    Test-AutoSkillPrivateAcl (Split-Path -Parent $testCredentialPath)
    Test-AutoSkillPrivateAcl $testCredentialPath
    Assert-CredentialTest $true 'directory and file have protected current-user-only ACLs'
    [Environment]::SetEnvironmentVariable('ZHIZENGZENG_API_KEY', $null, 'Process')
    Invoke-WithAutoSkillCredential {
        Assert-CredentialTest ($env:ZHIZENGZENG_API_KEY -ceq $testFakeKey) 'DPAPI round trip'
    }
    Assert-CredentialTest ([string]::IsNullOrEmpty($env:ZHIZENGZENG_API_KEY)) 'environment restored after stored load'
    Assert-CredentialThrows { Invoke-WithAutoSkillCredential { throw 'offline test failure' } } 'action failure propagates'
    Assert-CredentialTest ([string]::IsNullOrEmpty($env:ZHIZENGZENG_API_KEY)) 'environment restored after failure'
    [IO.File]::WriteAllText($testCredentialPath, 'invalid DPAPI test fixture')
    $env:ZHIZENGZENG_API_KEY = 'FAKE_ENV_PRECEDENCE_ONLY'
    Invoke-WithAutoSkillCredential {
        Assert-CredentialTest ($env:ZHIZENGZENG_API_KEY -ceq 'FAKE_ENV_PRECEDENCE_ONLY') 'environment takes precedence over corrupt store'
    }
    Assert-CredentialTest ($env:ZHIZENGZENG_API_KEY -ceq 'FAKE_ENV_PRECEDENCE_ONLY') 'caller environment preserved'
    [Environment]::SetEnvironmentVariable('ZHIZENGZENG_API_KEY', $null, 'Process')
    Assert-CredentialThrows { Get-AutoSkillZhizengzengCredential } 'corrupt store fails without fallback prompt'
    $testSecure = ConvertTo-SecureString $testFakeKey -AsPlainText -Force
    try { Set-AutoSkillZhizengzengCredential $testSecure } finally { $testSecure.Dispose() }
    $testAcl = Get-Acl -LiteralPath $testCredentialPath
    $testOtherSid = New-Object Security.Principal.SecurityIdentifier('S-1-1-0')
    $testAcl.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule($testOtherSid, 'Read', 'Allow')))
    $testFile = Get-Item -LiteralPath $testCredentialPath
    if ($PSVersionTable.PSVersion.Major -ge 6) { [IO.FileSystemAclExtensions]::SetAccessControl($testFile, $testAcl) }
    else { $testFile.SetAccessControl($testAcl) }
    Assert-CredentialThrows { Get-AutoSkillZhizengzengCredential } 'overbroad file permissions rejected'
    Set-AutoSkillPrivateAcl $testCredentialPath
    # A real container transfer with a fake credential only; no network code or model client is loaded.
    Invoke-WithAutoSkillCredential {
        $testCode = 'import hmac,json,os,sys; expected=sys.stdin.read().strip(); print(json.dumps(dict(container_matches_source=hmac.compare_digest(os.environ.get(''ZHIZENGZENG_API_KEY'',''''),expected),new_model_requests=0)))'
        $testOutput = $testFakeKey | & $testDockerExecutable exec -i --env ZHIZENGZENG_API_KEY harbor-p0-control-20261018 python -B -c $testCode
        Assert-CredentialTest ($LASTEXITCODE -eq 0) 'fake-only Docker exec succeeded'
        $testTransfer = $testOutput | ConvertFrom-Json
        Assert-CredentialTest ($testTransfer.container_matches_source -and $testTransfer.new_model_requests -eq 0) 'fake-only container transfer'
    }
    $testController = & $testDockerExecutable exec harbor-p0-control-20261018 python -B -c 'import os; print(int(bool(os.environ.get(''ZHIZENGZENG_API_KEY''))))'
    Assert-CredentialTest ($LASTEXITCODE -eq 0 -and $testController -eq '0') 'no persistent control-container credential'
    # Remaining launcher branches use a Docker stub: even --send-once cannot reach a model.
    $testDockerCalls = New-Object 'Collections.Generic.List[object]'
    $testPreflightFail = $false
    function docker {
        $testDockerCalls.Add(@($args))
        $global:LASTEXITCODE = 0
        if ($args[0] -eq 'inspect') { return 'true' }
        if ($args -contains '--send-once') {
            Assert-CredentialTest ($env:ZHIZENGZENG_API_KEY -ceq $testFakeKey) 'fake loaded at mocked request boundary'
            return '{"status":"MOCK_ONLY","new_model_requests":0}'
        }
        if ($args -contains '--run-id') {
            if ($testPreflightFail) { $global:LASTEXITCODE = 3 }
            Assert-CredentialTest ([string]::IsNullOrEmpty($env:ZHIZENGZENG_API_KEY)) 'preflight precedes credential loading'
            return '{"status":"OFFLINE_FIXTURE","request_attempts":0}'
        }
        if ($args -contains 'harbor') {
            Assert-CredentialTest ($env:ZHIZENGZENG_API_KEY -ceq $testFakeKey) 'trial wrapper loads fake credential'
            return 'MOCK_TRIAL_ONLY'
        }
        return '{"controller_persistent_credential_present":false,"new_model_requests":0}'
    }
    function Read-Host {
        $testState.prompts++
        ConvertTo-SecureString $testFakeKey -AsPlainText -Force
    }
    $testIsolatedLauncher = Join-Path $testDirectory 'Test-P1Connectivity.ps1'
    [Environment]::SetEnvironmentVariable('P1_ALLOW_PAID', $null, 'Process')
    $testOutput = & $testIsolatedLauncher -CheckOnly
    Assert-CredentialTest (($testOutput | ConvertFrom-Json).credential_available -and $testState.prompts -eq 0) 'stored credential needs no prompt'
    Assert-CredentialTest (@($testDockerCalls | Where-Object { $_ -contains '--env' }).Count -eq 0) 'offline checks never forward real credentials'
    $testCount = $testDockerCalls.Count
    Assert-CredentialThrows { & $testIsolatedLauncher -TrialConfig '/invalid.json' } 'paid gate blocks before credential or Docker access'
    Assert-CredentialTest ($testDockerCalls.Count -eq $testCount) 'blocked trial invokes no Docker'
    & $testIsolatedLauncher -SendOnce -RunId 'p1-connectivity-offline-fixture' | Out-Null
    Assert-CredentialTest (@($testDockerCalls | Where-Object { $_ -contains '--send-once' }).Count -eq 1) 'single mocked send without retry'
    $testPreflightFail = $true
    Assert-CredentialThrows { & $testIsolatedLauncher -SendOnce -RunId 'p1-connectivity-offline-fixture' } 'spent lock or failed preflight stops before credential'
    Assert-CredentialTest (@($testDockerCalls | Where-Object { $_ -contains '--send-once' }).Count -eq 1) 'failed preflight adds no request'
    $testPreflightFail = $false
    $env:P1_ALLOW_PAID = '1'
    & $testIsolatedLauncher -TrialConfig '/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-offline-fixture/configs/A1.json' | Out-Null
    Assert-CredentialTest ($env:P1_ALLOW_PAID -ceq '1') 'caller approval preserved'
    [Environment]::SetEnvironmentVariable('P1_ALLOW_PAID', $null, 'Process')
    Assert-CredentialThrows { & $testIsolatedLauncher -CheckOnly -SendOnce } 'mutually exclusive launcher modes'
    & $testIsolatedLauncher -SetCredential | Out-Null
    Assert-CredentialTest ($testState.prompts -eq 1) 'explicit setup always prompts for a new key'
    Remove-Item -LiteralPath $testCredentialPath
    & $testIsolatedLauncher -CheckOnly | Out-Null
    Assert-CredentialTest ($testState.prompts -eq 2) 'first missing credential prompts and saves'
    & $testIsolatedLauncher | Out-Null
    Assert-CredentialTest ($testState.prompts -eq 2) 'default mode is offline and subsequent load has no prompt'
    Assert-CredentialTest ([string]::IsNullOrEmpty($env:ZHIZENGZENG_API_KEY) -and [string]::IsNullOrEmpty($env:P1_ALLOW_PAID)) 'launcher restores key and never enables approval'
    [ordered]@{status='PASS'; assertions=$testState.assertions; real_model_requests=0; fake_container_transfer='PASS'; dpapi_current_user='PASS'; private_acl='PASS'; paid_gate='PASS'} | ConvertTo-Json -Compress
} finally {
    [Environment]::SetEnvironmentVariable('ZHIZENGZENG_API_KEY', $testPreviousKey, 'Process')
    [Environment]::SetEnvironmentVariable('P1_ALLOW_PAID', $testPreviousGate, 'Process')
    $testFakeKey = $null
    Remove-Item function:docker -ErrorAction SilentlyContinue
    Remove-Item function:Read-Host -ErrorAction SilentlyContinue
    $testResolved = [IO.Path]::GetFullPath($testDirectory)
    $testTempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if ($testResolved.StartsWith($testTempRoot, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $testResolved) -like 'autoskill-credential-test-*') {
        Remove-Item -LiteralPath $testResolved -Recurse -Force -ErrorAction SilentlyContinue
    }
}
