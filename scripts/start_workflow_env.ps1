param(
    [ValidateSet('dev', 'test', 'prod')]
    [string]$Environment = 'prod',
    [string]$BindHost = '',
    [int]$Port = 0,
    [switch]$SkipBackfill,
    [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'workflow_env_common.ps1')

$script:ProdUpgradeExitCode = 73

function ConvertTo-WorkflowProcessArgument {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    if ($Value.Length -eq 0) {
        return '""'
    }
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    $escaped = $Value -replace '(\\*)"', '$1$1\"'
    $escaped = $escaped -replace '(\\+)$', '$1$1'
    return '"' + $escaped + '"'
}

function Ensure-EnvironmentDeployment {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment,
        [Parameter(Mandatory = $true)]
        [string]$BindHost,
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $deployRoot = Join-Path (Get-WorkflowRunningRoot -SourceRoot $SourceRoot) $Environment
    $launchScript = Join-Path $deployRoot 'scripts\launch_workflow.ps1'
    if (Test-Path -LiteralPath $launchScript) {
        return
    }
    Write-Host "[workflow-start] deploy $Environment because running copy is missing ..."
    & (Join-Path $SourceRoot 'scripts\deploy_workflow_env.ps1') `
        -Environment $Environment `
        -BindHost $BindHost `
        -Port $Port
    if ($LASTEXITCODE -ne 0) {
        throw "deploy $Environment failed with exit code $LASTEXITCODE"
    }
}

function Wait-WorkflowHealth {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BindHost,
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$LauncherProcess,
        [int]$TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds([Math]::Max(5, $TimeoutSeconds))
    $url = "http://$BindHost`:$Port/healthz"
    while ((Get-Date) -lt $deadline) {
        if ($LauncherProcess.HasExited) {
            return @{
                ok        = $false
                reason    = 'launcher_exited'
                exit_code = $LauncherProcess.ExitCode
            }
        }
        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 3
            if ($response.ok) {
                return @{
                    ok  = $true
                    url = $url
                }
            }
        }
        catch {
        }
        Start-Sleep -Seconds 1
    }
    return @{
        ok        = $false
        reason    = 'health_timeout'
        exit_code = if ($LauncherProcess.HasExited) { $LauncherProcess.ExitCode } else { -1 }
    }
}

function Set-ProcessEnvironment {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor
    )

    $variables = @{
        WORKFLOW_RUNTIME_ENV            = [string]$Descriptor.environment
        WORKFLOW_RUNTIME_SOURCE_ROOT    = [string]$Descriptor.source_root
        WORKFLOW_RUNTIME_CONTROL_ROOT   = [string]$Descriptor.control_root
        WORKFLOW_RUNTIME_MANIFEST_PATH  = [string]$Descriptor.manifest_path
        WORKFLOW_RUNTIME_DEPLOY_ROOT    = [string]$Descriptor.deploy_root
        WORKFLOW_RUNTIME_VERSION        = [string]$Descriptor.version
        WORKFLOW_RUNTIME_PID_FILE       = [string]$Descriptor.pid_file
        WORKFLOW_RUNTIME_INSTANCE_FILE  = [string]$Descriptor.instance_file
    }

    $backup = @{}
    foreach ($pair in $variables.GetEnumerator()) {
        $backup[$pair.Key] = [Environment]::GetEnvironmentVariable($pair.Key, 'Process')
        [Environment]::SetEnvironmentVariable($pair.Key, [string]$pair.Value, 'Process')
    }
    return $backup
}

function Restore-ProcessEnvironment {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Backup
    )

    foreach ($pair in $Backup.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable([string]$pair.Key, $pair.Value, 'Process')
    }
}

