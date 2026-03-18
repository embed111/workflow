Set-StrictMode -Version Latest

$script:WorkflowEnvPorts = @{
    dev  = 8091
    test = 8092
    prod = 8090
}

$script:WorkflowCopyExcludeDirs = @(
    '.git',
    '.running',
    '.runtime',
    '.test',
    '.tmp',
    '.codex',
    'state',
    'logs',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache'
)

function ConvertTo-WorkflowPlainData {
    param(
        [Parameter(ValueFromPipeline = $true)]
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) {
        return $null
    }
    if ($Value -is [string] -or $Value -is [int] -or $Value -is [long] -or $Value -is [double] -or $Value -is [bool]) {
        return $Value
    }
    if ($Value -is [datetime]) {
        return $Value.ToString('o')
    }
    if ($Value -is [System.Collections.IDictionary]) {
        $result = @{}
        foreach ($key in $Value.Keys) {
            $result[[string]$key] = ConvertTo-WorkflowPlainData $Value[$key]
        }
        return $result
    }
    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        $items = @()
        foreach ($item in $Value) {
            $items += ,(ConvertTo-WorkflowPlainData $item)
        }
        return $items
    }
    if ($Value.PSObject -and $Value.PSObject.Properties.Count -gt 0) {
        $result = @{}
        foreach ($prop in $Value.PSObject.Properties) {
            $result[[string]$prop.Name] = ConvertTo-WorkflowPlainData $prop.Value
        }
        return $result
    }
    return [string]$Value
}

function Read-WorkflowJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter()]
        [object]$Default = $null
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return ConvertTo-WorkflowPlainData $Default
    }
    try {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return ConvertTo-WorkflowPlainData $Default
        }
        return ConvertTo-WorkflowPlainData ($raw | ConvertFrom-Json)
    }
    catch {
        return ConvertTo-WorkflowPlainData $Default
    }
}

function Write-WorkflowJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [object]$Payload
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $json = ConvertTo-WorkflowPlainData $Payload | ConvertTo-Json -Depth 32
    Set-Content -LiteralPath $Path -Value ($json + [Environment]::NewLine) -Encoding UTF8
}

function Append-WorkflowJsonLine {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [object]$Payload
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $line = ConvertTo-WorkflowPlainData $Payload | ConvertTo-Json -Depth 32 -Compress
    Add-Content -LiteralPath $Path -Value $line -Encoding UTF8
}

function Get-WorkflowSourceRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ScriptRoot
    )

    return [System.IO.Path]::GetFullPath((Join-Path $ScriptRoot '..'))
}

function Get-WorkflowRunningRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    return (Join-Path $SourceRoot '.running')
}

function Get-WorkflowControlRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    return (Join-Path (Get-WorkflowRunningRoot -SourceRoot $SourceRoot) 'control')
}

function Get-WorkflowEnvironmentPort {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment
    )

    return [int]$script:WorkflowEnvPorts[$Environment]
}

function Get-WorkflowEnvironmentManifestPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment
    )

    return (Join-Path (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'envs') ($Environment + '.json'))
}

function Get-WorkflowEnvironmentRuntimeRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment
    )

    return (Join-Path (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'runtime') $Environment)
}

function Get-WorkflowEnvironmentPidFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment
    )

    return (Join-Path (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'pids') ($Environment + '.pid'))
}

function Get-WorkflowEnvironmentInstanceFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment
    )

    return (Join-Path (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'instances') ($Environment + '.json'))
}

function Get-WorkflowEnvironmentLogRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment
    )

    return (Join-Path (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'logs') $Environment)
}

function Get-WorkflowProdCandidatePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    return (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'prod-candidate.json')
}

function Get-WorkflowProdUpgradeRequestPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    return (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'prod-upgrade-request.json')
}

function Get-WorkflowProdLastActionPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    return (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'prod-last-action.json')
}

function Get-WorkflowDeploymentEventsPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    return (Join-Path (Get-WorkflowControlRoot -SourceRoot $SourceRoot) 'deployment-events.jsonl')
}

function Get-WorkflowRuntimeConfigPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RuntimeRoot
    )

    return (Join-Path (Join-Path $RuntimeRoot 'state') 'runtime-config.json')
}

function Get-WorkflowRuntimeConfig {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RuntimeRoot
    )

    return (Read-WorkflowJson -Path (Get-WorkflowRuntimeConfigPath -RuntimeRoot $RuntimeRoot) -Default @{})
}

