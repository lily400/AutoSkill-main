$ErrorActionPreference = 'Stop'
$task003Root = 'D:\AS\AutoSkill-main\degradation_failure_lab'
$task003Local = 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\task003-fix'
$task003Blocks = @()
$task003Errors = @()
foreach ($task003File in @('docs/sgb/task003-clean-runbook.md','docs/sgb/task003-clean-admission.md')) {
    $task003Text = [System.IO.File]::ReadAllText((Join-Path $task003Root $task003File))
    $task003Index = 0
    foreach ($task003Match in [regex]::Matches($task003Text, '(?ms)^```powershell\r?\n(.*?)^```')) {
        $task003Index++
        $task003Tokens = $null
        $task003ParseErrors = $null
        [void][System.Management.Automation.Language.Parser]::ParseInput($task003Match.Groups[1].Value, [ref]$task003Tokens, [ref]$task003ParseErrors)
        $task003Blocks += [pscustomobject]@{file=$task003File; block=$task003Index; errors=@($task003ParseErrors).Count}
        foreach ($task003Error in $task003ParseErrors) {
            $task003Errors += [pscustomobject]@{file=$task003File;block=$task003Index;message=$task003Error.Message;line=$task003Error.Extent.StartLineNumber}
        }
    }
}
$task003Value = @{kind='syntax_only_no_commands_executed';blocks=$task003Blocks;errors=$task003Errors;success=($task003Errors.Count -eq 0)}
$task003Value | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $task003Local 'powershell-syntax.json') -Encoding UTF8
Write-Output ('PowerShell blocks={0}, parse errors={1}' -f $task003Blocks.Count,$task003Errors.Count)
if ($task003Errors.Count) { exit 1 }
