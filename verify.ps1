$
$ErrorActionPreference = 'Continue'
$compose = 'docker compose -f C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/docker-compose.yml exec -T trino curl -s'
function Query-Table {
    param([string]$Table)
    $sql = 'SELECT COUNT(*) FROM iceberg.default.' + $Table
    Write-Host '=== Table: ',$Table,' ===' -ForegroundColor Cyan
    $body = '{\"statement\":\"' + $sql + '\"}'
    Write-Host 'BODY:',$body
    $res = Invoke-Expression '$compose -X POST \'http://localhost:8080/v1/statement\' -H \'Content-Type: application/json\' -H \'X-Trino-User: test\' -d $body'
    Write-Host 'INITIAL:',$res
    $nextUri = ($res | ConvertFrom-Json).nextUri
    for ($i = 1;$i -le 18;$i++) {
        Start-Sleep -Seconds 5
        $r = Invoke-Expression '$compose \'$nextUri\' -H \'X-Trino-User: test\''
        $obj = $r | ConvertFrom-Json
        Write-Host 'Poll ',$i,' - state: ',$obj.stats.state
        if ($obj.stats.state -eq 'FINISHED' -or $obj.stats.state -eq 'FAILED') {
            Write-Host 'RESULT: ',$r
            break
        }
    }
    Write-Host ''
}
Query-Table 'user_behavior_dwd'
Query-Table 'user_behavior_pvuv_1m'
Query-Table 'item_hot_1h'
Write-Host '=== Flink Job Status Summary ===' -ForegroundColor Cyan
docker compose -f C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/docker-compose.yml exec -T jobmanager flink list