function Write-WorkflowRuntimeConfig {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RuntimeRoot,
        [Parameter(Mandatory = $true)]
        [hashtable]$Patch
    )

    $existing = Get-WorkflowRuntimeConfig -RuntimeRoot $RuntimeRoot
    $next = @{}
    foreach ($pair in $existing.GetEnumerator()) {
        $next[$pair.Key] = $pair.Value
    }
    foreach ($pair in $Patch.GetEnumerator()) {
        $next[$pair.Key] = $pair.Value
    }
    Write-WorkflowJson -Path (Get-WorkflowRuntimeConfigPath -RuntimeRoot $RuntimeRoot) -Payload $next
    return $next
}

function Ensure-WorkflowControlDirs {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    $controlRoot = Get-WorkflowControlRoot -SourceRoot $SourceRoot
    @(
        $controlRoot,
        (Join-Path $controlRoot 'envs'),
        (Join-Path $controlRoot 'runtime'),
        (Join-Path $controlRoot 'logs'),
        (Join-Path $controlRoot 'pids'),
        (Join-Path $controlRoot 'instances'),
        (Join-Path $controlRoot 'candidates'),
        (Join-Path $controlRoot 'backups'),
        (Join-Path $controlRoot 'reports')
    ) | ForEach-Object {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

function Get-WorkflowDefaultArtifactRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    $sourceConfig = Read-WorkflowJson -Path (Join-Path $SourceRoot '.runtime\state\runtime-config.json') -Default @{}
    $configured = [string]($sourceConfig['artifact_root'])
    if (-not [string]::IsNullOrWhiteSpace($configured)) {
        return [System.IO.Path]::GetFullPath($configured)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Split-Path $SourceRoot -Parent) '.output'))
}

function Get-WorkflowDerivedArtifactRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseArtifactRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test')]
        [string]$Environment
    )

    $trimmed = $BaseArtifactRoot.TrimEnd('\', '/')
    $leaf = Split-Path $trimmed -Leaf
    $parent = Split-Path $trimmed -Parent
    if ([string]::IsNullOrWhiteSpace($leaf)) {
        return [System.IO.Path]::GetFullPath((Join-Path $trimmed ("workflow-output-" + $Environment)))
    }
    return [System.IO.Path]::GetFullPath((Join-Path $parent ($leaf + '-' + $Environment)))
}

function Resolve-WorkflowEnvironmentDescriptor {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment,
        [Parameter()]
        [string]$AgentSearchRoot = '',
        [Parameter()]
        [string]$ArtifactRoot = '',
        [Parameter()]
        [string]$BindHost = '',
        [Parameter()]
        [int]$Port = 0
    )

    Ensure-WorkflowControlDirs -SourceRoot $SourceRoot
    $runningRoot = Get-WorkflowRunningRoot -SourceRoot $SourceRoot
    $deployRoot = Join-Path $runningRoot $Environment
    $runtimeRoot = Get-WorkflowEnvironmentRuntimeRoot -SourceRoot $SourceRoot -Environment $Environment
    $manifestPath = Get-WorkflowEnvironmentManifestPath -SourceRoot $SourceRoot -Environment $Environment
    $manifest = Read-WorkflowJson -Path $manifestPath -Default @{}
    $runtimeConfig = Get-WorkflowRuntimeConfig -RuntimeRoot $runtimeRoot
    $sourceConfig = Read-WorkflowJson -Path (Join-Path $SourceRoot '.runtime\state\runtime-config.json') -Default @{}
    $prodRuntimeRoot = Get-WorkflowEnvironmentRuntimeRoot -SourceRoot $SourceRoot -Environment 'prod'
    $prodRuntimeConfig = Get-WorkflowRuntimeConfig -RuntimeRoot $prodRuntimeRoot
    $prodArtifactBase = if (-not [string]::IsNullOrWhiteSpace([string]$prodRuntimeConfig['artifact_root'])) {
        [string]$prodRuntimeConfig['artifact_root']
    }
    else {
        Get-WorkflowDefaultArtifactRoot -SourceRoot $SourceRoot
    }

    $resolvedAgentRoot = if (-not [string]::IsNullOrWhiteSpace($AgentSearchRoot)) {
        $AgentSearchRoot
    }
    elseif (-not [string]::IsNullOrWhiteSpace([string]$runtimeConfig['agent_search_root'])) {
        [string]$runtimeConfig['agent_search_root']
    }
    elseif (-not [string]::IsNullOrWhiteSpace([string]$sourceConfig['agent_search_root'])) {
        [string]$sourceConfig['agent_search_root']
    }
    else {
        [System.IO.Path]::GetFullPath((Split-Path $SourceRoot -Parent))
    }

    $resolvedArtifactRoot = if (-not [string]::IsNullOrWhiteSpace($ArtifactRoot)) {
        $ArtifactRoot
    }
    elseif (-not [string]::IsNullOrWhiteSpace([string]$runtimeConfig['artifact_root'])) {
        [string]$runtimeConfig['artifact_root']
    }
    elseif ($Environment -eq 'prod') {
        $prodArtifactBase
    }
    else {
        Get-WorkflowDerivedArtifactRoot -BaseArtifactRoot $prodArtifactBase -Environment $Environment
    }

    $resolvedHost = if (-not [string]::IsNullOrWhiteSpace($BindHost)) {
        $BindHost
    }
    elseif (-not [string]::IsNullOrWhiteSpace([string]$manifest['host'])) {
        [string]$manifest['host']
    }
    else {
        '127.0.0.1'
    }

    $resolvedPort = if ($Port -gt 0) {
        $Port
    }
    elseif ([int]($manifest['port']) -gt 0) {
        [int]$manifest['port']
    }
    else {
        Get-WorkflowEnvironmentPort -Environment $Environment
    }

    $versionText = [string]$manifest['current_version']
    if ([string]::IsNullOrWhiteSpace($versionText)) {
        $versionText = ''
    }

    return @{
        environment     = $Environment
        source_root     = [System.IO.Path]::GetFullPath($SourceRoot)
        running_root    = [System.IO.Path]::GetFullPath($runningRoot)
        control_root    = [System.IO.Path]::GetFullPath((Get-WorkflowControlRoot -SourceRoot $SourceRoot))
        deploy_root     = [System.IO.Path]::GetFullPath($deployRoot)
        runtime_root    = [System.IO.Path]::GetFullPath($runtimeRoot)
        host            = $resolvedHost
        port            = [int]$resolvedPort
        agent_search_root = [System.IO.Path]::GetFullPath($resolvedAgentRoot)
        artifact_root   = [System.IO.Path]::GetFullPath($resolvedArtifactRoot)
        manifest_path   = [System.IO.Path]::GetFullPath($manifestPath)
        pid_file        = [System.IO.Path]::GetFullPath((Get-WorkflowEnvironmentPidFile -SourceRoot $SourceRoot -Environment $Environment))
        instance_file   = [System.IO.Path]::GetFullPath((Get-WorkflowEnvironmentInstanceFile -SourceRoot $SourceRoot -Environment $Environment))
        log_root        = [System.IO.Path]::GetFullPath((Get-WorkflowEnvironmentLogRoot -SourceRoot $SourceRoot -Environment $Environment))
        version         = $versionText
    }
}

