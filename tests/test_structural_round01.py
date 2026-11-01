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
        self.assertEqual(summary['C1_approved'], 0)
        self.assertEqual(summary['C2_approved'], 0)
        self.assertEqual(summary['dated_economic_study_original_projects'], 8)

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
        with self.assertRaisesRegex(ValueError, 'study event publication date mismatches original'):
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
