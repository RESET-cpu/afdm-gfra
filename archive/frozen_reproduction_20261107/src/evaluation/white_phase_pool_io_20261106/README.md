# Coordinator state-read repair

The 2026-11-06 pool coordinator stopped after a `PermissionError` opening an
atomically published worker `STATE.json`. Both workers finished their assigned
inputs and exited. This independent entry point retains the original pool code,
worker command, inference, model bindings, memory gates, and result protocol.

Only coordinator reads of `runtime_pool_20261106/sessions/<id>/worker<slot>/STATE.json`
retry `PermissionError`: 11 attempts separated by 0.05 seconds (at most 0.5 seconds
of waiting). Successful retries and exhausted retries are recorded. Invalid JSON,
missing files, other file reads, and inference failures are not retried.

Use `python -X utf8 -B -m evaluation.white_phase_pool_io_20261106.run coordinate`
after checking the recorded incident, preserved failure, source hashes, complete
result validation and process exit. The original coordinator still checks
STOP/FAILURE/COMPLETION, exclusive lock and live processes, validates all prior
saved arrays, and skips completed inputs. No `--resume` argument is used.

Evidence: result directory `runtime_pool_20261106/io_recovery_20261106/`.
