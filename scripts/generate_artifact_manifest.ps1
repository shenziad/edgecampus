param(
    [string]$OutputPath = "docs/final/ARTIFACT_MANIFEST.json"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$previousLocation = Get-Location

try {
    Set-Location $repoRoot
    $paths = @(
        git ls-files --cached --others --exclude-standard |
            Where-Object { $_ -match '\.(png|jpe?g|pkt|docx)$' } |
            Sort-Object -Unique
    )

    $artifacts = foreach ($relativePath in $paths) {
        $absolutePath = Join-Path $repoRoot ($relativePath -replace '/', [IO.Path]::DirectorySeparatorChar)
        if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
            continue
        }

        $item = Get-Item -LiteralPath $absolutePath
        $hash = (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash.ToLowerInvariant()
        [ordered]@{
            path = $relativePath
            bytes = $item.Length
            sha256 = $hash
        }
    }

    $manifest = [ordered]@{
        archive_date = "2026-09-19"
        project_status = "ACCEPTANCE_COMPLETE_REPORT_PREPARATION"
        branch = "feat/edge"
        note = "Deterministic SHA-256 manifest for repository evidence images, Packet Tracer packages, and archived source documents. It includes the imported A/B/D final evidence and the 2026-09-19 course patch figures 47-54. Historical gate reports remain unchanged; current configuration is documented in docs/COURSE_COVERAGE_PATCH.md."
        artifacts = @($artifacts)
    }

    $json = $manifest | ConvertTo-Json -Depth 5
    [IO.File]::WriteAllText((Join-Path $repoRoot $OutputPath), $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    Write-Output ("Wrote {0} artifacts to {1}" -f $artifacts.Count, $OutputPath)
}
finally {
    Set-Location $previousLocation
}
