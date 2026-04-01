param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$StrategyKey = "bollinger_reversal",
    [string]$Symbol = "AAPL",
    [string]$Timeframe = "1h",
    [string]$StartAt = "2026-03-20T00:00:00",
    [string]$EndAt = "2026-03-27T23:59:59",
    [int]$TimeoutBars = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 90)
    Write-Host $Title
    Write-Host ("=" * 90)
}

function Invoke-ApiJson {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [object]$Body = $null
    )

    if ($null -ne $Body) {
        return Invoke-RestMethod -Uri $Uri -Method $Method -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 20)
    }

    return Invoke-RestMethod -Uri $Uri -Method $Method
}

try {
    Write-Section "[1] HEALTHCHECK"
    $health = Invoke-ApiJson -Method GET -Uri "$BaseUrl/api/v1/health"
    $health | Format-List

    if ($health.status -ne "ok") {
        throw "Healthcheck returned unexpected status: $($health.status)"
    }

    Write-Section "[2] LISTAR ESTRATEGIAS"
    $strategies = Invoke-ApiJson -Method GET -Uri "$BaseUrl/api/v1/strategies"
    $strategies | Format-Table -AutoSize

    $strategyExists = $strategies | Where-Object { $_.key -eq $StrategyKey }
    if (-not $strategyExists) {
        throw "Strategy '$StrategyKey' nao encontrada no endpoint /api/v1/strategies"
    }

    Write-Section "[3] EXECUTAR RUN HISTORICAL"
    $body = @{
        strategy_key = $StrategyKey
        symbol = $Symbol
        timeframe = $Timeframe
        start_at = $StartAt
        end_at = $EndAt
        timeout_bars = $TimeoutBars
        parameters = @{}
    }

    $runResponse = Invoke-ApiJson -Method POST -Uri "$BaseUrl/api/v1/runs/historical" -Body $body
    $runResponse | ConvertTo-Json -Depth 20

    $runId = $runResponse.run.id
    if ([string]::IsNullOrWhiteSpace($runId)) {
        throw "A resposta do endpoint /api/v1/runs/historical nao retornou run.id"
    }

    Write-Section "[4] VALIDAR RUN NO HISTORICO"
    $historyUri = "$BaseUrl/api/v1/run-history?symbol=$([uri]::EscapeDataString($Symbol))&timeframe=$([uri]::EscapeDataString($Timeframe))&strategy_key=$([uri]::EscapeDataString($StrategyKey))&limit=20"
    $history = Invoke-ApiJson -Method GET -Uri $historyUri
    $history | Format-Table -AutoSize

    $matchedRun = $history | Where-Object { $_.id -eq $runId }
    if (-not $matchedRun) {
        throw "Run '$runId' nao foi encontrado no endpoint /api/v1/run-history"
    }

    Write-Section "RESULTADO FINAL"
    Write-Host "Teste da API concluido com sucesso."
    Write-Host "Run validado no historico: $runId"
    exit 0
}
catch {
    Write-Section "ERRO"
    Write-Error $_
    exit 1
}