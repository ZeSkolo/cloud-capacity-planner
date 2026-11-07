import unittest
from core import run, erlang

class Tests(unittest.TestCase):

    def test_mm1(self):
        r = erlang(1, 2, 1)
        self.assertAlmostEqual(r['mean_response_seconds'], 1.0)

    def test_unstable(self):
        with self.assertRaises(ValueError):
            erlang(2, 1, 1)

    def test_slo(self):
        self.assertLessEqual(run({})['recommended']['wait_breach_probability'], 0.05)

    def test_repeat(self):
        self.assertEqual(run({'simulation_jobs': 100}), run({'simulation_jobs': 100}))

    def test_bad_rate(self):
        with self.assertRaises(ValueError):
            run({'arrival_per_second': 0})
