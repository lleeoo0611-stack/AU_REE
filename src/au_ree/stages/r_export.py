"""05: Prepare R parameters, data dictionary and a reproducible manifest.
The R calculation is a separate explicit action; no rank is fabricated without evidence.
"""
from __future__ import annotations
from ..core import digest, utc

def run(db,ctx):
    scenarios=ctx['eligibility']['scenarios']
    codes={r['code']:dict(r) for r in db.execute('SELECT * FROM criteria')}
    meta=[]
    for c,cc in codes.items():meta.append({'criterion':c,'domain':cc['domain'],'direction':cc['direction'],'unit':cc['unit'],'basis':cc['basis']})
    for scenario,definition in scenarios.items():
        # Blank Saaty judgments; never manufacture research preferences.
        active=definition['criteria']
        pairs=[{'criterion_a':a,'criterion_b':b,'ratio':'','scenario':scenario} for i,a in enumerate(active) for b in active[i+1:]]
        ctx['artifacts'][f'ahp_pairs_{scenario}.csv']=(pairs,['criterion_a','criterion_b','ratio','scenario'])
    ctx['artifacts']['r_criteria_dictionary.csv']=(meta,['criterion','domain','direction','unit','basis'])
    weights=[{'perspective':p,'criterion':c,'weight':v,'status':ctx['r_analysis']['weights_status']} for p,w in ctx['r_analysis']['weights'].items() for c,v in w.items()]
    ctx['artifacts']['r_weights.csv']=(weights,['perspective','criterion','weight','status'])
    settings=[{'key':k,'value':v} for k,v in ctx['r_analysis'].items() if isinstance(v,(str,int,float))]
    ctx['artifacts']['r_settings.csv']=(settings,['key','value'])
    summaries=[dict(x) for x in db.execute('SELECT scenario,COUNT(*) AS total,SUM(eligible) AS eligible,SUM(point_ready) AS point_ready FROM eligibility GROUP BY scenario')]
    ctx['artifacts']['r_scenarios.csv']=(summaries,['scenario','total','eligible','point_ready'])
    return {'r_script':'R/run_mcda.R','config':'config/r_analysis.json','scenarios':summaries,
            'status':'R_INPUTS_READY' if any((r['point_ready'] or 0)>1 for r in summaries) else 'R_INPUTS_EXPORTED_NO_RANKING'}
