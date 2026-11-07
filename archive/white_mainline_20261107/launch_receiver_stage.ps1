param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('pilot_frames','user_count','activity_probability','cross_channel')]
    [string]$Stage
)
$ErrorActionPreference='Stop'
$taskRoot='D:\afdm-gfra'
$taskResult=Join-Path $taskRoot "result\$Stage\data\white_mainline_500_20261107"
$stageOrder=@('channel_denoising','pilot_frames','user_count','activity_probability','cross_channel')
$previousStage=$stageOrder[[Array]::IndexOf($stageOrder,$Stage)-1]
$previousResult=Join-Path $taskRoot "result\$previousStage\data\white_mainline_500_20261107"
$previousAdoption=Get-Content -LiteralPath (Join-Path $previousResult 'ADOPTION.json') -Raw | ConvertFrom-Json
if ($previousAdoption.status -ne 'PASS') { throw 'Previous figure adoption is incomplete' }
if (-not (Test-Path -LiteralPath (Join-Path $taskResult 'PLAN_HASH.json'))) { throw 'Prepare and verify the stage first' }
foreach ($name in @('RUNNING.lock','START.json','LAUNCH.json','FAILURE.json','STOP.json','COMPLETION.json')) {
    if (Test-Path -LiteralPath (Join-Path $taskResult $name)) { throw "Existing $name requires inspection; preserving it" }
}
$env:PYTHONPATH=Join-Path $taskRoot 'src'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
$env:NUMEXPR_NUM_THREADS='2'
$taskArgs=@('-X','utf8','-B','-m','evaluation.white_followup_20261107.receivers','coordinate','--stage',$Stage)
$taskProcess=Start-Process -FilePath (Join-Path $taskRoot '.venv\Scripts\python.exe') -ArgumentList $taskArgs -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskResult 'stdout.log') -RedirectStandardError (Join-Path $taskResult 'stderr.log') -PassThru
$receipt=[ordered]@{
    launcher_pid=$taskProcess.Id
    creation_time_utc=$taskProcess.StartTime.ToUniversalTime().ToString('o')
    executable=(Join-Path $taskRoot '.venv\Scripts\python.exe')
    arguments=$taskArgs
    hidden=$true
    stage=$Stage
    native_directory="E:\afdm-gfra-results\white_followup_20261107\$Stage"
    previous_adoption=$previousAdoption
    launched_at=(Get-Date).ToString('o')
}
$receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $taskResult 'LAUNCH.json') -Encoding utf8
$receipt | ConvertTo-Json -Depth 10