function Start-EnvironmentLauncher {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [switch]$SkipBackfill,
        [switch]$OpenBrowser
    )

    $launchScript = Join-Path ([string]$Descriptor.deploy_root) 'scripts\launch_workflow.ps1'
    if (-not (Test-Path -LiteralPath $launchScript)) {
        throw "launch script missing: $launchScript"
    }
    $manifest = Read-WorkflowJson -Path ([string]$Descriptor.manifest_path) -Default @{}
    if ([string]::IsNullOrWhiteSpace([string]$Descriptor.version)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$manifest['current_version'])) {
            $Descriptor.version = [string]$manifest['current_version']
        }
        elseif (-not [string]::IsNullOrWhiteSpace([string]$manifest['version'])) {
            $Descriptor.version = [string]$manifest['version']
        }
    }
    Write-WorkflowRuntimeConfig -RuntimeRoot ([string]$Descriptor.runtime_root) -Patch @{
        agent_search_root = [string]$Descriptor.agent_search_root
        artifact_root = [string]$Descriptor.artifact_root
        task_artifact_root = [string]$Descriptor.artifact_root
    } | Out-Null
    $backup = Set-ProcessEnvironment -Descriptor $Descriptor
    try {
        $args = @(
            '-NoProfile',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            $launchScript,
            '-BindHost',
            [string]$Descriptor.host,
            '-Port',
            [string]$Descriptor.port,
            '-RuntimeRoot',
            [string]$Descriptor.runtime_root
        )
        foreach ($pair in @(
            @('-RuntimeEnvironment', [string]$Descriptor.environment),
            @('-RuntimeControlRoot', [string]$Descriptor.control_root),
            @('-RuntimeManifestPath', [string]$Descriptor.manifest_path),
            @('-RuntimeVersion', [string]$Descriptor.version),
            @('-RuntimePidFile', [string]$Descriptor.pid_file),
            @('-RuntimeInstanceFile', [string]$Descriptor.instance_file),
            @('-RuntimeDeployRoot', [string]$Descriptor.deploy_root)
        )) {
            $name = [string]$pair[0]
            $value = [string]$pair[1]
            if ([string]::IsNullOrWhiteSpace($value)) {
                continue
            }
            $args += $name
            $args += $value
        }
        if ($SkipBackfill) {
            $args += '-SkipBackfill'
        }
        if ($OpenBrowser) {
            $args += '-OpenBrowser'
        }
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = (Get-Command 'powershell' -ErrorAction Stop).Source
        $startInfo.Arguments = (($args | ForEach-Object {
                    ConvertTo-WorkflowProcessArgument -Value ([string]$_)
                }) -join ' ')
        $startInfo.WorkingDirectory = [string]$Descriptor.deploy_root
        $startInfo.UseShellExecute = $false

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $startInfo
        $null = $process.Start()
        return $process
    }
    finally {
        Restore-ProcessEnvironment -Backup $backup
    }
}

function Stop-WorkflowServerFromDescriptor {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [Parameter()]
        [System.Diagnostics.Process]$LauncherProcess = $null
    )

    $serverProcess = $null
    if (Test-Path -LiteralPath ([string]$Descriptor.pid_file)) {
        $text = ''
        try {
            $text = (Get-Content -LiteralPath ([string]$Descriptor.pid_file) -Raw -Encoding UTF8).Trim()
        }
        catch {
            $text = ''
        }
        $pidValue = 0
        if ([int]::TryParse($text, [ref]$pidValue)) {
            try {
                $serverProcess = Get-Process -Id $pidValue -ErrorAction Stop
                Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
            }
            catch {
            }
        }
    }
    if ($LauncherProcess -and -not $LauncherProcess.HasExited) {
        try {
            Stop-Process -Id $LauncherProcess.Id -Force -ErrorAction SilentlyContinue
        }
        catch {
        }
    }
}

function Update-ProdLastAction {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [hashtable]$Payload
    )

    Write-WorkflowJson -Path (Get-WorkflowProdLastActionPath -SourceRoot $SourceRoot) -Payload $Payload
}

