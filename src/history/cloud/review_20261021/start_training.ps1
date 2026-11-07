param([switch]$Resume)
$ErrorActionPreference = 'Stop'
$trainingDirectory = $PSScriptRoot
$projectDirectory = 'C:\Users\25911\Desktop\afdm-gfra'
$pythonExecutable = Join-Path $projectDirectory '.venv\Scripts\python.exe'
$preflight = Get-Content -LiteralPath (Join-Path $trainingDirectory 'protocol\PREFLIGHT.json') -Raw | ConvertFrom-Json
$manifestHash = (Get-FileHash -LiteralPath (Join-Path $trainingDirectory 'MANIFEST.json') -Algorithm SHA256).Hash.ToLower()
if ($preflight.status -ne 'PASSED' -or $preflight.manifest_sha256 -ne $manifestHash) { throw 'Preflight does not cover this frozen run.' }
if (!$Resume -and (Test-Path -LiteralPath (Join-Path $trainingDirectory 'TRAINING_LAUNCH.json'))) { throw 'Already launched; inspect before using -Resume.' }
$env:AFDM_LSTMP_ROOT = $projectDirectory
$env:AFDM_LSTMP_CONFIG = Join-Path $trainingDirectory 'source_code\experiments\lstmp_execution_v3_20261020\config.json'
$env:PYTHONUTF8 = '1'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$stdout = Join-Path $trainingDirectory ('stdout_' + $stamp + '.log')
$stderr = Join-Path $trainingDirectory ('stderr_' + $stamp + '.log')
$mode = if ($Resume) { '--resume' } else { '--fresh' }
$trainingProcess = Start-Process -FilePath $pythonExecutable -ArgumentList @('-u','-m','experiments.lstmp_execution_v3_20261020.train','--train',$mode,'--device','cuda') -WorkingDirectory (Join-Path $trainingDirectory 'source_code') -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
@{launcher_pid=$trainingProcess.Id; launched_at=(Get-Date).ToString('o'); training_run=$trainingDirectory; stdout=$stdout; stderr=$stderr; resume=[bool]$Resume; planned_updates=142500; manifest_sha256=$manifestHash} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $trainingDirectory 'TRAINING_LAUNCH.json') -Encoding UTF8
Write-Output ('V3 accelerated continuation launched: ' + $trainingProcess.Id)
