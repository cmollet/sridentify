import os
import subprocess
import unittest


class SridentifyCLIModeTest(unittest.TestCase):

    def setUp(self):
        self.this_dir = os.path.abspath(os.path.dirname(__file__))
        self.fixtures_dir = os.path.join(self.this_dir, 'fixtures')
        self.prj_file = os.path.join(self.fixtures_dir, 'street_center_lines.prj')
        self.fake_prj = os.path.join(self.fixtures_dir, 'not_a_real.prj')

    def test_cli_mode_against_valid_prj_returns_expected_espg(self):
        result = subprocess.run(
            ['sridentify', self.prj_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.decode('utf-8').strip(), '3435')

    def test_cli_mode_exits_with_error_message_if_prj_file_does_not_exist(self):
        result = subprocess.run(
            ['sridentify', 'foo.prj'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.decode('utf-8').strip(),
            "ERROR - No such file: 'foo.prj'"
        )

    def test_no_remote_api_call_option_does_not_call_api(self):
        result = subprocess.run(
            ['sridentify', '-n', self.fake_prj],
            stdout=subprocess.PIPE
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.decode('utf-8').strip(), '')

if __name__ == '__main__':
    unittest.main()