function Prepare-ProdUpgrade {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor
    )

    $sourceRoot = [string]$Descriptor.source_root
    $request = Read-WorkflowJson -Path (Get-WorkflowProdUpgradeRequestPath -SourceRoot $sourceRoot) -Default @{}
    $candidate = Read-WorkflowJson -Path (Get-WorkflowProdCandidatePath -SourceRoot $sourceRoot) -Default @{}
    if ([string]::IsNullOrWhiteSpace([string]$request['candidate_version'])) {
        throw 'prod upgrade request missing candidate_version'
    }
    if ([string]::IsNullOrWhiteSpace([string]$candidate['version'])) {
        throw 'prod upgrade candidate missing'
    }
    if ([string]$request['candidate_version'] -ne [string]$candidate['version']) {
        throw "prod upgrade request/candidate mismatch: request=$($request['candidate_version']) candidate=$($candidate['version'])"
    }
    $candidateAppRoot = [string]$candidate['candidate_app_root']
    if (-not (Test-Path -LiteralPath $candidateAppRoot)) {
        throw "candidate app root missing: $candidateAppRoot"
    }

    $currentManifest = Read-WorkflowJson -Path ([string]$Descriptor.manifest_path) -Default @{}
    $currentVersion = [string]$currentManifest['current_version']
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $backupRoot = Join-Path (Join-Path ([string]$Descriptor.control_root) 'backups') ('prod-' + $stamp)
    $backupAppRoot = Join-Path $backupRoot 'app'
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    Copy-WorkflowTree -SourcePath ([string]$Descriptor.deploy_root) -TargetPath $backupAppRoot

    Copy-WorkflowTree -SourcePath $candidateAppRoot -TargetPath ([string]$Descriptor.deploy_root)
    $descriptor.version = [string]$candidate['version']
    $appliedAt = (Get-Date).ToUniversalTime().ToString('o')
    Write-WorkflowJson -Path (Join-Path ([string]$Descriptor.deploy_root) '.workflow-deployment.json') -Payload @{
        environment   = 'prod'
        version       = [string]$candidate['version']
        deployed_at   = $appliedAt
        source_root   = [string]$Descriptor.source_root
        control_root  = [string]$Descriptor.control_root
        manifest_path = [string]$Descriptor.manifest_path
    }
    Write-WorkflowEnvironmentManifest -Descriptor $Descriptor -Extra @{
        current_version      = [string]$candidate['version']
        current_version_rank = [string]$candidate['version_rank']
        deploy_status        = 'upgrade_pending_health'
        upgrade_requested_at = [string]$request['requested_at']
        upgrade_candidate_version = [string]$candidate['version']
        upgrade_candidate_evidence_path = [string]$candidate['evidence_path']
        backup_app_root      = $backupAppRoot
    } | Out-Null
    Update-ProdLastAction -SourceRoot $sourceRoot -Payload @{
        action            = 'upgrade'
        status            = 'switching'
        requested_at      = [string]$request['requested_at']
        started_at        = $appliedAt
        current_version   = $currentVersion
        candidate_version = [string]$candidate['version']
        evidence_path     = [string]$candidate['evidence_path']
        backup_app_root   = $backupAppRoot
    }
    Write-WorkflowDeploymentEvent -SourceRoot $sourceRoot -Payload @{
        environment   = 'prod'
        version       = [string]$candidate['version']
        action        = 'upgrade_switching'
        result        = 'pending'
        evidence_path = [string]$candidate['evidence_path']
    }

    return @{
        requested_at      = [string]$request['requested_at']
        previous_version  = $currentVersion
        candidate_version = [string]$candidate['version']
        evidence_path     = [string]$candidate['evidence_path']
        backup_app_root   = $backupAppRoot
    }
}

function Restore-ProdBackup {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [Parameter(Mandatory = $true)]
        [hashtable]$UpgradeContext
    )

    $backupAppRoot = [string]$UpgradeContext.backup_app_root
    if (-not (Test-Path -LiteralPath $backupAppRoot)) {
        throw "prod backup missing: $backupAppRoot"
    }
    Copy-WorkflowTree -SourcePath $backupAppRoot -TargetPath ([string]$Descriptor.deploy_root)
    $descriptor.version = [string]$UpgradeContext.previous_version
    Write-WorkflowEnvironmentManifest -Descriptor $Descriptor -Extra @{
        current_version      = [string]$UpgradeContext.previous_version
        current_version_rank = [string]$UpgradeContext.previous_version
        deploy_status        = 'deployed'
        deployed_at          = (Get-Date).ToUniversalTime().ToString('o')
        upgrade_requested_at = ''
        upgrade_candidate_version = ''
        upgrade_candidate_evidence_path = ''
        backup_app_root      = $backupAppRoot
    } | Out-Null
}

$sourceRoot = Get-WorkflowSourceRoot -ScriptRoot $PSScriptRoot
$effectiveHost = if ([string]::IsNullOrWhiteSpace($BindHost)) { '127.0.0.1' } else { $BindHost }
$effectivePort = if ($Port -gt 0) { $Port } else { Get-WorkflowEnvironmentPort -Environment $Environment }

Ensure-EnvironmentDeployment -SourceRoot $sourceRoot -Environment $Environment -BindHost $effectiveHost -Port $effectivePort

$descriptor = Resolve-WorkflowEnvironmentDescriptor `
    -SourceRoot $sourceRoot `
    -Environment $Environment `
    -BindHost $effectiveHost `
    -Port $effectivePort
Assert-WorkflowArtifactIsolation -Descriptor $descriptor

$pendingUpgrade = $null
$openedBrowser = $false

