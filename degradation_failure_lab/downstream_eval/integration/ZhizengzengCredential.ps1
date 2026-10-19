# Windows DPAPI (CurrentUser): never use -Key, plaintext files or user/machine environment variables.
function Get-AutoSkillCredentialPath {
    Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'AutoSkill\credentials\zhizengzeng.dpapi'
}

function Set-AutoSkillPrivateAcl([string]$Path) {
    $taskSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $taskItem = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($taskItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Credential links are not supported.' }
    $taskInheritance = [Security.AccessControl.InheritanceFlags]::None
    $taskAcl = Get-Acl -LiteralPath $Path -ErrorAction Stop
    if ($taskItem.PSIsContainer) {
        $taskInheritance = [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit'
    }
    if ($taskAcl.GetOwner([Security.Principal.SecurityIdentifier]) -ne $taskSid) {
        throw 'The credential location must be owned by the current Windows user.'
    }
    $taskAcl.SetAccessRuleProtection($true, $false)
    foreach ($taskExistingRule in @($taskAcl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]))) {
        $taskAcl.RemoveAccessRuleSpecific($taskExistingRule)
    }
    $taskRule = New-Object Security.AccessControl.FileSystemAccessRule($taskSid, 'FullControl', $taskInheritance, 'None', 'Allow')
    $taskAcl.AddAccessRule($taskRule)
    # Set only the DACL; Set-Acl can request SeSecurityPrivilege for unrelated security sections.
    if ($PSVersionTable.PSVersion.Major -ge 6) { [IO.FileSystemAclExtensions]::SetAccessControl($taskItem, $taskAcl) }
    else { $taskItem.SetAccessControl($taskAcl) }
}

function Test-AutoSkillPrivateAcl([string]$Path) {
    $taskItem = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($taskItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Credential links are not supported.' }
    $taskAcl = Get-Acl -LiteralPath $Path -ErrorAction Stop
    $taskSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    if (-not $taskAcl.AreAccessRulesProtected -or $taskAcl.GetOwner([Security.Principal.SecurityIdentifier]) -ne $taskSid) {
        throw 'Credential permissions must be restricted to the current Windows user. Run -SetCredential again.'
    }
    $taskRules = @($taskAcl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]))
    if ($taskRules.Count -ne 1 -or $taskRules[0].IdentityReference -ne $taskSid -or
        $taskRules[0].AccessControlType -ne 'Allow' -or $taskRules[0].FileSystemRights -ne 'FullControl') {
        throw 'Credential permissions must be restricted to the current Windows user. Run -SetCredential again.'
    }
}

function Set-AutoSkillZhizengzengCredential([Security.SecureString]$Secret) {
    $taskOwnSecret = $null -eq $Secret
    $taskTemporaryFile = $null
    try {
        if ($taskOwnSecret) { $Secret = Read-Host 'Enter a NEW Zhizengzeng API Key (hidden; encrypted for this Windows user)' -AsSecureString }
        if ($Secret.Length -eq 0) { throw 'An empty credential cannot be saved.' }
        $taskPath = Get-AutoSkillCredentialPath
        $taskDirectory = Split-Path -Parent $taskPath
        New-Item -ItemType Directory -Path $taskDirectory -Force -ErrorAction Stop | Out-Null
        Set-AutoSkillPrivateAcl $taskDirectory
        if ((Test-Path -LiteralPath $taskPath) -and ((Get-Item -LiteralPath $taskPath -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Credential links are not supported.'
        }
        $taskEncrypted = ConvertFrom-SecureString -SecureString $Secret -ErrorAction Stop
        $taskTemporaryFile = Join-Path $taskDirectory ([Guid]::NewGuid().ToString('N') + '.tmp')
        [IO.File]::WriteAllText($taskTemporaryFile, $taskEncrypted, (New-Object Text.UTF8Encoding($false)))
        Set-AutoSkillPrivateAcl $taskTemporaryFile
        Move-Item -LiteralPath $taskTemporaryFile -Destination $taskPath -Force -ErrorAction Stop
        Test-AutoSkillPrivateAcl $taskPath
    } finally {
        $taskEncrypted = $null
        if ($taskTemporaryFile -and (Test-Path -LiteralPath $taskTemporaryFile)) { Remove-Item -LiteralPath $taskTemporaryFile -Force }
        if ($taskOwnSecret -and $null -ne $Secret) { $Secret.Dispose() }
    }
}

function Get-AutoSkillZhizengzengCredential {
    $taskPath = Get-AutoSkillCredentialPath
    if (-not (Test-Path -LiteralPath $taskPath)) {
        Set-AutoSkillZhizengzengCredential
    }
    Test-AutoSkillPrivateAcl (Split-Path -Parent $taskPath)
    Test-AutoSkillPrivateAcl $taskPath
    try {
        $taskEncrypted = [IO.File]::ReadAllText($taskPath)
        $taskSecret = ConvertTo-SecureString -String $taskEncrypted -ErrorAction Stop
        if ($taskSecret.Length -eq 0) { throw 'Empty credential.' }
        return $taskSecret
    } catch {
        throw 'The stored credential could not be decrypted for this Windows user. Run -SetCredential to replace it.'
    } finally { $taskEncrypted = $null }
}

function Invoke-WithAutoSkillCredential([scriptblock]$Action) {
    $taskPreviousKey = [Environment]::GetEnvironmentVariable('ZHIZENGZENG_API_KEY', 'Process')
    $taskSecret = $null
    $taskPointer = [IntPtr]::Zero
    try {
        if ([string]::IsNullOrWhiteSpace($taskPreviousKey)) {
            $taskSecret = Get-AutoSkillZhizengzengCredential
            $taskPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($taskSecret)
            [Environment]::SetEnvironmentVariable('ZHIZENGZENG_API_KEY', [Runtime.InteropServices.Marshal]::PtrToStringBSTR($taskPointer), 'Process')
        }
        & $Action
    } finally {
        [Environment]::SetEnvironmentVariable('ZHIZENGZENG_API_KEY', $taskPreviousKey, 'Process')
        $taskPreviousKey = $null
        if ($taskPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($taskPointer) }
        if ($null -ne $taskSecret) { $taskSecret.Dispose() }
    }
}
