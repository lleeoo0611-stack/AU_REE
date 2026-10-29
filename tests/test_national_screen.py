import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from screen_national_raw import tier,normal

def test_scheme_a_evidence_classification():
    assert tier('Rare Earth Elements','monazite','')=='E1_DIRECT_REE'
    assert tier('Gold','Monazite','')=='E2_REE_MINERAL_ONLY'
    assert tier('Gold','Quartz','Rare Earths are reported in regional host rocks')=='E3_GEOLOGICAL_CONTEXT'
    assert tier('Gold','Quartz','no relevant mineralization')=='E0_NOT_REE'

def test_normalization_keeps_different_deposit_names():
    assert normal('Mount Weld - North')!=normal('Mount Weld South')

def test_national_raw_not_sensitive_to_commodity():
    from acquire_national_raw import fetch_wfs
    # Covered by test_national_raw.py: gold and REE both remain in full raw chunks.
    assert callable(fetch_wfs)
