param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'test', 'prod')]
    [string]$Environment,
    [string]$BindHost = '',
    [int]$Port = 0,
    [string]$AgentSearchRoot = '',
    [string]$ArtifactRoot = '',
    [switch]$SkipTestGate,
    [switch]$StartAfterDeploy,
    [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'workflow_env_common.ps1')

function New-VersionId {
    return (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
}

function Test-RunningProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PidFile
    )

    if (-not (Test-Path -LiteralPath $PidFile)) {
        return $null
    }
    $text = ''
    try {
        $text = (Get-Content -LiteralPath $PidFile -Raw -Encoding UTF8).Trim()
    }
    catch {
        return $null
    }
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }
    $pidValue = 0
    if (-not [int]::TryParse($text, [ref]$pidValue)) {
        return $null
    }
    try {
        return Get-Process -Id $pidValue -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function Copy-WorkflowTree {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourcePath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath,
        [Parameter()]
        [string[]]$ExcludeDirs = @()
    )

    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    $args = @(
        $SourcePath,
        $TargetPath,
        '/MIR',
        '/R:1',
        '/W:1',
        '/NFL',
        '/NDL',
        '/NJH',
        '/NJS',
        '/NP'
    )
    if ($ExcludeDirs.Count -gt 0) {
        $args += '/XD'
        $args += $ExcludeDirs
    }
    & robocopy @args | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed with exit code $LASTEXITCODE"
    }
}

function Write-DeploymentMetadata {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [Parameter(Mandatory = $true)]
        [string]$Version,
        [Parameter(Mandatory = $true)]
        [string]$DeployedAt
    )

    $metadataPath = Join-Path ([string]$Descriptor.deploy_root) '.workflow-deployment.json'
    Write-WorkflowJson -Path $metadataPath -Payload @{
        environment   = [string]$Descriptor.environment
        version       = $Version
        deployed_at   = $DeployedAt
        source_root   = [string]$Descriptor.source_root
        control_root  = [string]$Descriptor.control_root
        manifest_path = [string]$Descriptor.manifest_path
    }
    return $metadataPath
}

function Invoke-TestGate {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [Parameter(Mandatory = $true)]
        [string]$Version
    )

    $sourceRoot = [string]$Descriptor.source_root
    $gateScript = Join-Path $sourceRoot 'scripts\acceptance\run_acceptance_runtime_release_gate.py'
    if (-not (Test-Path -LiteralPath $gateScript)) {
        throw "test gate script missing: $gateScript"
    }
    $reportRoot = Join-Path ([string]$Descriptor.control_root) 'reports'
    New-Item -ItemType Directory -Path $reportRoot -Force | Out-Null
    $arguments = @(
        $gateScript,
        '--workspace-root',
        ([string]$Descriptor.deploy_root),
        '--runtime-root',
        ([string]$Descriptor.runtime_root),
        '--host',
        ([string]$Descriptor.host),
        '--port',
        ([string]$Descriptor.port),
        '--version',
        $Version,
        '--report-root',
        $reportRoot
    )
    $output = & python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "test gate failed with exit code $LASTEXITCODE"
    }
    $evidencePath = ''
    if ($output) {
        $evidencePath = [string]($output | Select-Object -Last 1)
    }
    if ([string]::IsNullOrWhiteSpace($evidencePath) -or -not (Test-Path -LiteralPath $evidencePath)) {
        throw "test gate did not return a valid evidence path: $evidencePath"
    }
    return [System.IO.Path]::GetFullPath($evidencePath)
}

function Publish-ProdCandidate {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [Parameter(Mandatory = $true)]
        [string]$Version,
        [Parameter(Mandatory = $true)]
        [string]$EvidencePath,
        [Parameter(Mandatory = $true)]
        [string]$PublishedAt
    )

    $candidateRoot = Join-Path (Join-Path ([string]$Descriptor.control_root) 'candidates') $Version
    $candidateAppRoot = Join-Path $candidateRoot 'app'
    $candidateMetaPath = Join-Path $candidateRoot 'candidate.json'
    if (Test-Path -LiteralPath $candidateRoot) {
        Remove-Item -LiteralPath $candidateRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $candidateRoot -Force | Out-Null
    Copy-WorkflowTree -SourcePath ([string]$Descriptor.deploy_root) -TargetPath $candidateAppRoot
    Write-WorkflowJson -Path $candidateMetaPath -Payload @{
        version            = $Version
        version_rank       = $Version
        source_environment = 'test'
        source_deploy_root = [string]$Descriptor.deploy_root
        candidate_app_root = $candidateAppRoot
        test_batch_id      = ('test-gate-' + $Version)
        passed_at          = $PublishedAt
        evidence_path      = $EvidencePath
        created_at         = $PublishedAt
    }
    $candidatePayload = @{
        version            = $Version
        version_rank       = $Version
        source_environment = 'test'
        test_batch_id      = ('test-gate-' + $Version)
        passed_at          = $PublishedAt
        evidence_path      = $EvidencePath
        candidate_app_root = $candidateAppRoot
        candidate_meta_path = $candidateMetaPath
    }
    Write-WorkflowJson -Path (Get-WorkflowProdCandidatePath -SourceRoot ([string]$Descriptor.source_root)) -Payload $candidatePayload
    return $candidatePayload
}

$sourceRoot = Get-WorkflowSourceRoot -ScriptRoot $PSScriptRoot
$descriptor = Resolve-WorkflowEnvironmentDescriptor `
    -SourceRoot $sourceRoot `
    -Environment $Environment `
    -AgentSearchRoot $AgentSearchRoot `
    -ArtifactRoot $ArtifactRoot `
    -BindHost $BindHost `
    -Port $Port
