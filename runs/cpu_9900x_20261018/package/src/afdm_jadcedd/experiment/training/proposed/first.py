"""Continue the common first-order score on the full-geometry channel prior."""
from pathlib import Path
from copy import deepcopy
import json
import math
import os
import time

from afdm_jadcedd.project import ROOT
import numpy as np
import torch
from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
from afdm_jadcedd.experiment.training.scores.checkpoints import save_direct_checkpoint
from afdm_jadcedd.experiment.training.scores.direct_objectives import direct_first_loss
from afdm_jadcedd.experiment.training.scores.trainer import ScoreTrainer, cpu_state
from afdm_jadcedd.utils import sha256, write_json
from .continuation import import_first


def learning_rate(settings, epoch):
    schedule = settings.get('continuation_schedule', {})
    start = schedule.get('start_epoch', 1)
    fraction = (epoch-start)/max(settings['maximum_epochs']-start, 1)
    high = schedule.get('start_learning_rate', settings['learning_rate'])
    low = settings['minimum_learning_rate']
    if epoch < start or not low <= high:
        raise ValueError('Invalid first-score learning-rate continuation')
    return low + .5*(high-low)*(1+math.cos(math.pi*fraction))


class SharedFirstTrainer(ScoreTrainer):
    def run(self, configuration, prior, data, specification_hash):
        settings = configuration['first']
        initial = ROOT / settings['initial_checkpoint']
        if sha256(initial) != settings['initial_checkpoint_sha256']:
            raise ValueError('Warm-start checkpoint identity changed')
        torch.manual_seed(settings['seed'])
        rng = np.random.default_rng(settings['seed'])
        model, blob = load_direct_checkpoint(initial, self.device)
        if blob['order'] != 1 or blob['global_complex_rms'] != configuration['scale']:
            raise ValueError('First score and shared training coordinates differ')
        # Reuse the original DSM and complete fixed-noise validation machinery.
        recipe = dict(scores=dict(global_complex_rms=configuration['scale'], normalization='population_rms'),
                      training=dict(architecture=blob['config'], validation_seed=settings['validation_seed'],
                                    microbatch_size=settings['microbatch_size']))
        ema = deepcopy(model).eval()
        optimizer = torch.optim.Adam(model.parameters(), lr=settings['learning_rate'])
        last = self.output/'last.pt'
        best_path = self.output/'first_best.pt'
        epoch, cursor, steps, best, meaningful_best, stale = 1, 0, 0, math.inf, math.inf, 0
        indices, history, loss_sum, seen = None, [], 0., 0
        continuation = None
        last_saved = time.time()

        def save_best(score, selected_epoch, destination=None):
            save_direct_checkpoint(destination or best_path, ema, scale=configuration['scale'],
                metadata=dict(epoch=selected_epoch, validation=score, first_sha256=None,
                              objective='direct_cai_dsm', specification_sha256=specification_hash,
                              prior_definition_sha256=sha256(ROOT/configuration['prior_definition']),
                              initialization_sha256=settings['initial_checkpoint_sha256'],
                              continuation=continuation,
                              training_scope='Full-geometry training; continuation provenance records any inherited trajectory'))

        def checkpoint():
            nonlocal last_saved
            state = dict(schema='full-geometry-shared-first-resume-v1', specification_sha256=specification_hash,
                         model=cpu_state(model), ema=cpu_state(ema), optimizer=optimizer.state_dict(),
                         rng=rng.bit_generator.state, torch_rng=torch.get_rng_state(), mps_rng=self.device_rng(),
                         epoch=epoch, cursor=cursor, steps=steps, indices=indices, best=best,
                         meaningful_best=meaningful_best, stale=stale, history=history,
                         loss_sum=loss_sum, seen=seen, continuation=continuation)
            temporary = last.with_suffix('.tmp')
            torch.save(state, temporary)
            temporary.replace(last)
            last_saved = time.time()

        complete = self.output/'complete.json'
        if complete.exists():
            record = json.loads(complete.read_text())
            if (record['specification_sha256'] != specification_hash
                    or record['weight_sha256'] != sha256(best_path)):
                raise ValueError('Completed first-stage artifacts changed')
            self.status('COMPLETED', **{key: record[key] for key in ('selected_epoch', 'stopping_reason')})
            return True
        state = None
        imported = False
        if last.exists():
            state = torch.load(last, map_location='cpu', weights_only=False)
            if state['specification_sha256'] != specification_hash:
                raise ValueError('Resume specification changed')
            continuation = state.get('continuation')
        elif settings.get('continuation'):
            state, continuation = import_first(configuration, self.output, specification_hash, self.device)
            imported = True
        if state is not None:
            model.load_state_dict(state['model'])
            ema.load_state_dict(state['ema'])
            optimizer.load_state_dict(state['optimizer'])
            for row in optimizer.state.values():
                for key, value in row.items():
                    if torch.is_tensor(value) and key != 'step':
                        row[key] = value.to(self.device)
            rng.bit_generator.state = state['rng']
            torch.set_rng_state(state['torch_rng'])
            self.restore_device_rng(state)
            epoch, cursor, steps, indices = (state[k] for k in ('epoch', 'cursor', 'steps', 'indices'))
            best, meaningful_best, stale, history = (state[k] for k in ('best', 'meaningful_best', 'stale', 'history'))
            loss_sum, seen = state['loss_sum'], state['seen']
            del state
            if imported:
                checkpoint()
            self.status('CONTINUED' if imported else 'RESUMED', epoch=epoch, samples=cursor, optimizer_steps=steps)
        else:
            self.status('VALIDATING_WARM_START', samples=len(data['validation']))
            score = self.validation(ema, None, data['validation'], recipe, 'first')
            best = meaningful_best = score['loss']
            write_json(self.output/'baseline.json', score)
            save_best(score, 0)
            checkpoint()
            self.status('WARM_START_VALIDATED', validation_loss=score['loss'], validation_nmse_db=score['nmse_db'])
        reason = 'MAXIMUM_TRAINING_BUDGET'
        while epoch <= settings['maximum_epochs']:
            start = time.time()
            rate = learning_rate(settings, epoch)
            for group in optimizer.param_groups:
                group['lr'] = rate
            model.train()
            if indices is None:
                indices = rng.permutation(len(data['train']))
            while cursor < len(indices):
                if self.stop or (self.output/'pause.request').exists():
                    checkpoint()
                    self.status('PAUSED', epoch=epoch, samples=cursor, optimizer_steps=steps, resumable=True)
                    return False
                chosen = indices[cursor:cursor+settings['batch_size']]
                optimizer.zero_grad(set_to_none=True)
                for offset in range(0, len(chosen), settings['microbatch_size']):
                    part = chosen[offset:offset+settings['microbatch_size']]
                    h, r, v, labels = self.make_batch(np.asarray(data['train'][part]), rng, recipe)
                    ht, rt, vt = (torch.as_tensor(x, device=self.device) for x in (h, r, v))
                    lt = torch.as_tensor(labels, device=self.device)
                    loss = direct_first_loss(model(rt, lt), rt, ht, vt)
                    value = float(loss.detach().cpu())
                    if not np.isfinite(value):
                        raise FloatingPointError('Nonfinite DSM loss; saved checkpoint preserved')
                    (loss*len(part)/len(chosen)).backward()
                    loss_sum += value*len(part)
                    seen += len(part)
                torch.nn.utils.clip_grad_norm_(model.parameters(), settings['gradient_clip'], error_if_nonfinite=True)
                optimizer.step()
                cursor += len(chosen)
                steps += 1
                with torch.no_grad():
                    for average, current in zip(ema.parameters(), model.parameters()):
                        average.lerp_(current, 1-settings['ema_decay'])
                if time.time()-last_saved >= settings['checkpoint_seconds']:
                    checkpoint()
                if steps % 10 == 0:
                    self.status('TRAINING', epoch=epoch, maximum_epochs=settings['maximum_epochs'],
                                samples=cursor, training_samples=len(indices), optimizer_steps=steps,
                                loss=loss_sum/seen, learning_rate=rate,
                                elapsed_epoch_seconds=time.time()-start)
            self.status('VALIDATING', epoch=epoch, optimizer_steps=steps)
            score = self.validation(ema, None, data['validation'], recipe, 'first')
            history.append(dict(epoch=epoch, train_loss=loss_sum/seen, validation=score,
                                learning_rate=rate, seconds_this_invocation=time.time()-start))
            write_json(self.output/'history.json', history)
            if score['loss'] < best:
                best = score['loss']
                save_best(score, epoch)
            if score['loss'] < meaningful_best*(1-settings['meaningful_relative_improvement']):
                meaningful_best, stale = score['loss'], 0
            else:
                stale += 1
            self.status('EPOCH_COMPLETE', epoch=epoch, optimizer_steps=steps,
                        validation_loss=score['loss'], validation_nmse_db=score['nmse_db'],
                        best_validation_loss=best, validation_plateau_epochs=stale)
            finished_epoch = epoch
            epoch += 1
            cursor, indices, loss_sum, seen = 0, None, 0., 0
            checkpoint()
            if (finished_epoch >= settings['minimum_epochs']
                    and stale >= settings['validation_patience']):
                reason = 'VALIDATION_PLATEAU'
                break
        final_path = self.output/'first_final.pt'
        save_best(history[-1]['validation'], epoch-1, destination=final_path)
        selected = torch.load(best_path, map_location='cpu', weights_only=False)
        record = dict(status='COMPLETED', stopping_reason=reason, optimization_converged_proven=False,
                      epochs=len(history), optimizer_steps=steps, selected_epoch=selected['metadata']['epoch'],
                      validation=selected['metadata']['validation'], weight_sha256=sha256(best_path),
                      specification_sha256=specification_hash,
                      final_weight_sha256=sha256(final_path), continuation=continuation,
                      route_specific_training_completed=False, receiver_evaluation_completed=False)
        write_json(complete, record)
        self.status('COMPLETED', stopping_reason=reason, epochs=len(history), optimizer_steps=steps,
                    selected_epoch=record['selected_epoch'], weight_sha256=record['weight_sha256'])
        return True
