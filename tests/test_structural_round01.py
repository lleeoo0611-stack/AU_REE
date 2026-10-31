"""Scientific evidence boundaries and reproducibility, not inferred approvals."""
import copy
import csv
import io
import json
import unittest
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


if __name__ == '__main__':
    unittest.main()
