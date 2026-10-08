"""Conditional task estimates and family-aware descriptive uncertainty."""
from fractions import Fraction
import random

from ..rollback_pilot.analysis import number
from ..rollback_pilot.cohort_v1.analysis import analyze as prior_analyze

SEED=2026100837


def family_view(rows,domain):
    eligible=[r for r in rows if r['domain']==domain and r['primary_scheduled']]
    groups={}
    for row in eligible:
        scores=row['grades']['K']+row['grades']['R']
        difference=Fraction(sum(row['grades']['R'])-sum(row['grades']['K']),2) if None not in scores else None
        groups.setdefault(row['stratum'],[]).append({'task_id':row['task_id'],'difference':number(difference)})
    complete={family:[Fraction(x['difference']['fraction']) for x in tasks if x['difference'] is not None]
              for family,tasks in groups.items()}
    means={family:sum(values,Fraction(0))/len(values) for family,values in complete.items() if values}
    interval=None
    if domain=='coding' and len(means)>=6:
        rng=random.Random(SEED);families=sorted(means);samples=[]
        for _ in range(10000):
            chosen=rng.choices(families,k=len(families))
            values=[x for family in chosen for x in complete[family]]
            samples.append(sum(values,Fraction(0))/len(values))
        samples.sort();interval={'kind':'descriptive_family_resampling_95_percent','seed':SEED,'resamples':10000,
            'lower':number(samples[250]),'upper':number(samples[9750]),'eligible_complete_families':len(means),
            'scope':'within these sampled algorithmic families; not confirmatory or inference to all coding'}
    return {'eligible_tasks':len(eligible),'represented_families':len(groups),'families':groups,
            'complete_family_means':{k:number(v) for k,v in means.items()},'family_resampling':interval,
            'interval_unavailable_reason':None if interval else 'fewer than six represented complete coding families, or three fixed mathematical strata',
            'variants_are_independent_families':False,'provider_sampling_seed':None}


def analyze(rows,events):
    result=prior_analyze(rows,events)
    result['evidence_kind']='new_math_development_followup_low_initial_medium_recovery_with_protocol_diagnostics'
    for domain in ('math','coding'):
        result['domains'][domain]['complete_pair_screen_at_least_six']=result['domains'][domain]['primary_R_minus_K']['complete_tasks']>=6
        result['domains'][domain]['family_analysis']=family_view(rows,domain)
        result['domains'][domain]['task_resampling_scope']='conditional on the constructed task set; shared coding templates are not independent families'
    result['confirmatory_p_value']=None
    result['human_measures_scope']='optional masked independent ratings unperformed; not used for objective eligibility'
    return result


def markdown(result):
    lines=['# Mathematical rollback follow-up results','',
        'New fixed 32-task mathematical cohort, GPT-6 Luna through the Codex subscription.',
        'Initial checkpoint/branch effort is low; writers and all terminal arms are medium.',
        'Three fixed mathematical construction strata. Coding calibration is excluded.','',
        '| Domain | Selected | Initial correct | Public failures | K/R scheduled | K/R complete | R minus K (pp) |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for domain,r in result['domains'].items():
        p=r['primary_R_minus_K'];mean=p['complete_pair_mean']
        lines.append(f"| {domain} | {r['selected_tasks']} | {r['initial_candidates_correct']} | {r['public_failure_tasks']} | {p['scheduled_tasks']} | {p['complete_tasks']} | {mean['percentage_points'] if mean else 'unidentified'} |")
    lines+=['','Every selected task, public-pass stop, unusable writer, unperformed slot and unknown',
        'outcome is retained. Two draws are repeated measurements on one task. Family analyses,',
        'all four condition totals, secondary intersections, missingness bounds, exact rejected',
        'candidate repetition and resources are saved in analysis.json. Optional human measures',
        'remain unknown. There is no confirmatory p-value or native-harness claim.','']
    r=result['resources'];lines+=[f"Complete generations: {r['known_completed_calls']}; unresolved: {r['unknown_or_pending_calls']}.",
        f"Calculated planning credits: {r['shared_experiment_planning_credits']}; actual account charge unavailable.",
        'Reasoning is included in output. Projections are not independent policy runs or additive actual charges.','']
    return '\n'.join(lines)
