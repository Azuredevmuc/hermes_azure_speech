param(
    [string]$HermesHome = "$env:USERPROFILE\.hermes",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $HermesHome)) {
    throw "Hermes home does not exist: $HermesHome"
}

$envFile = Join-Path $HermesHome ".env"
$desiredEntries = [ordered]@{
    "AZURE_SPEECH_KEY" = ""
    "AZURE_SPEECH_REGION" = ""
    "AZURE_SPEECH_VOICE" = "de-DE-KatjaNeural"
    "AZURE_SPEECH_LANGUAGE" = "de-DE"
}

$existingEntries = [ordered]@{}
if (Test-Path -LiteralPath $envFile) {
    foreach ($line in Get-Content -LiteralPath $envFile -Encoding UTF8) {
        if ($line -match '^\s*#' -or $line -notmatch '=') {
            continue
        }

        $parts = $line.Split('=', 2)
        $key = $parts[0].Trim()
        $value = if ($parts.Count -gt 1) { $parts[1] } else { "" }
        if ($key) {
            $existingEntries[$key] = $value
        }
    }
}

$changed = $false
foreach ($key in $desiredEntries.Keys) {
    if ($Force -or -not $existingEntries.Contains($key)) {
        $existingEntries[$key] = $desiredEntries[$key]
        $changed = $true
    }
}

if (-not (Test-Path -LiteralPath $envFile)) {
    $changed = $true
}

if (-not $changed) {
    Write-Host "Hermes .env already contains the Azure Speech keys: $envFile"
    Write-Host "No values were changed."
    exit 0
}

$output = New-Object System.Collections.Generic.List[string]
$output.Add("# Hermes Azure Speech bootstrap")
$output.Add("# Fill in the blank values locally. Do not commit real credentials.")
foreach ($key in $existingEntries.Keys) {
    $output.Add("$key=$($existingEntries[$key])")
}

Set-Content -LiteralPath $envFile -Value $output -Encoding UTF8

Write-Host "Updated Hermes environment template: $envFile"
Write-Host "Next steps:"
Write-Host "  1. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in $envFile"
Write-Host "  2. Keep or adjust AZURE_SPEECH_VOICE and AZURE_SPEECH_LANGUAGE"
Write-Host "  3. Ensure config.yaml uses tts.provider: azure-speech and stt.provider: azure-speech"
