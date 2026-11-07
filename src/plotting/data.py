"""Load saved summaries without importing receivers or running experiments."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass
class PlotData:
    experiment: str
    rows: list
    methods: list
    scenes: int
    metadata: dict

    def subset(self, **parameters):
        rows = [r for r in self.rows if all(r['parameters'].get(k)==v for k,v in parameters.items())]
        if not rows:
            raise ValueError(f'No saved rows for {parameters}')
        return PlotData(self.experiment, rows, self.methods, self.scenes, self.metadata)


def load(source, experiment):
    source = Path(source).resolve()
    if source.is_dir():
        source = source/'SUMMARY.json'
    if not source.exists():
        raise ValueError(f'No saved SUMMARY.json: {source}. Plotting never starts inference or creates results.')
    summary = read(source)
    plan_path = Path(summary.get('source_plan', source.parent/'PLAN.json'))
    if not plan_path.is_absolute():
        plan_path = source.parent/plan_path
    if not plan_path.exists():
        raise ValueError('The saved summary needs its source PLAN.json for experiment and condition identity.')
    plan = read(plan_path)
    if plan['experiment'] != experiment or summary.get('experiment',experiment) != experiment:
        raise ValueError(f'Expected {experiment}; the saved plan is {plan["experiment"]}.')
    if summary.get('status') not in ('COMPLETE','INTERIM'):
        raise ValueError('Use a complete summary or an audited, fully paired interim snapshot.')
    if summary.get('source_plan_sha256') and digest(plan_path)!=summary['source_plan_sha256']:
        raise ValueError('Source plan hash differs from the saved snapshot.')
    methods = list(plan['methods'])
    rows, keys, counts = [], set(), set()
    for saved in summary['rows']:
        row = dict(saved)
        method = row['method']
        if method not in methods:
            raise ValueError(f'Method not in saved plan: {method}')
        if 'parameters' in row:
            parameters = row['parameters']
        elif 'condition' in row:
            parameters = plan['conditions'][int(row['condition'])]
        else:
            candidates = [c for c in plan['conditions'] if all(row.get(k)==v for k,v in c.items() if k in row)]
            if len(candidates)!=1:
                raise ValueError('Cannot uniquely match snapshot row to a saved condition.')
            parameters = candidates[0]
        if parameters not in plan['conditions']:
            raise ValueError('Condition not present in the saved plan.')
        index = plan['conditions'].index(parameters)
        key = (method,index)
        if key in keys:
            raise ValueError(f'Duplicate method/condition: {key}')
        keys.add(key)
        count = row.get('completed',row.get('scenes'))
        if not isinstance(count,int) or count<=0:
            raise ValueError('Every plotted condition needs a positive physical-scene count.')
        counts.add(count)
        if not isinstance(row.get('nmse_db'),(int,float)) or not math.isfinite(row['nmse_db']):
            raise ValueError('A row is incomplete or has undefined NMSE.')
        if plan['experiment_kind']=='receiver':
            total = row['active']+row['inactive']
            aer = (row['misses']+row['false_alarms'])/total
            nmse = 10*math.log10(row['full_error']/row['signal_energy'])
            if not math.isclose(aer,row['aer'],abs_tol=1e-12) or not math.isclose(nmse,row['nmse_db'],abs_tol=1e-9):
                raise ValueError('Saved pooled metrics disagree with counts or energy sums.')
        else:
            nmse = 10*math.log10(row['error']/row['energy'])
            if not math.isclose(nmse,row['nmse_db'],abs_tol=1e-9):
                raise ValueError('Denoising NMSE disagrees with pooled energy sums.')
        row.update(parameters=dict(parameters),condition=index,scenes=count)
        rows.append(row)
    expected = {(m,i) for m in methods for i in range(len(plan['conditions']))}
    if keys!=expected or len(counts)!=1:
        raise ValueError('All methods and conditions must have the same fully paired scene set.')
    scenes = counts.pop()
    if summary['status']=='COMPLETE' and scenes!=plan['scene_count']:
        raise ValueError('Complete summary does not contain the planned scene count.')
    if summary['status']=='INTERIM':
        progress = summary.get('progress',{})
        ids = progress.get('full_scene_ids',[])
        if len(ids)!=scenes or len(set(ids))!=scenes or progress.get('fully_completed')!=scenes:
            raise ValueError('Interim summary must identify its complete, shared physical scenes.')
        audit_path = source.parent/'RESULT_AUDIT.json'
        # Exported manuscript data may retain a provenance link to the audited snapshot.
        if not audit_path.exists() and (source.parent/'PROVENANCE.json').exists():
            provenance = read(source.parent/'PROVENANCE.json')
            original = Path(provenance['source_summary'])
            if digest(source)!=provenance['source_summary_sha256'] or digest(original)!=digest(source):
                raise ValueError('Exported data differs from its audited source summary.')
            audit_path = original.parent/'RESULT_AUDIT.json'
        audit = read(audit_path)
        if audit.get('status') not in ('PASS','PASSED') or not audit.get('compact_rescoring_passed'):
            raise ValueError('Interim snapshot has no passing compact-output audit.')
    metadata = dict(source_summary=str(source),source_sha256=digest(source),source_plan=str(plan_path),
        source_plan_sha256=digest(plan_path),status=summary['status'],mode=plan.get('mode'),
        planned_scenes=plan['scene_count'],phase_mode=plan.get('phase_mode'),noise_mode=plan.get('noise_mode'),
        timing=summary.get('timing',plan.get('timing','')),parallel_execution=plan.get('parallel_execution'),
        scene_ids=summary.get('progress',{}).get('full_scene_ids'),
        labels={m:plan['algorithm_specs'][m]['label'] for m in methods})
    return PlotData(experiment,rows,methods,scenes,metadata)
