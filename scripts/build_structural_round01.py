"""Rebuild the bounded Structural Cohort evidence review, without granting gates.

The curated review ledger is an analytical input, never an approval ledger.
Offline checks use published hashes/locators; --verify-originals also checks the
local original-byte archive. A source map is never an approved GIS geometry.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'inputs/source_review_20261101/structural_round01_reviews.json'
SOURCES = ROOT / 'inputs/source_review_20261101/structural_round01_sources.json'
ACCESS = ROOT / 'inputs/source_review_20261101/structural_round01_access_manifest.json'
BASE = ROOT / 'docs/audits/2026-10-31_c1_c2_project_review_39.csv'
P1 = ROOT / 'inputs/source_review_20261031/p1_13_positive_case_gate_decisions.csv'
OUT = ROOT / 'docs/audits/structural_round01'
GATES = ('ID', 'ROLE', 'WINDOW', 'JORC', 'GIS_SOURCE')
CUTOFF = '2026-10-29'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate_review(r, sources):
    require(not r.get('approval_ref') and not r.get('researcher_signature'),
            'analytical ledger cannot grant independent approval')
    require(set(r['gates']) == set(GATES), 'five structural gates required')
    require(r['project_scope'] and r['deposits'] and r['reopen_condition'], 'unbounded project review')
    for gate, evidence in r['gates'].items():
        require(evidence['status'] in {'REVIEW_READY', 'REVIEW_PENDING', 'BLOCKED_EVIDENCE',
                                     'OUTSIDE_WINDOW', 'INACTIVE'}, 'invalid evidence status')
        require(evidence['reason'] and evidence['next_evidence'], 'gate needs reason and next evidence')
        for ref in evidence['source_ids']:
            require(ref in sources, 'unknown evidence document: ' + ref)
            source = sources[ref]
            require(r['review_group_id'] in source['review_group_ids'], 'source scope transfer denied')
            if evidence['status'] == 'REVIEW_READY':
                require(source['publication_date'] and source['publication_date'] <= CUTOFF,
                        'undated/post-cutoff source cannot resolve gate')
                require(source['access_status'] == 'ORIGINAL_BYTES_LOCAL', 'original required for readiness')
        if evidence['status'] == 'REVIEW_READY':
            require(evidence['source_ids'] and evidence['locator'], 'ready without source/locator')
    for resource in r['resources']:
        source=sources.get(resource['source_id'])
        require(source is not None, 'resource references unknown source')
        require(r['review_group_id'] in source['review_group_ids'],
                'resource source scope transfer denied')
        require(resource['basis'] and resource['scope'] and resource['next_evidence'], 'resource basis missing')
        if resource['same_scope_REO_evidence']:
            require(source['publication_date'] and source['publication_date'] <= CUTOFF,
                    'resource original is undated/post-cutoff')
            require(resource['publication_date'] == source['publication_date'],
                    'resource publication date mismatches original')
            require(resource['basis'] in {'TREO_IN_SITU', 'TREO_EX_Y_IN_SITU', 'REO_SCOPED_BREAKDOWN'},
                    'HM/MzEq/target cannot become REO')
            require(resource['source_id'] in sources and resource['locator'], 'resource needs original locator')
            require(sources[resource['source_id']]['access_status'] == 'ORIGINAL_BYTES_LOCAL',
                    'resource original unavailable')
            require(resource['publication_date'] and resource['publication_date'] <= CUTOFF,
                    'resource date invalid')
    for event in r['events']:
        source=sources.get(event['source_id'])
        require(source is not None, 'study event references unknown source')
        require(r['review_group_id'] in source['review_group_ids'],
                'study event source scope transfer denied')
        require(event['publication_date'] <= CUTOFF if event['publication_date'] else
                not event['study_original_verified'], 'unverified study date')
        if event['study_original_verified']:
            require(source['publication_date'] and source['publication_date'] <= CUTOFF,
                    'study original is undated/post-cutoff')
            require(event['publication_date'] == source['publication_date'],
                    'study event publication date mismatches original')
            require(event['source_id'] in sources and event['publication_date'] and event['locator'],
                    'study needs original/date/locator')
            require(sources[event['source_id']]['access_status'] == 'ORIGINAL_BYTES_LOCAL',
                    'study original unavailable')
            require(event['event_type'] in {'SCOPING', 'PFS', 'DFS', 'BFS'},
                    'regulatory scoping is not economic study')
    for gap in r['resolved_gaps']:
        source=sources.get(gap['source_id'])
        require(source is not None, 'resolved gap has unknown source')
        require(r['review_group_id'] in source['review_group_ids'],
                'resolved gap source scope transfer denied')


def csv_text(rows):
    require(bool(rows), 'empty output')
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator='\n', quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def validate_frozen_source_lineage(groups):
    """Bind documentary review groups to existing frozen source-target memberships.

    A Project review group must have source members, a consistent state/name,
    and a stable PRJ identity. Source and Deposit records remain distinct.
    """
    register = read_csv(ROOT / 'outputs/project_entity_register.csv')
    membership = read_csv(ROOT / 'outputs/project_entity_membership_487.csv')
    require(len(membership) == 487, 'frozen Census source membership count changed')
    target_ids = [r.get('target_id') for r in membership]
    require(all(target_ids) and len(set(target_ids)) == 487,
            'frozen Census source membership IDs missing or duplicated')

    group_by_id = {row['review_group_id']: row for row in groups}
    project_by_id = {row['entity_id']: row for row in register}
    require(len(project_by_id) == len(register) == len(group_by_id) == 39,
            'Project group identities do not match 39 frozen groups')
    require(set(group_by_id) == set(project_by_id),
            'documentary Project groups differ from Census Project entities')

    for pid, project in project_by_id.items():
        base = group_by_id[pid]
        require(project['entity_type'] == 'Project_candidate'
                and project['canonical_name'] == base['project_name']
                and project['state_or_territory'] == base['state'],
                'documentary group name, state or entity type differs from Census: ' + pid)

    linked_counts = Counter()
    for member in membership:
        pid = member.get('project_entity_id', '').strip()
        if not pid:
            require(member.get('relation') == 'UNRESOLVED_NO_PROJECT_LINK_INFERRED',
                    'unlinked target has unexpected Project relationship')
            continue
        require(pid in project_by_id, 'source target linked to unknown documentary group')
        require(member['state'] == project_by_id[pid]['state_or_territory'],
                'source state conflicts with documentary Project parent: ' + member['target_id'])
        require(member.get('relation') in ('PROJECT_LINK_REVIEWED_CANDIDATE',
                                           'REVIEW_GROUP_LINK_HOLD'),
                'source Project relation was promoted without independent review')
        linked_counts[pid] += 1
    require(all(linked_counts[pid] > 0 for pid in project_by_id),
            'documentary Project group lacks frozen source-target members')
    return {'frozen_source_target_count': len(membership),
            'reviewed_candidate_groups': len(project_by_id),
            'source_rows_linked_to_candidate_groups': sum(linked_counts.values()),
            'source_rows_without_candidate_group': len(membership)-sum(linked_counts.values())}


def build(verify_originals=False):
    reviews = json.loads(INPUT.read_text(encoding='utf-8'))
    definitions = json.loads(SOURCES.read_text(encoding='utf-8'))
    access = json.loads(ACCESS.read_text(encoding='utf-8'))
    base = read_csv(BASE)
    require(len(base) == len(reviews) == 39, '39 frozen groups required')
    validate_frozen_source_lineage(base)
    require({r['review_group_id'] for r in reviews} == {r['review_group_id'] for r in base},
            'frozen group IDs changed')
    require(len({r['review_group_id'] for r in reviews}) == 39, 'duplicate group')
    sm = {r['source_id']: r for r in access}
    require(len(sm) == len(access) == len(definitions), 'source manifest cardinality')
    for definition in definitions:
        record = sm[definition['source_id']]
        require(all(record[k] == definition[k] for k in definition), 'source inventory/manifest mismatch')
        if record['publication_date']:
            date.fromisoformat(record['publication_date'])
        if record['access_status'] == 'ORIGINAL_BYTES_LOCAL':
            require(len(record['sha256']) == 64 and record['byte_count'] > 0, 'original hash missing')
            if verify_originals:
                path = ROOT / record['archive_path']
                require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'],
                        'original archive missing or changed: ' + record['source_id'])
    base_idx = {r['review_group_id']: r for r in base}
    gap_ids = [gap['gap_id'] for r in reviews for gap in r['resolved_gaps']]
    require(len(gap_ids) == len(set(gap_ids)), 'duplicate gap reduction counted')
    for r in reviews:
        for gap in r['resolved_gaps']:
            require(gap['source_id'] in sm, 'gap resolution has no source')
            source = sm[gap['source_id']]
            require(source['access_status'] == 'ORIGINAL_BYTES_LOCAL' and
                    source['publication_date'] and source['publication_date'] <= CUTOFF,
                    'gap resolution requires dated original evidence')
    tables = {key: [] for key in ('identity_crosswalk', 'gate_evidence_resolution', 'resource_register',
                                  'study_stage_timeline', 'structural_candidates', 'c2_identity_review',
                                  'gap_priority_queue', 'criterion_coverage', 'source_gap_resolution')}
    for r in reviews:
        b = base_idx[r['review_group_id']]
        require(r['project_name'] == b['project_name'], 'renamed original project group')
        validate_review(r, sm)
        common = dict(review_group_id=r['review_group_id'], project_name=r['project_name'],
                      state=b['state'], snapshot_asof=CUTOFF)
        ready = sum(e['status'] == 'REVIEW_READY' for e in r['gates'].values())
        status = 'REVIEW_READY' if ready == 5 else 'BLOCKED_EVIDENCE'
        tables['identity_crosswalk'].append(dict(common, project_scope=r['project_scope'],
            deposits=r['deposits'], excluded_or_unresolved_entities=r['excluded_entities'],
            proposed_project_id=b['review_group_id'], verified_independent_project_id='',
            source_target_link='UNCHANGED_EXISTING_GROUP_NOT_NEW_PROJECT', product_role=r['product_role'],
            footprint_source=r['footprint_source'], geometry_role=r['geometry_role'],
            original_CRS=r['original_CRS'], review_depth=r['review_depth'],
            original_identity_decision=b['ID_gate'], approval_ref='', researcher_signature=''))
        for gate in GATES:
            e = r['gates'][gate]
            refs = e['source_ids']
            row = dict(common, gate=gate, original_gate=('GIS_RELEASE' if gate == 'GIS_SOURCE' else gate),
                original_decision=b['GIS_RELEASE_gate' if gate == 'GIS_SOURCE' else gate + '_gate'],
                evidence_status=e['status'], reason_code=e['reason'], source_ids='|'.join(refs),
                source_urls='|'.join(sm[s]['url'] for s in refs), locator=e['locator'],
                original_access_levels='|'.join(sm[s]['access_status'] for s in refs),
                original_sha256s='|'.join(sm[s]['sha256'] for s in refs),
                conflict_or_limit=e['limit'], next_required_evidence=e['next_evidence'],
                formal_gate_decision='UNCHANGED_HOLD', approval_ref='', researcher_signature='')
            tables['gate_evidence_resolution'].append(row)
            if e['status'] != 'REVIEW_READY':
                tables['gap_priority_queue'].append(dict(common, priority=r['priority'], gate=gate,
                    reason_code=e['reason'], next_required_evidence=e['next_evidence'],
                    stop_rule='NO_REPEAT_SAME_SOURCE_UNTIL_REOPEN_CONDITION', reopen_condition=r['reopen_condition']))
        for item in r['resources']:
            tables['resource_register'].append(dict(common, **item, approval_ref=''))
        for event in r['events']:
            tables['study_stage_timeline'].append(dict(common, **event, approval_ref=''))
        tables['structural_candidates'].append(dict(common, priority=r['priority'],
            ready_evidence_gates=ready, evidence_status=status,
            data_complete=(ready == 5), structural_eligibility='NOT_FORMALLY_APPROVED',
            independently_verified_project_id=False, same_scope_REO_evidence=any(x['same_scope_REO_evidence'] for x in r['resources']),
            dated_economic_study_original=any(x['study_original_verified'] for x in r['events']),
            original_access='|'.join(sorted({sm[x]['access_status'] for e in r['gates'].values() for x in e['source_ids']})),
            conflicts=r['conflicts'], next_action=r['reopen_condition'], C1_admitted=False,
            GIS_release_approved=False, readiness_scope='FIVE_DOCUMENTARY_GATES_INCLUDING_SOURCE_MAPPING_ONLY',
            core_panel='UNSELECTED', extended_panel='UNSELECTED'))
        c2_ready = all(r['gates'][g]['status'] == 'REVIEW_READY' for g in ('ID', 'ROLE'))
        tables['c2_identity_review'].append(dict(common, candidate_status='REVIEW_READY_ID_ROLE' if c2_ready else 'PENDING_ID_ROLE_EVIDENCE',
            identity_scope=r['project_scope'], ree_role=r['product_role'], footprint_ref=r['footprint_source'],
            verified_project_id='', C2_approved=False, approval_ref='', researcher_signature='',
            next_action='Independent ID/ROLE decision and vetted footprint metadata; ' + r['reopen_condition']))
        for c in json.loads((ROOT/'config/criteria.json').read_text(encoding='utf-8'))['criteria']:
            tables['criterion_coverage'].append(dict(common, criterion=c['code'], domain=c['domain'],
                evidence_status='SOURCE_LOCATED_REVIEW_PENDING' if c['code'] in r['coverage_source_ids'] else 'REVIEW_PENDING',
                source_ids='|'.join(r['coverage_source_ids'].get(c['code'], [])),
                value='', approval_ref='', panel_membership='UNSELECTED'))
        for resolution in r['resolved_gaps']:
            tables['source_gap_resolution'].append(dict(common, **resolution,
                reduction_unit='ONE_DEFINED_DOCUMENTARY_GAP_NOT_FORMAL_GATE', independent_approval=False))
    # P1 source cases are retained as source cases. Only reviewed proposals, no automatic joins.
    p1_rows = []
    for p in read_csv(P1):
        matches = [r for r in reviews if (p['source_case_name'] == r['project_name']) or
                   (p['case_id'] == 'P1G-0007' and r['project_name'] == 'Fingerboards Project') or
                   (p['case_id'] == 'P1X-0007' and r['project_name'].startswith('Wimmera'))]
        p1_rows.append(dict(case_id=p['case_id'], source_case_name=p['source_case_name'],
            original_source_row_count=p['source_row_count'],
            proposed_group_ids='|'.join(r['review_group_id'] for r in matches),
            crosswalk_status='PROPOSED_SCOPE_REVIEW_NOT_APPROVED' if matches else 'UNRESOLVED_NOT_MERGED',
            resource_scope_warning=p['missing_critical_evidence'],
            new_project_counted=False, approval_ref=''))
    tables['p1_case_crosswalk'] = p1_rows
    require(len(p1_rows) == 13, '13 P1 cases required')
    tables['gap_priority_queue'].sort(key=lambda r: (r['priority'], GATES.index(r['gate'])))
    candidates = tables['structural_candidates']
    counts = {g: dict(sorted(Counter(r['gates'][g]['reason'] for r in reviews
               if r['gates'][g]['status'] != 'REVIEW_READY').items())) for g in GATES}
    summary = dict(run_id='AU_REE_STRUCTURAL_R01_20261101', base_commit='d723bc431389ea56bbf2a5b905fa52a8a64b3fee', source_cutoff=CUTOFF,
        review_date='2026-11-01', groups_bounded_reviewed=39,
        technical_original_review_groups=sum(r['review_depth']=='TECHNICAL_ORIGINAL_PAGES' for r in reviews),
        group_review_depths=dict(Counter(r['review_depth'] for r in reviews)),
        source_urls_attempted=len(access), originals_archived=sum(r['access_status']=='ORIGINAL_BYTES_LOCAL' for r in access),
        pdf_originals_archived=sum(r['access_status']=='ORIGINAL_BYTES_LOCAL' and r['format']=='pdf' for r in access),
        new_independently_approved_project_IDs=0,
        source_supported_ID_ROLE_review_candidates=sum(r['candidate_status']=='REVIEW_READY_ID_ROLE' for r in tables['c2_identity_review']),
        same_scope_REO_source_evidence_projects=sum(r['same_scope_REO_evidence'] for r in candidates),
        JORC_documentary_review_ready_projects=sum(r['gates']['JORC']['status']=='REVIEW_READY' for r in reviews),
        dated_economic_study_original_projects=sum(r['dated_economic_study_original'] for r in candidates),
        structural_review_ready=sum(r['evidence_status']=='REVIEW_READY' for r in candidates),
        formal_structural_eligibility=0, C1_approved=0, C2_approved=0, C2_pending=39,
        readiness_scope='DOCUMENTARY_PACKET_NOT_OFFICIAL_GIS_RELEASE_OR_INDEPENDENT_APPROVAL',
        ready_gate_evidence_cells=sum(r['evidence_status']=='REVIEW_READY' for r in tables['gate_evidence_resolution']),
        remaining_gate_evidence_cells=sum(r['evidence_status']!='REVIEW_READY' for r in tables['gate_evidence_resolution']),
        documentary_gaps_resolved=len(tables['source_gap_resolution']), blocker_counts_by_gate=counts,
        GIS_release_approvals=0, core_panel='UNSELECTED', extended_panel='UNSELECTED', MCDA_executed=False,
        input_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (INPUT,SOURCES,ACCESS,BASE,P1,ROOT/'config/criteria.json')})
    result = {key+'.csv': csv_text(rows) for key, rows in tables.items()}
    result['summary.json'] = json.dumps(summary, ensure_ascii=False, indent=2) + '\n'
    return result, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    parser.add_argument('--verify-originals', action='store_true')
    args = parser.parse_args()
    outputs, summary = build(args.verify_originals)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (OUT/name).write_bytes(content.encode('utf-8'))
    else:
        for name, content in outputs.items():
            require((OUT/name).read_bytes() == content.encode('utf-8'), 'stale derived output: ' + name)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