while ($true) {
    $openNow = $OpenBrowser -and (-not $openedBrowser)
    $launcher = Start-EnvironmentLauncher -Descriptor $descriptor -SkipBackfill:$SkipBackfill -OpenBrowser:$openNow
    $openedBrowser = $true
    $healthTimeoutSeconds = if ($pendingUpgrade -and $Environment -eq 'prod') { 60 } else { 30 }
    $health = Wait-WorkflowHealth -BindHost ([string]$descriptor.host) -Port ([int]$descriptor.port) -LauncherProcess $launcher -TimeoutSeconds $healthTimeoutSeconds

    if (-not $health.ok) {
        Stop-WorkflowServerFromDescriptor -Descriptor $descriptor -LauncherProcess $launcher
        if ($pendingUpgrade -and $Environment -eq 'prod') {
            Write-Host "[workflow-start] upgrade health check failed, rollback to $($pendingUpgrade.previous_version) ..."
            Restore-ProdBackup -Descriptor $descriptor -UpgradeContext $pendingUpgrade
            Update-ProdLastAction -SourceRoot $sourceRoot -Payload @{
                action            = 'upgrade'
                status            = 'rollback_success'
                finished_at       = (Get-Date).ToUniversalTime().ToString('o')
                previous_version  = [string]$pendingUpgrade.previous_version
                candidate_version = [string]$pendingUpgrade.candidate_version
                evidence_path     = [string]$pendingUpgrade.evidence_path
                reason            = [string]$health.reason
            }
            Write-WorkflowDeploymentEvent -SourceRoot $sourceRoot -Payload @{
                environment   = 'prod'
                version       = [string]$pendingUpgrade.previous_version
                action        = 'upgrade_rollback'
                result        = 'success'
                evidence_path = [string]$pendingUpgrade.evidence_path
            }
            Remove-Item -LiteralPath (Get-WorkflowProdUpgradeRequestPath -SourceRoot $sourceRoot) -Force -ErrorAction SilentlyContinue
            $pendingUpgrade = $null
            continue
        }
        throw "环境 $Environment 启动失败：$($health.reason) exit_code=$($health.exit_code)"
    }

    Write-Host "[workflow-start] environment: $Environment"
    Write-Host "[workflow-start] url: http://$($descriptor.host):$($descriptor.port)"
    Write-Host "[workflow-start] version: $($descriptor.version)"

    if ($pendingUpgrade -and $Environment -eq 'prod') {
        $finishedAt = (Get-Date).ToUniversalTime().ToString('o')
        Write-WorkflowEnvironmentManifest -Descriptor $descriptor -Extra @{
            current_version      = [string]$pendingUpgrade.candidate_version
            current_version_rank = [string]$pendingUpgrade.candidate_version
            deploy_status        = 'deployed'
            deployed_at          = $finishedAt
            upgrade_requested_at = ''
            upgrade_candidate_version = ''
            upgrade_candidate_evidence_path = ''
            backup_app_root      = [string]$pendingUpgrade.backup_app_root
        } | Out-Null
        Update-ProdLastAction -SourceRoot $sourceRoot -Payload @{
            action            = 'upgrade'
            status            = 'success'
            finished_at       = $finishedAt
            previous_version  = [string]$pendingUpgrade.previous_version
            current_version   = [string]$pendingUpgrade.candidate_version
            candidate_version = [string]$pendingUpgrade.candidate_version
            evidence_path     = [string]$pendingUpgrade.evidence_path
        }
        Write-WorkflowDeploymentEvent -SourceRoot $sourceRoot -Payload @{
            environment   = 'prod'
            version       = [string]$pendingUpgrade.candidate_version
            action        = 'upgrade'
            result        = 'success'
            evidence_path = [string]$pendingUpgrade.evidence_path
        }
        Remove-Item -LiteralPath (Get-WorkflowProdUpgradeRequestPath -SourceRoot $sourceRoot) -Force -ErrorAction SilentlyContinue
        $pendingUpgrade = $null
    }

    $launcher.WaitForExit()
    $exitCode = $launcher.ExitCode

    if ($Environment -eq 'prod' -and $exitCode -eq $script:ProdUpgradeExitCode) {
        Write-Host '[workflow-start] prod upgrade requested, switching candidate ...'
        try {
            $pendingUpgrade = Prepare-ProdUpgrade -Descriptor $descriptor
        }
        catch {
            $candidate = Read-WorkflowJson -Path (Get-WorkflowProdCandidatePath -SourceRoot $sourceRoot) -Default @{}
            $request = Read-WorkflowJson -Path (Get-WorkflowProdUpgradeRequestPath -SourceRoot $sourceRoot) -Default @{}
            $finishedAt = (Get-Date).ToUniversalTime().ToString('o')
            $reason = $_.Exception.Message
            Update-ProdLastAction -SourceRoot $sourceRoot -Payload @{
                action            = 'upgrade'
                status            = 'failed'
                finished_at       = $finishedAt
                current_version   = [string]$descriptor.version
                candidate_version = [string]$request['candidate_version']
                evidence_path     = [string]$candidate['evidence_path']
                reason            = $reason
            }
            Write-WorkflowDeploymentEvent -SourceRoot $sourceRoot -Payload @{
                environment   = 'prod'
                version       = [string]$request['candidate_version']
                action        = 'upgrade'
                result        = 'failed'
                evidence_path = [string]$candidate['evidence_path']
                reason        = $reason
            }
            Remove-Item -LiteralPath (Get-WorkflowProdUpgradeRequestPath -SourceRoot $sourceRoot) -Force -ErrorAction SilentlyContinue
            throw
        }
        continue
    }

    exit $exitCode
}