Assert-WorkflowArtifactIsolation -Descriptor $descriptor

$runningProcess = Test-RunningProcess -PidFile ([string]$descriptor.pid_file)
if ($runningProcess) {
    throw "环境 $Environment 当前正在运行（PID=$($runningProcess.Id)），请先停止后再部署。"
}

$version = New-VersionId
$deployedAt = (Get-Date).ToUniversalTime().ToString('o')
$descriptor.version = $version

Write-Host "[workflow-deploy] environment: $Environment"
Write-Host "[workflow-deploy] source root: $sourceRoot"
Write-Host "[workflow-deploy] deploy root: $($descriptor.deploy_root)"
Write-Host "[workflow-deploy] runtime root: $($descriptor.runtime_root)"
Write-Host "[workflow-deploy] agent root: $($descriptor.agent_search_root)"
Write-Host "[workflow-deploy] artifact root: $($descriptor.artifact_root)"
Write-Host "[workflow-deploy] version: $version"

Copy-WorkflowTree -SourcePath $sourceRoot -TargetPath ([string]$descriptor.deploy_root) -ExcludeDirs $script:WorkflowCopyExcludeDirs
$metadataPath = Write-DeploymentMetadata -Descriptor $descriptor -Version $version -DeployedAt $deployedAt

$runtimeConfigPatch = @{
    agent_search_root = [string]$descriptor.agent_search_root
    artifact_root     = [string]$descriptor.artifact_root
    task_artifact_root = [string]$descriptor.artifact_root
}
$sourceRuntimeConfig = Read-WorkflowJson -Path (Join-Path $sourceRoot '.runtime\state\runtime-config.json') -Default @{}
if ($sourceRuntimeConfig.ContainsKey('show_test_data')) {
    $runtimeConfigPatch['show_test_data'] = [bool]$sourceRuntimeConfig.show_test_data
}
$runtimeConfig = Write-WorkflowRuntimeConfig -RuntimeRoot ([string]$descriptor.runtime_root) -Patch $runtimeConfigPatch

if ($Environment -eq 'prod') {
    Remove-Item -LiteralPath (Get-WorkflowProdUpgradeRequestPath -SourceRoot $sourceRoot) -Force -ErrorAction SilentlyContinue
}

$manifest = Write-WorkflowEnvironmentManifest -Descriptor $descriptor -Extra @{
    current_version      = $version
    current_version_rank = $version
    deploy_status        = 'deployed'
    deployed_at          = $deployedAt
    deployment_metadata_path = $metadataPath
    runtime_config_path  = (Get-WorkflowRuntimeConfigPath -RuntimeRoot ([string]$descriptor.runtime_root))
}

$deployReportPath = Join-Path ([string]$descriptor.log_root) ('deploy-' + $version + '.json')
$deployReport = @{
    environment         = $Environment
    version             = $version
    action              = 'deploy'
    started_at          = $deployedAt
    finished_at         = (Get-Date).ToUniversalTime().ToString('o')
    source_root         = $sourceRoot
    deploy_root         = [string]$descriptor.deploy_root
    runtime_root        = [string]$descriptor.runtime_root
    host                = [string]$descriptor.host
    port                = [int]$descriptor.port
    agent_search_root   = [string]$descriptor.agent_search_root
    artifact_root       = [string]$descriptor.artifact_root
    runtime_config_path = [string](Get-WorkflowRuntimeConfigPath -RuntimeRoot ([string]$descriptor.runtime_root))
    deployment_metadata_path = $metadataPath
    result              = 'success'
}

if ($Environment -eq 'test' -and -not $SkipTestGate) {
    Write-Host "[workflow-deploy] test gate: start"
    $evidencePath = Invoke-TestGate -Descriptor $descriptor -Version $version
    $candidate = Publish-ProdCandidate -Descriptor $descriptor -Version $version -EvidencePath $evidencePath -PublishedAt ((Get-Date).ToUniversalTime().ToString('o'))
    $manifest = Write-WorkflowEnvironmentManifest -Descriptor $descriptor -Extra @{
        latest_test_gate_status   = 'passed'
        latest_test_gate_evidence = $evidencePath
        latest_candidate_version  = [string]$candidate.version
        latest_candidate_path     = [string]$candidate.candidate_app_root
        latest_candidate_created_at = [string]$candidate.passed_at
    }
    $deployReport['test_gate'] = @{
        status        = 'passed'
        evidence_path = $evidencePath
    }
    $deployReport['prod_candidate'] = $candidate
    Write-Host "[workflow-deploy] test gate: passed"
    Write-Host "[workflow-deploy] candidate: $($candidate.version)"
}
elseif ($Environment -eq 'test') {
    $deployReport['test_gate'] = @{
        status = 'skipped'
    }
}

Write-WorkflowJson -Path $deployReportPath -Payload $deployReport
Write-WorkflowDeploymentEvent -SourceRoot $sourceRoot -Payload @{
    environment   = $Environment
    version       = $version
    action        = 'deploy'
    result        = 'success'
    evidence_path = $deployReportPath
}

Write-Host "[workflow-deploy] manifest: $($descriptor.manifest_path)"
Write-Host "[workflow-deploy] report: $deployReportPath"

if ($StartAfterDeploy) {
    & (Join-Path $sourceRoot 'scripts\start_workflow_env.ps1') -Environment $Environment -OpenBrowser:$OpenBrowser
    exit $LASTEXITCODE
}