function Assert-WorkflowArtifactIsolation {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor
    )

    $environment = [string]$Descriptor.environment
    if ($environment -eq 'prod') {
        return
    }
    $sourceRoot = [string]$Descriptor.source_root
    $prodConfig = Get-WorkflowRuntimeConfig -RuntimeRoot (Get-WorkflowEnvironmentRuntimeRoot -SourceRoot $sourceRoot -Environment 'prod')
    $prodArtifactRoot = if (-not [string]::IsNullOrWhiteSpace([string]$prodConfig['artifact_root'])) {
        [System.IO.Path]::GetFullPath([string]$prodConfig['artifact_root'])
    }
    else {
        Get-WorkflowDefaultArtifactRoot -SourceRoot $sourceRoot
    }
    $currentArtifactRoot = [System.IO.Path]::GetFullPath([string]$Descriptor.artifact_root)
    if ($currentArtifactRoot.TrimEnd('\', '/') -ieq $prodArtifactRoot.TrimEnd('\', '/')) {
        throw "环境 $environment 的任务产物路径与 prod 冲突：$currentArtifactRoot。请改用独立路径后再部署或启动。"
    }
}

function Write-WorkflowEnvironmentManifest {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Descriptor,
        [Parameter()]
        [hashtable]$Extra = @{}
    )

    $existing = Read-WorkflowJson -Path ([string]$Descriptor.manifest_path) -Default @{}
    $payload = @{}
    foreach ($pair in $existing.GetEnumerator()) {
        $payload[$pair.Key] = $pair.Value
    }
    foreach ($pair in $Descriptor.GetEnumerator()) {
        $payload[$pair.Key] = $pair.Value
    }
    foreach ($pair in $Extra.GetEnumerator()) {
        $payload[$pair.Key] = $pair.Value
    }
    $payload['updated_at'] = (Get-Date).ToUniversalTime().ToString('o')
    Write-WorkflowJson -Path ([string]$Descriptor.manifest_path) -Payload $payload
    return $payload
}

function Write-WorkflowDeploymentEvent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [Parameter(Mandatory = $true)]
        [hashtable]$Payload
    )

    $row = @{}
    foreach ($pair in $Payload.GetEnumerator()) {
        $row[$pair.Key] = $pair.Value
    }
    if (-not $row.ContainsKey('timestamp')) {
        $row['timestamp'] = (Get-Date).ToUniversalTime().ToString('o')
    }
    Append-WorkflowJsonLine -Path (Get-WorkflowDeploymentEventsPath -SourceRoot $SourceRoot) -Payload $row
}
