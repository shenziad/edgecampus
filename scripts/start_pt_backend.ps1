param(
    [ValidateRange(1024, 65535)][int]$ControllerPort = 58000,
    [ValidateRange(1024, 65535)][int]$BackendPort = 8000,
    [string]$ControllerUsername
)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "runtime/noc-venv/Scripts/python.exe"
if (!(Test-Path -LiteralPath $pythonExe)) {
    throw "缺少 runtime/noc-venv 环境，请先按 docs/PT_CONTROLLER_SETUP.md 创建 Python 环境。"
}
if (!$ControllerUsername) { $ControllerUsername = Read-Host "PT 控制器管理员用户名" }
$controllerPassword = Read-Host "PT 控制器管理员密码" -AsSecureString
$controllerCredential = [pscredential]::new($ControllerUsername, $controllerPassword)
$previousControllerEnv = @{}
foreach ($name in @("PT_CONTROLLER_URL", "PT_CONTROLLER_USERNAME", "PT_CONTROLLER_PASSWORD")) {
    $previousControllerEnv[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}
Push-Location $repoRoot
try {
    $env:PT_CONTROLLER_URL = "http://127.0.0.1:$ControllerPort"
    $env:PT_CONTROLLER_USERNAME = $ControllerUsername
    $env:PT_CONTROLLER_PASSWORD = $controllerCredential.GetNetworkCredential().Password
    & $pythonExe -m uvicorn backend.app.main:app --host 127.0.0.1 --port $BackendPort
} finally {
    foreach ($name in $previousControllerEnv.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previousControllerEnv[$name], "Process")
    }
    Pop-Location
}
