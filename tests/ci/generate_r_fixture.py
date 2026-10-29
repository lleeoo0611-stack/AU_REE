"""Synthetic MCDA fixtures for CI only: never merge into the research evidence DB."""
from pathlib import Path
import csv,sys
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
def emit(name,columns,rows):
    with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
criteria=['T1','D1','I1','C1']
emit('matrix.csv',['project_id','project_name',*criteria],[
    {'project_id':'SYNTHETIC-A','project_name':'Synthetic A','T1':1,'D1':5,'I1':12,'C1':3},
    {'project_id':'SYNTHETIC-B','project_name':'Synthetic B','T1':2,'D1':4,'I1':6,'C1':4},
    {'project_id':'SYNTHETIC-C','project_name':'Synthetic C','T1':3,'D1':3,'I1':20,'C1':2},
])
emit('criteria.csv',['criterion','domain','direction','unit','basis'],[
    {'criterion':c,'domain':'Synthetic','direction':orientation,'unit':'test','basis':'SYNTHETIC'}
    for c,orientation in [('T1','MIN'),('D1','MAX'),('I1','MIN'),('C1','MAX')]])
emit('weights.csv',['perspective','criterion','weight','status'],[
    {'perspective':'synthetic','criterion':c,'weight':0.25,'status':'CI_ONLY'} for c in criteria])
emit('ahp.csv',['criterion_a','criterion_b','ratio'],[
    {'criterion_a':a,'criterion_b':b,'ratio':1} for i,a in enumerate(criteria) for b in criteria[i+1:]])
emit('empty_matrix.csv',['project_id','project_name',*criteria],[])
print('Generated synthetic-only CI inputs at',out)
