"""Scientific evidence boundaries and reproducibility, not inferred approvals."""
import copy
import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import build_structural_round01 as m
from scripts import build_c0_freeze_c1_c2_v1 as cohort_module


class StructuralRound01Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviews = json.loads(m.INPUT.read_text(encoding='utf-8'))
        cls.sources = {x['source_id']: x for x in json.loads(m.ACCESS.read_text(encoding='utf-8'))}

    def jupiter(self):
        return copy.deepcopy(next(r for r in self.reviews if r['project_name'].startswith('Jupiter')))

    def test_fixed_groups_and_separate_source_case_denominator(self):
        outputs, summary = m.build()
        self.assertEqual(summary['groups_bounded_reviewed'], 39)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(outputs['gate_evidence_resolution.csv'])))), 195)
        cases = list(csv.DictReader(io.StringIO(outputs['p1_case_crosswalk.csv'])))
        self.assertEqual(len(cases), 13)
        self.assertTrue(all(x['new_project_counted']=='False' for x in cases))

    def test_documentary_groups_have_the_correct_frozen_source_parents(self):
        result = m.validate_frozen_source_lineage(m.read_csv(m.BASE))
        self.assertEqual(result['frozen_source_target_count'], 487)
        self.assertEqual(result['reviewed_candidate_groups'], 39)
        self.assertEqual(result['source_rows_linked_to_candidate_groups'], 78)
        self.assertEqual(result['source_rows_without_candidate_group'], 409)

        actual_read = m.read_csv
        def corrupt(path):
            rows = actual_read(path)
            if path.name == 'project_entity_membership_487.csv':
                rows[0]['project_entity_id'] = 'PRJ-DOES-NOT-EXIST'
            return rows
        with patch.object(m, 'read_csv', side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, 'unknown documentary group'):
                m.validate_frozen_source_lineage(actual_read(m.BASE))

    def test_stale_partial_signed_gate_cannot_enter_structural_snapshot(self):
        original_read = m.read_csv
        groups = original_read(m.BASE)
        verified = copy.deepcopy(groups)
        verified[0]["JORC_gate"] = "PASS_SYNTHETIC_PARTIAL_GATE"
        def supplied(path):
            if path.name == 'c1_c2_project_gate_signoffs_v1.csv':
                return [{"decision_status": "PASS"}]
            return original_read(path)
        with patch.object(m, 'read_csv', side_effect=supplied):
            with patch.object(cohort_module, 'build',
                              return_value=([], verified, [], {})):
                with self.assertRaisesRegex(ValueError,
                                            "Structural signed release differs"):
                    m.build(identity_db=object())

    def test_frozen_source_missing_orphaned_project_group_blocked(self):
        actual_read = m.read_csv
        def drop_link(path):
            rows = actual_read(path)
            if path.name == 'project_entity_membership_487.csv':
                for row in rows:
                    if row['project_entity_id'] == 'PRJ-679f5da200a4564c':
                        row['project_entity_id'] = ''
                        row['relation'] = 'UNRESOLVED_NO_PROJECT_LINK_INFERRED'
            return rows
        with patch.object(m, 'read_csv', side_effect=drop_link):
            with self.assertRaisesRegex(ValueError, 'lacks frozen source-target'):
                m.validate_frozen_source_lineage(actual_read(m.BASE))

    def test_nolans_dated_government_fid_remains_outside_prefid_without_approval(self):
        """A dated public government report is evidence, not a signed Project gate."""
        row = next(r for r in self.reviews if r['review_group_id'] == 'PRJ-7f2aa9b3a0cabe53')
        event = next(e for e in row['events'] if e['event_type'] == 'FID_DATE_CORROBORATION')
        self.assertEqual(event['source_id'], 'R01-S27')
        self.assertEqual(event['publication_date'], '')
        self.assertEqual(event['effective_date'], '')
        self.assertIn('27-Oct-2026', event['locator'])
        self.assertIn('21-May-2026', event['locator'])
        self.assertFalse(event['study_original_verified'])
        self.assertEqual(row['gates']['WINDOW']['status'], 'OUTSIDE_WINDOW')
        self.assertEqual(row['gates']['WINDOW']['reason'],
                         'GOVERNMENT_FID_PUBLIC_LOCATOR_ARCHIVE_DATE_REVIEW_PENDING')
        self.assertEqual(self.sources['R01-S27']['access_status'], 'ORIGINAL_BYTES_LOCAL')
        self.assertEqual(self.sources['R01-S27']['sha256'],
                         '2bbc7f637693bd71e7875a170cf236e50b8e517a24c6244e072724312debb200')
        outputs, summary = m.build()
        studies = list(csv.DictReader(io.StringIO(outputs['study_stage_timeline.csv'])))
        same = [x for x in studies if x['review_group_id'] == row['review_group_id']]
        self.assertEqual(len(same), 2)
        self.assertTrue(any(x['event_type'] == 'FID_DATE_CORROBORATION' for x in same))
        cohort = m.read_csv(m.BASE)
        self.assertEqual(summary['C1_approved'],
                         sum(x['C1_release_status'] == 'C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES' for x in cohort))
        self.assertEqual(summary['C2_approved'],
                         sum(x['C2_project_id_approved'] == 'YES' for x in cohort))
        self.assertEqual(summary['dated_economic_study_original_projects'], 8)

    def test_copi_archived_contractor_supports_documentary_id_role_only(self):
        copi = copy.deepcopy(next(r for r in self.reviews
                                  if r['review_group_id'] == 'PRJ-42437b4a11115372'))
        source = self.sources['R01-CO-PFS-CONTRACTOR']
        self.assertEqual(source['publication_date'], '2025-09-30')
        self.assertEqual(source['access_status'], 'ORIGINAL_BYTES_LOCAL')
        self.assertEqual(source['sha256'],
                         'd6e9d2f503854ab05e9da0060ca6578ed11836fe6f9b61083e51418bcf05c8cc')
        for name in ('ID', 'ROLE'):
            self.assertEqual(copi['gates'][name]['status'], 'REVIEW_READY')
            self.assertEqual(copi['gates'][name]['source_ids'], ['R01-CO-PFS-CONTRACTOR'])
            self.assertIn('Independent', copi['gates'][name]['next_evidence'])
        for name in ('WINDOW', 'JORC', 'GIS_SOURCE'):
            self.assertNotEqual(copi['gates'][name]['status'], 'REVIEW_READY')
        self.assertFalse(any(x['same_scope_REO_evidence'] for x in copi['resources']))
        m.validate_review(copi, self.sources)

        bad_sources = copy.deepcopy(self.sources)
        bad_sources['R01-CO-PFS-CONTRACTOR']['publication_date'] = ''
        with self.assertRaisesRegex(ValueError, 'undated/post-cutoff source'):
            m.validate_review(copi, bad_sources)

        bad_sources = copy.deepcopy(self.sources)
        bad_sources['R01-CO-PFS-CONTRACTOR']['access_status'] = 'SOURCE_UNAVAILABLE'
        with self.assertRaisesRegex(ValueError, 'original required for readiness'):
            m.validate_review(copi, bad_sources)

        outputs, summary = m.build()
        rows = list(csv.DictReader(io.StringIO(outputs['c2_identity_review.csv'])))
        record = next(x for x in rows if x['review_group_id'] == copi['review_group_id'])
        self.assertEqual(record['candidate_status'], 'REVIEW_READY_ID_ROLE')
        coproject = next(b for b in m.read_csv(m.BASE) if b['review_group_id'] == copi['review_group_id'])
        self.assertEqual(record['C2_approved'], str(coproject['C2_project_id_approved'] == 'YES'))
        self.assertEqual(summary['ready_gate_evidence_cells'], 29)
        self.assertEqual(summary['remaining_gate_evidence_cells'], 166)
        self.assertEqual(summary['source_supported_ID_ROLE_review_candidates'], 9)
        self.assertEqual(summary['C1_approved'], sum(
            b['C1_release_status'] == 'C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES' for b in m.read_csv(m.BASE)))
        self.assertEqual(summary['C2_approved'], sum(
            b['C2_project_id_approved'] == 'YES' for b in m.read_csv(m.BASE)))

    def test_structural_signed_c2_requires_authenticated_cohort(self):
        gid = 'PRJ-42437b4a11115372'  # Copi has real document-ready ID and ROLE.
        original_read=m.read_csv
        copied=[dict(r) for r in original_read(m.BASE)]
        project=next(r for r in copied if r['review_group_id']==gid)
        project['C2_project_id_approved']='YES'
        project['formal_identity_signoff']='SYNTHETIC-APP'
        def fixture(path):
            if path==m.BASE:
                return copied
            if path.name == 'c1_c2_project_gate_signoffs_v1.csv':
                return [{'review_group_id':gid,'cohort':'C2','gate_id':gate,
                         'decision_status':'PASS','approval_ref':'SYNTHETIC-APP',
                         'reviewer_id':'Synthetic Reviewer'} for gate in ('ID','ROLE')]
            if path.name == 'c1_c2_project_identity_metadata_v1.csv':
                return [{'review_group_id':gid,'verified_project_id':'SYNTHETIC-ID'}]
            return original_read(path)
        with patch.object(m,'read_csv',side_effect=fixture):
            with self.assertRaisesRegex(ValueError,'requires independently approved identity'):
                m.build()
            # Stubbed trusted cohort only tests propagation. Cryptographic
            # gate validation is exercised with real bytes/SQLite in cohort tests.
            with patch.object(cohort_module,'build',
                              return_value=([],copied,[],{})):
                outputs,summary=m.build(identity_db=object())
        rows=list(csv.DictReader(io.StringIO(outputs['c2_identity_review.csv'])))
        row=next(r for r in rows if r['review_group_id']==gid)
        self.assertEqual(row['C2_approved'],'True')
        self.assertEqual(row['verified_project_id'],'SYNTHETIC-ID')
        self.assertEqual(summary['C2_approved'],1)

    def test_structural_c1_cannot_pass_with_unready_originals(self):
        gid='PRJ-42437b4a11115372'
        original_read=m.read_csv
        copied=[dict(r) for r in original_read(m.BASE)]
        project=next(r for r in copied if r['review_group_id']==gid)
        project['C2_project_id_approved']='YES'
        project['formal_identity_signoff']='SYNTHETIC-ID-APP'
        project['C1_release_status']='C1_ADMITTED_ALL_SIX_INDEPENDENT_GATES'
        def fixture(path):
            if path==m.BASE:
                return copied
            return original_read(path)
        with patch.object(m,'read_csv',side_effect=fixture):
            with patch.object(cohort_module,'build',return_value=([],copied,[],{})):
                with self.assertRaisesRegex(ValueError,
                                            'five ready documentary evidence gates'):
                    m.build(identity_db=object())

    def test_sqlite_approved_crosswalk_requires_same_signed_cohort(self):
        from reproducibility.build_census_database import validate_signed_structural_import
        outputs,_=m.build()
        names=('identity_crosswalk','c2_identity_review','structural_candidates')
        raw={name:list(csv.DictReader(io.StringIO(outputs[name+'.csv']))) for name in names}
        cohort=cohort_module.build()[1]
        self.assertEqual(validate_signed_structural_import(raw,cohort,'2026-10-29'),[])
        gid='PRJ-42437b4a11115372'
        signed=copy.deepcopy(cohort)
        accepted=next(r for r in signed if r['review_group_id']==gid)
        accepted['C2_project_id_approved']='YES'
        accepted['formal_identity_signoff']='SYNTHETIC-APP'
        candidate=copy.deepcopy(raw)
        project=next(r for r in candidate['identity_crosswalk'] if r['review_group_id']==gid)
        project['verified_independent_project_id']='SYNTHETIC-ID'
        project['approval_ref']='SYNTHETIC-APP'
        c2=next(r for r in candidate['c2_identity_review'] if r['review_group_id']==gid)
        c2['C2_approved']='True'
        c2['verified_project_id']='SYNTHETIC-ID'
        c2['approval_ref']='SYNTHETIC-APP'
        structural=next(r for r in candidate['structural_candidates'] if r['review_group_id']==gid)
        structural['independently_verified_project_id']='True'
        self.assertEqual(validate_signed_structural_import(candidate,signed,'2026-10-29'),
                         [(gid,'SYNTHETIC-ID','SYNTHETIC-APP')])
        with self.assertRaisesRegex(ValueError,'not reconciled'):
            validate_signed_structural_import(
                {**candidate,'identity_crosswalk':[{
                    **r, 'approval_ref':'FORGED-REF' if r['review_group_id']==gid
                    else r['approval_ref']} for r in candidate['identity_crosswalk']]},
                signed,'2026-10-29')
        with self.assertRaisesRegex(ValueError,'Unapproved Project identity'):
            validate_signed_structural_import(candidate,cohort,'2026-10-29')
        with self.assertRaisesRegex(ValueError,'source cutoff'):
            validate_signed_structural_import(candidate,signed,'2026-10-28')

    def test_date_leak_and_undated_source_rejected(self):
        for bad_date in ('2026-10-30', ''):
            sources = copy.deepcopy(self.sources)
            sources['R01-JU-MRE']['publication_date'] = bad_date
            with self.assertRaisesRegex(ValueError, 'undated/post-cutoff'):
                m.validate_review(self.jupiter(), sources)

    def test_cross_project_resource_transfer_rejected(self):
        row = self.jupiter()
        row['gates']['ID']['source_ids'] = ['R01-BR-DFS']
        with self.assertRaisesRegex(ValueError, 'scope transfer'):
            m.validate_review(row, self.sources)

    def test_jorc_resource_cannot_borrow_other_project_source(self):
        row = self.jupiter()
        resource = next(x for x in row['resources'] if x['same_scope_REO_evidence'])
        resource['source_id'] = 'R01-BR-DFS'
        with self.assertRaisesRegex(ValueError, 'resource source scope transfer denied'):
            m.validate_review(row, self.sources)

    def test_resource_publication_must_equal_cited_original(self):
        row = self.jupiter()
        resource = next(x for x in row['resources'] if x['same_scope_REO_evidence'])
        resource['publication_date'] = '2025-01-01'
        with self.assertRaisesRegex(ValueError, 'resource publication date mismatches original'):
            m.validate_review(row, self.sources)

    def test_dated_nonstudy_event_requires_matching_archived_source_metadata(self):
        browns = next(r for r in self.reviews if r['project_name'].startswith('Browns Range'))
        source_event = next(e for e in browns['events'] if e['event_type'] == 'FID_DELAY')
        self.assertEqual(source_event['publication_date'], '2026-09-30')
        bad = copy.deepcopy(browns)
        entry = next(e for e in bad['events'] if e['event_type'] == 'FID_DELAY')
        entry['publication_date'] = '2026-10-01'
        with self.assertRaisesRegex(ValueError, 'event publication date mismatches archived'):
            m.validate_review(bad, self.sources)

        bad = copy.deepcopy(browns)
        entry = next(e for e in bad['events'] if e['event_type'] == 'FID_DELAY')
        entry['publication_date'] = ''
        with self.assertRaisesRegex(ValueError, 'effective event date requires verified'):
            m.validate_review(bad, self.sources)

        altered_sources = copy.deepcopy(self.sources)
        altered_sources['R01-BR-FID']['access_status'] = 'SOURCE_UNAVAILABLE'
        with self.assertRaisesRegex(ValueError, 'dated event requires archived original bytes'):
            m.validate_review(browns, altered_sources)

    def test_event_effective_date_after_cutoff_rejected(self):
        browns = next(r for r in self.reviews if r['project_name'].startswith('Browns Range'))
        bad = copy.deepcopy(browns)
        entry = next(e for e in bad['events'] if e['event_type'] == 'FID_DELAY')
        entry['effective_date'] = '2026-10-30'
        with self.assertRaisesRegex(ValueError, 'event effective date after source cutoff'):
            m.validate_review(bad, self.sources)

        bad = copy.deepcopy(browns)
        entry = next(e for e in bad['events'] if e['event_type'] == 'FID_DELAY')
        entry['publication_date'] = '2026-10-30'
        changed_sources = copy.deepcopy(self.sources)
        changed_sources['R01-BR-FID']['publication_date'] = '2026-10-30'
        with self.assertRaisesRegex(ValueError, 'event publication date after source cutoff'):
            m.validate_review(bad, changed_sources)

    def test_study_publication_cannot_be_backdated(self):
        row = self.jupiter()
        event = next(x for x in row['events'] if x['study_original_verified'])
        event['publication_date'] = '2025-01-01'
        with self.assertRaisesRegex(ValueError, 'event publication date mismatches archived source metadata'):
            m.validate_review(row, self.sources)

    def test_study_original_from_different_project_is_rejected(self):
        row = self.jupiter()
        event = next(x for x in row['events'] if x['study_original_verified'])
        event['source_id'] = 'R01-BR-DFS'
        with self.assertRaisesRegex(ValueError, 'study event source scope transfer denied'):
            m.validate_review(row, self.sources)

    def test_documentary_gap_cannot_borrow_other_project_original(self):
        row = self.jupiter()
        self.assertTrue(row['resolved_gaps'])
        row['resolved_gaps'][0]['source_id'] = 'R01-BR-DFS'
        with self.assertRaisesRegex(ValueError, 'resolved gap source scope transfer denied'):
            m.validate_review(row, self.sources)

    def test_wim_2016_external_source_cannot_upgrade_unarchived_resource_or_product(self):
        wim_url = 'GENERALCOMPANYUPDATEMAY2016.pdf'
        avonbank = copy.deepcopy(next(g for g in self.reviews
                                     if g['review_group_id'] == 'PRJ-679f5da200a4564c'))
        bungalally = copy.deepcopy(next(g for g in self.reviews
                                       if g['review_group_id'] == 'PRJ-867a533642228a73'))
        self.assertIn(wim_url, avonbank['conflicts'])
        self.assertIn('6,000 t/y REE concentrate', avonbank['conflicts'])
        self.assertIn('May-2016', avonbank['reopen_condition'])
        self.assertIn(wim_url, bungalally['conflicts'])
        self.assertIn('207Mt', bungalally['conflicts'])
        self.assertIn('205Mt', bungalally['conflicts'])
        self.assertIn('1.4% OF THM', bungalally['conflicts'])
        self.assertIn('2015 Optiro CP MRE', bungalally['reopen_condition'])
        for group,source_id in ((avonbank,'R01-S01'), (bungalally,'R01-S05')):
            self.assertFalse(group['resources'][0]['same_scope_REO_evidence'])
            self.assertEqual(group['resources'][0]['resource_or_reserve'], 'UNVERIFIED')
            self.assertEqual(group['resources'][0]['tonnage_Mt'], '')
            self.assertEqual(group['gates']['ID']['status'], 'BLOCKED_EVIDENCE')
            self.assertEqual(group['gates']['ROLE']['status'], 'BLOCKED_EVIDENCE')
            self.assertEqual(group['gates']['JORC']['status'], 'BLOCKED_EVIDENCE')
            self.assertEqual(group['gates']['ID']['source_ids'], [source_id])
            self.assertFalse(any(e['study_original_verified'] for e in group['events']))
            m.validate_review(group, self.sources)
        self.assertFalse(any(wim_url in src['url'] for src in self.sources.values()))
        outputs, summary = m.build()
        self.assertEqual(summary['groups_bounded_reviewed'], 39)
        self.assertEqual(summary['ready_gate_evidence_cells'], 29)
        self.assertEqual(summary['remaining_gate_evidence_cells'], 166)
        self.assertEqual(summary['C1_approved'], 0)
        self.assertEqual(summary['C2_approved'], 0)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(
            outputs['gate_evidence_resolution.csv'])))), 195)

    def test_hm_and_mzeq_cannot_become_direct_reo(self):
        for basis in ('HM', 'THM', 'MZEQ', 'EXPLORATION_TARGET'):
            row = self.jupiter()
            row['resources'][0]['basis'] = basis
            with self.assertRaisesRegex(ValueError, 'cannot become REO'):
                m.validate_review(row, self.sources)

    def test_ees_scoping_not_economic_scoping(self):
        row = self.jupiter()
        event = next(e for e in row['events'] if e['study_original_verified'])
        event['event_type'] = 'EES_SCOPING'
        with self.assertRaisesRegex(ValueError, 'not economic study'):
            m.validate_review(row, self.sources)

    def test_missing_original_not_documentary_readiness(self):
        sources = copy.deepcopy(self.sources)
        sources['R01-JU-MRE']['access_status'] = 'SOURCE_UNAVAILABLE'
        with self.assertRaisesRegex(ValueError, 'original required'):
            m.validate_review(self.jupiter(), sources)

    def test_no_fabricated_signatures_or_pass_status(self):
        row = self.jupiter()
        row['researcher_signature'] = 'invented'
        with self.assertRaisesRegex(ValueError, 'cannot grant'):
            m.validate_review(row, self.sources)
        row = self.jupiter()
        row['gates']['ID']['status'] = 'PASS'
        with self.assertRaisesRegex(ValueError, 'invalid evidence status'):
            m.validate_review(row, self.sources)

    def test_readiness_not_eligibility_or_gis_release(self):
        outputs, summary = m.build()
        rows = list(csv.DictReader(io.StringIO(outputs['structural_candidates.csv'])))
        self.assertTrue(any(r['evidence_status']=='REVIEW_READY' for r in rows))
        self.assertTrue(all(r['structural_eligibility']=='NOT_FORMALLY_APPROVED' and
                            r['GIS_release_approved']==r['C1_admitted']=='False' for r in rows))
        self.assertEqual(summary['C2_approved'], 0)
        self.assertFalse(summary['MCDA_executed'])

    def test_rounding_and_chemical_denominators_preserved(self):
        by_name = {r['project_name']: r for r in self.reviews}
        dubbo = by_name['Dubbo Project']
        self.assertEqual(dubbo['gates']['JORC']['status'], 'REVIEW_PENDING')
        self.assertEqual(dubbo['resources'][0]['basis'], 'TREO_EX_Y_IN_SITU')
        gc = by_name['Goschen Central Project']
        self.assertEqual(gc['gates']['JORC']['reason'], 'SOURCE_TABLE_YEAR_CUTOFF_CONFLICT')
        jupiter = self.jupiter()
        self.assertEqual(jupiter['resources'][-1]['category'], 'ROUNDED_HEADLINE_TOTAL')

    def test_deterministic_offline_outputs(self):
        first, _ = m.build()
        second, _ = m.build()
        self.assertEqual(first, second)
        for name, content in first.items():
            self.assertEqual((m.OUT/name).read_bytes(), content.encode('utf-8'))

    def test_duplicate_and_missing_group_denied(self):
        with patch.object(m, 'read_csv', return_value=[]):
            with self.assertRaisesRegex(ValueError, '39 frozen'):
                m.build()


    def test_original_cache_contract_and_missing_bytes_fail_closed(self):
        """An evidence hash without the corresponding immutable bytes is not a verified original."""
        from scripts import acquire_structural_round01 as acquire
        item={
            'source_id':'R01-SYNTHETIC',
            'url':'https://example.gov.au/original.pdf',
            'format':'pdf',
            'publication_date':'2026-10-01',
            'review_group_ids':['PRJ-SYNTHETIC'],
        }
        raw=b'%PDF synthetic fixture bytes only'
        with tempfile.TemporaryDirectory() as temporary:
            archive=Path(temporary)/'originals'
            archive.mkdir()
            orig=archive/'R01-SYNTHETIC.bin'
            metadata=archive/'R01-SYNTHETIC.json'
            orig.write_bytes(raw)
            record={
                **item,
                'access_status':'ORIGINAL_BYTES_LOCAL',
                'sha256':hashlib.sha256(raw).hexdigest(),
                'byte_count':len(raw),
            }
            metadata.write_text(json.dumps(record),encoding='utf-8')
            with patch.object(acquire,'ARCHIVE',archive):
                self.assertEqual(acquire.fetch(item)['sha256'],record['sha256'])
                altered={**item,'url':'https://example.gov.au/revised.pdf'}
                with self.assertRaisesRegex(ValueError,'source contract changed'):
                    acquire.fetch(altered)
                orig.unlink()
                with self.assertRaisesRegex(FileNotFoundError,'archived original missing'):
                    acquire.fetch(item)
                orig.write_bytes(b'not the original data')
                with self.assertRaisesRegex(ValueError,'archived bytes/hash/size changed'):
                    acquire.fetch(item)
                metadata.unlink()
                with self.assertRaisesRegex(FileExistsError,'lacks manifest'):
                    acquire.fetch(item)

    def test_access_holds_remain_holds_without_retrieval(self):
        from scripts import acquire_structural_round01 as acquire
        item={
            'source_id':'R01-MISSING-SYNTHETIC',
            'url':'https://example.gov.au/unavailable.pdf',
            'format':'pdf',
            'publication_date':'2026-10-01',
            'review_group_ids':['PRJ-SYNTHETIC'],
        }
        with tempfile.TemporaryDirectory() as temporary:
            archive=Path(temporary)/'originals'
            archive.mkdir()
            record={**item,'access_status':'SOURCE_UNAVAILABLE','sha256':'','byte_count':0}
            (archive/'R01-MISSING-SYNTHETIC.json').write_text(json.dumps(record),encoding='utf-8')
            with patch.object(acquire,'ARCHIVE',archive):
                self.assertEqual(acquire.fetch(item)['access_status'],'SOURCE_UNAVAILABLE')


if __name__ == '__main__':
    unittest.main()
