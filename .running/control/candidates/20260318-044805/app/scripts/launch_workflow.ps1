param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8090,
    [string]$RuntimeRoot = ".runtime",
    [switch]$SkipBackfill,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot 'workflow_env_common.ps1')

$workspaceRoot = Get-WorkflowSourceRoot -ScriptRoot $PSScriptRoot
$workspaceDir = Get-Item -LiteralPath $workspaceRoot
$isDeployedCopy = $workspaceDir.Parent -and $workspaceDir.Parent.Name -eq '.running'

if (-not $isDeployedCopy) {
    & (Join-Path $workspaceRoot 'scripts\start_workflow_env.ps1') `
        -Environment prod `
        -BindHost $BindHost `
        -Port $Port `
        -SkipBackfill:$SkipBackfill `
        -OpenBrowser:$OpenBrowser
    exit $LASTEXITCODE
}

$deploymentMetaPath = Join-Path $workspaceRoot '.workflow-deployment.json'
$deploymentMeta = Read-WorkflowJson -Path $deploymentMetaPath -Default @{}
$environment = [string]$deploymentMeta['environment']
if ([string]::IsNullOrWhiteSpace($environment)) {
    $environment = [string]$workspaceDir.Name
}
$controlRoot = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot '..\control'))
$manifestPath = Join-Path (Join-Path $controlRoot 'envs') ($environment + '.json')
$manifest = Read-WorkflowJson -Path $manifestPath -Default @{}

$effectiveHost = if ([string]::IsNullOrWhiteSpace($BindHost) -and -not [string]::IsNullOrWhiteSpace([string]$manifest['host'])) {
    [string]$manifest['host']
} else {
    $BindHost
}
if ([string]::IsNullOrWhiteSpace($effectiveHost)) {
    $effectiveHost = '127.0.0.1'
}

$effectivePort = if ($Port -eq 8090 -and [int]($manifest['port']) -gt 0) {
    [int]$manifest['port']
} else {
    $Port
}

$effectiveRuntimeRoot = $RuntimeRoot
if ($RuntimeRoot -eq '.runtime' -and -not [string]::IsNullOrWhiteSpace([string]$manifest['runtime_root'])) {
    $effectiveRuntimeRoot = [string]$manifest['runtime_root']
}

[Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_ENV', $environment, 'Process')
[Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_CONTROL_ROOT', $controlRoot, 'Process')
[Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_MANIFEST_PATH', $manifestPath, 'Process')
[Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_DEPLOY_ROOT', $workspaceRoot, 'Process')
if (-not [string]::IsNullOrWhiteSpace([string]$deploymentMeta['version'])) {
    [Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_VERSION', [string]$deploymentMeta['version'], 'Process')
}
if (-not [string]::IsNullOrWhiteSpace([string]$manifest['pid_file'])) {
    [Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_PID_FILE', [string]$manifest['pid_file'], 'Process')
}
if (-not [string]::IsNullOrWhiteSpace([string]$manifest['instance_file'])) {
    [Environment]::SetEnvironmentVariable('WORKFLOW_RUNTIME_INSTANCE_FILE', [string]$manifest['instance_file'], 'Process')
}

& (Join-Path $PSScriptRoot "dev/launch_workflow.ps1") `
    -BindHost $effectiveHost `
    -Port $effectivePort `
    -RuntimeRoot $effectiveRuntimeRoot `
    -SkipBackfill:$SkipBackfill `
    -OpenBrowser:$OpenBrowser
exit $LASTEXITCODE
