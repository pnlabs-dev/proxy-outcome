import unittest

from proxy_outcome.cli import _headers


class CliSafetyTests(unittest.TestCase):
    def test_malformed_header_error_does_not_echo_input(self):
        sensitive = "SECRET-DO-NOT-ECHO"
        with self.assertRaises(SystemExit) as caught:
            _headers([sensitive])
        self.assertNotIn(sensitive, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
