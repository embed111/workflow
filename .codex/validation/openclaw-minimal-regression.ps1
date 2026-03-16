$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$serverStdout = Join-Path $env:TEST_LOG_DIR "workflow-server.stdout.log"
$serverStderr = Join-Path $env:TEST_LOG_DIR "workflow-server.stderr.log"
$port = 18091

$proc = Start-Process python `
    -ArgumentList "scripts/workflow_web_server.py", "--host", "127.0.0.1", "--port", "$port" `
    -WorkingDirectory $repoRoot `
    -PassThru `
    -RedirectStandardOutput $serverStdout `
    -RedirectStandardError $serverStderr

try {
    $ready = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$port/healthz"
            if ($resp.StatusCode -eq 200) {
                $ready = $true
                break
            }
        }
        catch {
        }
    }

    if (-not $ready) {
        throw "healthz timeout on port $port"
    }

    Push-Location $repoRoot
    try {
        python scripts/workflow_entry_cli.py --mode status
        if ($LASTEXITCODE -ne 0) {
            throw "workflow_entry_cli.py --mode status failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
    }
}
