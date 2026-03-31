$statusFile = "status.json"
$logFile = "update.log"

function Write-Status($state, $message="") {
    $json = @{
        status = $state
        message = $message
        time = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    } | ConvertTo-Json -Depth 2

    Set-Content $statusFile $json
}

Write-Status "running" "OSM更新開始"

Write-Host "OSM 更新中..."
docker compose run --rm osm_updater 2>&1 | Tee-Object -FilePath $logFile

if ($LASTEXITCODE -ne 0) {
    Write-Status "error" "OSM 更新失敗"
    exit 1
}

Write-Status "processing" "ビジネステーブルの更新中"

Write-Host "📊 Refreshing table..."
Get-Content sql/incremental_update.sql |
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm 2>&1 |
Tee-Object -FilePath $logFile -Append

if ($LASTEXITCODE -ne 0) {
    Write-Status "error" "ビジネステーブルの更新失敗"
    exit 1
}

Write-Status "done" "更新完了"

Write-Host "✅完了"