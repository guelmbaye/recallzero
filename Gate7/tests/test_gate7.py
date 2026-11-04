import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import gate7 as g

class Gate7Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.patch = patch.object(g, 'ROOT', self.root)
        self.patch.start()
        g.cmd_init(type('Args', (), {'force': False})())

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def fixture_complete(self):
        for w in g.WORLDS:
            img = self.root / 'evidence' / (w + '.jpg')
            img.parent.mkdir(exist_ok=True)
            img.write_bytes(('SYNTHETIC TEST ONLY ' + w).encode())
            world = g.read(g.evidence_path(w))
            world.update(photos=[{'path': 'evidence/' + w + '.jpg', 'source_page': 'test://synthetic-' + w, 'sha256': g.digest(img.read_bytes())}],
                         evidence_inspected_by_operator=True,
                         unit_linkage_basis='SYNTHETIC_TEST_FIXTURE',
                         independent_case_provenance='SYNTHETIC_TEST_FIXTURE',
                         observed_marks={'side_capacity_ah': 6 if w in 'BF' else None, 'base_model_code': 'RB18L40' if w in 'BF' else ''})
            g.write(g.evidence_path(w), world)
        truth = g.read(g.truth_path())
        truth.update(status='INSPECTED_PRE_MODEL', inspector='TEST_OPERATOR')
        g.write(g.truth_path(), truth)

    def test_unready_seal_blocks(self):
        truth = g.read(g.truth_path())
        truth.update(status='INSPECTED_PRE_MODEL', inspector='TEST_OPERATOR')
        g.write(g.truth_path(), truth)
        self.assertEqual(g.cmd_seal(None), 2)

    def test_truth_tamper_blocks(self):
        self.fixture_complete()
        self.assertEqual(g.cmd_seal(None), 0)
        truth = g.read(g.truth_path())
        truth['world_actions']['A'] = 'ALLOW'
        g.write(g.truth_path(), truth)
        with self.assertRaisesRegex(ValueError, 'TRUTH_CHANGED'):
            g.verify_seal()

    def test_image_tamper_blocks(self):
        self.fixture_complete()
        g.cmd_seal(None)
        (self.root / 'evidence' / 'B.jpg').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'EVIDENCE_CHANGED'):
            g.verify_seal()

    def test_blind_export_no_truth(self):
        self.fixture_complete()
        g.cmd_seal(None)
        g.cmd_export(None)
        payload = g.read(self.root / 'reports' / 'payloads' / 'B.json')
        self.assertNotIn('expected', payload)
        self.assertNotIn('case_type', payload)
        self.assertNotIn('observed_marks', payload)
        self.assertNotIn('expected_action', payload)

    def test_baseline_not_claimed_ocr(self):
        self.fixture_complete()
        g.cmd_seal(None)
        g.cmd_baseline(None)
        output = g.read(self.root / 'baselines' / 'transcription_rules.json')
        self.assertEqual(output['B']['action'], 'HOLD_FOR_REVIEW')
        self.assertEqual(output['A']['action'], 'REQUEST_MORE_EVIDENCE')
        self.assertIn('NOT_OCR', output['B']['type'])

    def test_unverified_results_incomplete(self):
        self.fixture_complete()
        g.cmd_seal(None)
        g.cmd_baseline(None)
        g.cmd_evaluate(None)
        report = g.read(self.root / 'reports' / 'gate7_results.json')
        self.assertEqual(report['status'], 'INCOMPLETE_NOT_A_BENCHMARK')
        self.assertFalse(report['meta_superiority_proven'])

if __name__ == '__main__':
    unittest.main()
