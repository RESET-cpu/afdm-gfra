# Worker-state read and write repair

The previous independent repair covered coordinator reads only. On 2026-11-07,
a worker failed while replacing its BUSY state, before starting the next input.
This entry point applies the same bounded handling to both readers and writers.

Only `runtime_pool_20261106/sessions/<id>/worker<slot>/STATE.json` operations retry
PermissionError: 11 attempts separated by 0.05 seconds. Other errors, other file
operations and inference failures are not retried. Writes call the original atomic
JSON writer with the same value; no numerical computation or result is retried.

Coordinator and worker bootstrap use
`evaluation.white_phase_pool_stateio_20261107.run`. Both call the original pool
functions without changing their source or the inference/configuration/weights.
The module field in execution records identifies this bootstrap; the parent pool
amendment binding remains unchanged, with this additional adapter bound separately.

Use `coordinate` (without `--resume`) only after failure/process/output inspection.
The existing STOP, lock, resource, result-rescoring and skip-completed guards apply.
Evidence is in the result directory `runtime_pool_20261106/state_io_recovery_20261107/`.
