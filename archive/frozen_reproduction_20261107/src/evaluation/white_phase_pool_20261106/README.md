# Persistent execution of the white estimated-phase SNR experiment

Authorized by the author on 2026-11-06 after measuring low GPU utilization.
This package changes execution only: reuse a receiver inside each worker, cache
the immutable input index, poll completion every 0.2 seconds, and allow up to
three workers under the existing RAM/VRAM admission checks. Two CPU threads per
worker and every numerical control remain unchanged. No frozen source is edited.

The existing `Receiver.infer` creates new per-input iteration state and resets
the seeded probes. Diagnostic counters are also cleared between inputs. Each
input still has its original input hashes, prediction arrays, inference record,
post-inference truth scoring, result hash, and unique pointer. Completed outputs
cannot be overwritten. New results identify this execution amendment while
retaining the unchanged scientific PLAN hash.

The result directory's `runtime_pool_20261106` contains authorization, amendment,
CPU checks, separate numerical validation arrays, drain/exit evidence, and
session receipts. Numerical validation compares sequential reused-model inputs
with saved fresh-process results, including a repeated input and the largest
observed iteration count. Decisions, phase, iteration counts and stopping
reasons must match; other arrays allow only FP32-scale roundoff. Validation
outputs never count toward the 6000 scientific inputs.

After the original STOP interface has drained both workers and the coordinator
has exited, preserve its records. A validated continuation rescans and re-scores
every completed output before dispatching missing inputs. The original final
three-method full-array report remains the completion gate.

Entry: `python -X utf8 -B -m evaluation.white_phase_pool_20261106.run coordinate`
with `PYTHONPATH=D:\afdm-gfra\src`. Launch hidden. `STOP.json` drains the pool;
failures stop new dispatch, retain all output, and never retry automatically.
Resume is the same command only after lock/process/failure/partial-output review.
Do not invoke a second coordinator or any of the older queue entrypoints.
